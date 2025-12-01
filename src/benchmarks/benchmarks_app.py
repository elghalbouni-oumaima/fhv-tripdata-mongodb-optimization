"""
Automatic Slow Query Detection & Index Benchmarking
---------------------------------------------------

Ce script :
1. Exécute 10 requêtes candidates
2. Mesure l'explain() BEFORE index
3. Sauvegarde les temps d'exécution (execution_time.json)
4. Si une requête est lente → crée un index adapté
5. Mesure l'explain() AFTER index
6. Sauvegarde metrics avant/après dans JSON
7. Optimisé pour collections volumineuses

Auteur : Optimisé par ChatGPT
"""

from src.mongo_import import connect_to_mongo
import json
from datetime import datetime
import os
from src.logger import logger

# -------------------------------------------------------------------
# CONFIG
# -------------------------------------------------------------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
RESULTS_DIR = os.path.abspath(os.path.join(BASE_DIR, "../..", "results", "benchmarking"))

DB_NAME = "trips_db"
COLLECTION_NAME = "fhvhv_trips_2021-10"

db = connect_to_mongo(DB_NAME)
collection = db[COLLECTION_NAME]


# -------------------------------------------------------------------
# 1 — LISTE DES REQUÊTES DE TEST
# -------------------------------------------------------------------
SLOW_QUERY_CANDIDATES = [
    {"name": "q1_triptime_gte_300", "query": {"trip_time": {"$gte": 300}}, "index": {"trip_time": 1}},
    {"name": "q2_PULocation_100", "query": {"PULocationID": 100}, "index": {"PULocationID": "hashed"}},
    {"name": "q3_license_PU",
     "query": {"hvfhs_license_num": "HV0003", "PULocationID": 97},
     "index": {"hvfhs_license_num": 1, "PULocationID": 1}},
    {"name": "q4_miles_range",
     "query": {"trip_miles": {"$gte": 5, "$lte": 10}},
     "index": {"trip_miles": 1}},
    {"name": "q5_miles_time",
     "query": {"trip_miles": {"$gte": 5}, "trip_time": {"$gte": 1200}},
     "index": {"trip_miles": 1, "trip_time": -1}},
    {"name": "q6_base_B02764",
     "query": {"dispatching_base_num": "B02764"},
     "index": {"dispatching_base_num": 1}},
    {"name": "q7_fare_gte_20",
     "query": {"base_passenger_fare": {"$gte": 20}},
     "index": {"base_passenger_fare": 1}},
    {"name": "q8_license_miles_time",
     "query": {"hvfhs_license_num": "HV0003", "trip_miles": {"$gte": 10}, "trip_time": {"$gte": 1800}},
     "index": {"hvfhs_license_num": 1, "trip_miles": 1, "trip_time": -1}},
    {"name": "q9_DOLocation_85", "query": {"DOLocationID": 85}, "index": {"DOLocationID": 1}},
    {"name": "q10_license_exact", "query": {"hvfhs_license_num": "HV0005"}, "index": {"hvfhs_license_num": 1}},
]


# -------------------------------------------------------------------
# 2 — Détection automatique du type d'index
# -------------------------------------------------------------------
def detect_index_type(index_param):
    """
    Détecte le type d’index :
    - simple index
    - hashed index
    - compound index
    """
    items = list(index_param.items())

    if len(items) == 1 and items[0][1] == "hashed":
        return "hashed index"

    if len(items) == 1:
        return "simple index"

    return "compound index"


# -------------------------------------------------------------------
# 3 — EXPLAIN OPTIMISÉ
# -------------------------------------------------------------------
def run_explain(query, coll=collection):
    """
    Explain optimisé :
    - limit(10000) pour éviter les scans complets
    - .explain() sans paramètre (compatibilité pyMongo)
    """
    cursor = coll.find(query).limit(10000)
    explain_data = cursor.explain()

    stats = explain_data.get("executionStats", {})
    planner = explain_data.get("queryPlanner", {})

    return {
        "executionTimeMillis": stats.get("executionTimeMillis"),
        "totalDocsExamined": stats.get("totalDocsExamined"),
        "totalKeysExamined": stats.get("totalKeysExamined"),
        "nReturned": stats.get("nReturned"),
        "executionStages": stats.get("executionStages"),
        "indexName": (
            planner.get("winningPlan", {})
                   .get("inputStage", {})
                   .get("indexName")
        )
    }


