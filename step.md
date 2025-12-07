
# Project Playbook: Distributed NYC Taxi Analytics

## Project Context

### Goal

Deploy a **sharded MongoDB infrastructure** capable of ingesting and analyzing **16M+ NYC For-Hire Vehicle trip records** with high throughput and low latency.

### Key Requirements Addressed

  * **Availability:** Replica Sets for all data nodes.
  * **Scalability:** 3 distinct shards to handle write loads.
  * **Performance:**
      * **Compound Sharding Key:** `PULocationID` (High Cardinality) + `hvfhs_license_num`.
      * **Pre-splitting:** Manually creating chunks to prevent "hot spotting" during the massive import.

-----

# Phase 1: Infrastructure Initialization

Before creating the database, we must launch the physical nodes and link them together.

-----

## **Step 1: Start the Containerized Cluster**

Run:

```bash
docker-compose up -d
```

### What this does

Starts the complete cluster stack:

  * **Config Server:** `configsvr`
  * **Shards:** `shard1`, `shard2`, `shard3`
  * **Router:** `mongos`
  * **Observability:** Prometheus, Grafana, Exporter

-----

## **Step 2: Initialize the Config Server**

```bash
docker exec -it fhv-tripdata-mongodb-optimization-configsvr-1 mongosh
```

Inside `mongosh`:

```js
rs.initiate({
  _id: "configReplSet",
  configsvr: true,
  members: [{ _id: 0, host: "configsvr:27017" }]
})
```

### Explanation

The **Config Server** acts as the "brain" of the cluster, storing metadata map of which chunk lives on which shard.

exit
-----

## **Step 3: Initialize Data Shards**

Convert each storage container into a Replica Set.

### **Shard 1**

```bash
docker exec -it fhv-tripdata-mongodb-optimization-shard1-1 mongosh
```

```js
rs.initiate({
  _id: "shard1ReplSet",
  members: [{ _id: 0, host: "shard1:27017" }]
})
```
exit

### **Shard 2**

```bash
docker exec -it fhv-tripdata-mongodb-optimization-shard2-1 mongosh
```

```js
rs.initiate({
  _id: "shard2ReplSet",
  members: [{ _id: 0, host: "shard2:27017" }]
})
```
exit
### **Shard 3**

```bash
docker exec -it fhv-tripdata-mongodb-optimization-shard3-1 mongosh
```

```js
rs.initiate({
  _id: "shard3ReplSet",
  members: [{ _id: 0, host: "shard3:27017" }]
})
```
exit
-----

## **Step 4: Connect Shards to the Router (mongos)**

```bash
docker exec -it fhv-tripdata-mongodb-optimization-mongos-1 mongosh
```

Inside `mongos`:

```js
sh.addShard("shard1ReplSet/shard1:27017")
sh.addShard("shard2ReplSet/shard2:27017")
sh.addShard("shard3ReplSet/shard3:27017")
```

### What this does

The router (`mongos`) now formally recognizes the 3 storage shards.

-----

# Phase 2: Schema Design & Sharding Strategy

All commands from this point forward run inside the **mongos shell**.

-----

## **Step 5: Stop the Balancer (Optimization Prep)**

```js
sh.stopBalancer()
```

### Why?

We are about to import 16GB+ of data. We do not want MongoDB wasting resources trying to move data around *while* we are writing it.

-----

## **Step 6: Database & Index Setup**

```js
use trips_db

// Enable sharding at the database level
sh.enableSharding("trips_db")

// Strategic Indexes
db["fhvhv_trips_2021-10"].createIndex({ PULocationID: 1, hvfhs_license_num: 1 })
db["fhvhv_trips_2021-10"].createIndex({ DOLocationID: 1 })
db["fhvhv_trips_2021-10"].createIndex({ trip_miles: 1, trip_time: 1 })
db["fhvhv_trips_2021-10"].createIndex({ request_datetime: 1, pickup_datetime: 1 })
```

-----

## **Step 7: Apply Sharding Key**

```js
sh.shardCollection("trips_db.fhvhv_trips_2021-10", { PULocationID: 1, hvfhs_license_num: 1 })
```

