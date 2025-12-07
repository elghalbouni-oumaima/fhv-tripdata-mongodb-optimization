# README.md

# Uber For-Hire Vehicle Trip Data Optimization with MongoDB

This project focuses on optimizing analytical queries on the NYC For-Hire Vehicle (FHV) trip dataset using MongoDB.
The goal is to demonstrate how indexing, sharding, and query optimization techniques improve performance on large-scale datasets.

The dataset contains approximately 16 million rows and includes fields such as pickup and dropoff locations, timestamps, provider information, trip distance, trip duration, fares, and surcharges.

---

## 1. Project Objectives

1. Import and preprocess a large dataset (millions of rows).
2. Design an efficient MongoDB collection structure.
3. Benchmark slow queries on an unindexed collection.
4. Apply indexing techniques (simple, compound, hashed).
5. Measure and compare query performance before and after indexing.
6. Implement sharding and evaluate distributed query performance.
7. Visualize benchmark results using a Dash dashboard.
8. Provide reproducible and modular code following clean project architecture.

---

## 2. Dataset

**Source:** NYC TLC For-Hire Vehicle Trip Records (2021)
**Format:** Parquet
**Size:** Approximately 16 million rows
**Columns:**

* Pickup and dropoff timestamps
* Pickup and dropoff location IDs
* Trip distance and duration
* Provider license (HV0003, HV0005, etc.)
* Base fare, tolls, surcharges
* Several service flags

---

## 3. Project Architecture

```
project/
│
├── data/
│   ├── raw/          # Original Parquet files
│   ├── processed/    # Cleaned and transformed JSON/NDJSON files
│
├── src/
│   ├── clean_data.py          # Preprocessing and data cleaning
│   ├── mongo_import.py      # Batch import into MongoDB
│   ├── benchmark.py         # Query benchmarking and explain analysis
│   └── logger.py            # Centralized logging
│
├── dashboard/
│   ├── app.py               # Dash application for visualizing results
│   └── assets/              # Layout and CSS
│
│
├── README.md
├── requirements.txt
└── .env                     # MongoDB credentials and file paths
```

---

## 4. Data Preprocessing Pipeline

The preprocessing script performs the following tasks:

1. Load Parquet data in memory-safe batches.
2. Cast datetime columns to standard ISO datetime.
3. Convert numeric fields to consistent float or integer types.
4. Normalize string fields by stripping whitespace and enforcing uppercase.
5. Encode service flags (Y/N to 1/0).
6. Remove unnecessary columns.
7. Add a unique row identifier.
8. Export cleaned data as JSON or NDJSON for fast import.

---

## 5. MongoDB Import

Data is imported using batches to avoid memory overhead:

* Configurable batch size
* Error handling and logging
* Optional index creation before or after import

Import script uses PyMongo to insert NDJSON records efficiently.

---

## 6. Query Benchmarking

Each query is executed using `explain("executionStats")` to collect:

* executionTimeMillis
* totalDocsExamined
* totalKeysExamined
* winningPlan details
* scan type (COLLSCAN or IXSCAN)

Queries tested include:

1. Range queries on trip duration
2. Equality filters on pickup locations
3. Provider and location combined filters
4. Range queries on trip distance
5. Compound filters involving miles and time
6. Lookup by provider license
7. Fare-based filtering

Results are written to JSON files in the `benchmark_results/` directory.

---

## 7. Indexing Strategy

Tested index types:

1. Simple index (single field)
2. Compound index (two or more fields)
3. Hashed index (for equality queries)

Example indexes:

```
{ trip_time: 1 }
{ PULocationID: "hashed" }
{ hvfhs_license_num: 1, PULocationID: 1 }
```

A comparison is performed before and after adding indexes.

---

## 8. Sharding

Sharding is applied to improve distribution and scalability in large workloads.

Shard key selected:

```
{ PULocationID: 1, hvfhs_license_num: 1 }
```

Rationale:

* High cardinality
* Even distribution
* Matches several benchmark queries
* Avoids insert hotspots
* Reduces scatter-gather operations

Performance after sharding is compared against the unsharded cluster.

---

## 9. Dash Dashboard

A Dash application is included to visualize:

* Execution time before and after indexing
* Number of documents examined
* Performance impact of different index types
* Sharding improvements
* Query-by-query comparison

Dashboard components:

* Tables
* Bar charts
* Line charts
* Filters for query category and index type

---

## 10. Requirements

Install dependencies:

```
pip install -r requirements.txt
```

Requirements include:

* pandas
* pyarrow
* pymongo
* dash
* python-dotenv

MongoDB must be installed locally or accessible via connection string.

Dataset source*: “Uber NYC For-Hire Vehicles Trip Data (2021)” — https://www.kaggle.com/datasets/shuhengmo/uber-nyc-forhire-vehicles-trip-data-2021
File used: fhvhv_tripdata_2021-10.parquet

---

## 11. How to Run

1. Preprocess dataset:

```
python src/pipeline.py
```

2. Import processed data:

```
python src/mongo_import.py
```

3. Run benchmarks:

```
python src/benchmarks/benchmarks_app.py
```

4. Start Dash dashboard:

```
python dashboard/app.py
```

---

## 12. Conclusion

This project demonstrates practical data engineering and database optimization techniques using MongoDB.
It shows how indexing, batching, preprocessing, and sharding significantly improve query performance on large-scale datasets.