# -------------------------------------------------------------------
# 4 — Save BEFORE execution time for ALL queries
# -------------------------------------------------------------------
def save_execution_times():
    """
    Sauvegarde les temps BEFORE index
    dans execution_time.json
    """
    os.makedirs(RESULTS_DIR, exist_ok=True)
    results = []

    logger.info("⏳ Collecting execution times BEFORE indexing...")

    for q in SLOW_QUERY_CANDIDATES:
        name = q["name"]
        query = q["query"]
        index_param = q["index"]
        index_type = detect_index_type(index_param)

        explain_res = run_explain(query)
        exec_time = explain_res["executionTimeMillis"]

        results.append({
            "query_name": name,
            "query": query,
            "executionTimeMillis": exec_time,
            "index_type": index_type
        })

        logger.info(f"→ {name}: {exec_time} ms ({index_type})")

    # SAVE FILE
    path = os.path.join(RESULTS_DIR, "execution_time.json")
    with open(path, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=4)

    logger.info(f"✔ execution_time.json saved → {path}")


# -------------------------------------------------------------------
# 5 — SAVE METRICS BEFORE/AFTER INDEX
# -------------------------------------------------------------------
def save_metrics(name, before, after, index_param):
    """
    Sauvegarde les metrics BEFORE/AFTER dans JSON
    """
    os.makedirs(RESULTS_DIR, exist_ok=True)

    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    filename = f"{name}_{timestamp}.json"
    path = os.path.join(RESULTS_DIR, filename)

    data = {
        "query_name": name,
        "index_param": index_param,
        "index_type": detect_index_type(index_param),
        "results": {
            "before": before,
            "after": after
        }
    }

    with open(path, "w") as f:
        json.dump(data, f, indent=4)

    logger.info(f"✔ Saved benchmark → {path}")


# -------------------------------------------------------------------
# 6 — DROP INDEXES intelligently
# -------------------------------------------------------------------
def drop_conflicting_indexes(index_param):
    """
    Supprime uniquement les index ayant EXACTEMENT
    les mêmes champs que l’index proposé.
    """
    info = collection.index_information()

    for index_name, meta in info.items():
        if index_name == "_id_":
            continue

        fields = {field: v for field, v in meta["key"]}

        if set(fields.keys()) == set(index_param.keys()):
            logger.warning(f"Dropping old index: {index_name}")
            collection.drop_index(index_name)


# -------------------------------------------------------------------
# 7 — MAIN: Slow Query Detection
# -------------------------------------------------------------------
def run_slow_query_detection(threshold_ms=200):
    logger.info("🚀 Starting slow query detection...")

    # Step 1 — Save ALL BEFORE execution times
    save_execution_times()

    # Step 2 — Process each query
    for q in SLOW_QUERY_CANDIDATES:
        name = q["name"]
        query = q["query"]
        index_param = q["index"]

        logger.info(f"\n=== TEST {name} ===")

        before = run_explain(query)
        time_before = before["executionTimeMillis"]

        logger.info(f"⏱ BEFORE = {time_before} ms")

        if time_before <= threshold_ms:
            logger.info(f"→ Query {name} is FAST (<{threshold_ms} ms). Skipped.")
            continue

        logger.warning(f"⚠ SLOW QUERY → Creating index {index_param}")

        drop_conflicting_indexes(index_param)
        collection.create_index(index_param)

        after = run_explain(query)

        logger.info(f"⏱ AFTER = {after['executionTimeMillis']} ms")

        # Save BEFORE/AFTER comparison
        save_metrics(name, before, after, index_param)

    logger.info("🏁 Slow query detection finished.")


# -------------------------------------------------------------------
# 8 — RUN SCRIPT
# -------------------------------------------------------------------
if __name__ == "__main__":
    logger.info("===== STARTING BENCHMARK ENGINE =====")
    run_slow_query_detection(threshold_ms=200)
    logger.info("===== FINISHED =====")