### Why this sharding strategy?

  * **PULocationID (Pickup Location):** Has \~263 unique zones (Manhattan, Queens, etc.). Excellent for distribution.
  * **hvfhs\_license\_num:** Adds uniqueness to the key.

-----

# Phase 3: Pre-Splitting (Advanced Optimization)

If we import now, all data goes to Shard 1 (the default). We will manually define the chunk boundaries based on NYC Zones (1 to 263).

-----

## **Step 8: Create Logical Splits**

```js
use admin
// Create splits for every Pickup Location ID (1 to 263)
for (var i = 1; i <= 263; i++) {
    db.adminCommand({
        split: "trips_db.fhvhv_trips_2021-10",
        middle: { PULocationID: i, hvfhs_license_num: MinKey }
    });
}
```

### What this does

This pre-allocates empty "buckets" for every single neighborhood in New York City.

-----

## **Step 9: Distribute Chunks (Round Robin)**

```js
var shards = ["shard1ReplSet", "shard2ReplSet", "shard3ReplSet"];

// Move chunks in a round-robin fashion
for (var i = 1; i <= 263; i++) {
    var splitKey = { PULocationID: i, hvfhs_license_num: MinKey };
    var targetShard = shards[i % shards.length];
    
    db.adminCommand({
        moveChunk: "trips_db.fhvhv_trips_2021-10",
        find: splitKey,
        to: targetShard
    });
}
```

### Expected Distribution

  * **Shard 1:** Zones 1, 4, 7...
  * **Shard 2:** Zones 2, 5, 8...
  * **Shard 3:** Zones 3, 6, 9...

This ensures that as we import, **all 3 shards write simultaneously**.

-----

# Phase 4: Data Injection

### PowerShell Import Loop

Since the dataset is split into 8 parts (`trips_0.json` to `trips_7.json`), run this in your host terminal:

```powershell
for ($i = 0; $i -le 7; $i++) {
    Write-Host "Importing File part $i..."
    
    # 1. Copy JSON into the container
    docker cp data/processed/trips_$i.json fhv-tripdata-mongodb-optimization-mongos-1:/trips.json

    # 2. Execute Mongoimport
    docker exec fhv-tripdata-mongodb-optimization-mongos-1 mongoimport `
        --host localhost `
        --port 27017 `
        --db trips_db `
        --collection fhvhv_trips_2021-10 `
        --file /trips.json `
}
```

-----

# Phase 5: Verification & Maintenance

## **Step 10: Verify Distribution**

```js
use trips_db
db["fhvhv_trips_2021-10"].getShardDistribution()
```

Expected output:

  * Roughly **33%** data size on Shard 1
  * Roughly **33%** data size on Shard 2
  * Roughly **33%** data size on Shard 3

## **Step 11: Restart the Balancer**

```js
sh.startBalancer()
```

-----

# Phase 6: Monitoring & Analytics

## **1. Grafana Dashboard**

**Access:** [http://localhost:3000](https://www.google.com/search?q=http://localhost:3000)

  * **User:** `admin`
  * **Pass:** `password123`
  * **Visualizes:** Ops/sec, Shard Latency, CPU Usage.

## **2. Sample Analytical Queries**

**Count trips by dispatch base for a specific dropoff zone:**

```js
db.fhvhv_trips_2021-10.aggregate([
  { $match: { DOLocationID: 85 } },
  { $group: { _id: "$dispatching_base_num", total_trips: { $sum: 1 } } }
])
```

**Analyze query performance:**

```js
db.fhvhv_trips_2021-10.find({ PULocationID: 68 }).explain("executionStats")
```

#  temporary drop index on the shard key

```js
db["fhvhv_trips_2021-10"].dropIndex("PULocationID_1_hvfhs_license_num_1")
db["fhvhv_trips_2021-10"].dropIndex("DOLocationID_1")
db["fhvhv_trips_2021-10"].dropIndex("trip_miles_1_trip_time_1")
db["fhvhv_trips_2021-10"].dropIndex("request_datetime_1_pickup_datetime_1")
```