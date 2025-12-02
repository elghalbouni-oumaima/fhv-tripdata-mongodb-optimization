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
    # --- INDEX SIMPLE (Single Field) ---
    {
        "name": "q1_simple_outlier",
        # Optimisation : Réduit le scan de 100% de la base à < 1%.
        "query": {"trip_time": {"$gte": 4000}}, 
        "index": {"trip_time": 1}
    },
    {
        "name": "q2_simple_sort",
        # Optimisation : Évite le tri en mémoire (Blocking Sort).
        "query": {"trip_miles": {"$gte": 10}},
        "sort": {"trip_miles": -1},
        "index": {"trip_miles": 1}
    },
    {
        "name": "q3_simple_lookup",
        # Optimisation : Accès direct à une valeur rare.
        "query": {"dispatching_base_num": "B02800"}, 
        "index": {"dispatching_base_num": 1}
    },

    # --- INDEX HASHED (Haché) ---
    {
        "name": "q4_hashed_license",
        # Optimisation : Distribution uniforme, parfait pour l'égalité exacte.
        "query": {"hvfhs_license_num": "HV0003"},
        "index": {"hvfhs_license_num": "hashed"}
    },
    {
        "name": "q5_hashed_puloc",
        # Optimisation : Recherche pointue très rapide.
        "query": {"PULocationID": 132},
        "index": {"PULocationID": "hashed"}
    },

    # --- INDEX COMPOUND (Composé) ---
    {
        "name": "q6_compound_esr_sort",
        # Optimisation ESR (Equality -> Sort -> Range).
        # Permet de trier sans calcul CPU.
        "query": {"PULocationID": 79, "trip_miles": {"$gte": 5}},
        "sort": {"trip_time": 1},
        "index": {"PULocationID": 1, "trip_time": 1, "trip_miles": 1}
    },
    {
        "name": "q7_compound_covered",
        # *** COVERED QUERY *** : Le plus rapide possible.
        # DocsExamined sera 0 car tout est dans l'index.
        "query": {"hvfhs_license_num": "HV0005", "trip_miles": {"$gte": 2}},
        "projection": {"hvfhs_license_num": 1, "trip_miles": 1, "_id": 0},
        "index": {"hvfhs_license_num": 1, "trip_miles": 1}
    },
    {
        "name": "q8_compound_multi_filter",
        # Filtre sur deux champs pour réduire drastiquement les résultats.
        "query": {"shared_request_flag": 1, "PULocationID": 230},
        "index": {"PULocationID": 1, "shared_request_flag": 1}
    },
    {
        "name": "q9_compound_date_sort",
        # Tri temporel optimisé.
        "query": {"request_datetime": {"$gte": "2019-01-15"}},
        "sort": {"request_datetime": 1},
        "index": {"request_datetime": 1}
    },

    # --- VOTRE REQUÊTE SPÉCIFIQUE (Modifiée pour le format) ---
    {
        "name": "q10_complex_user_request",
        # Analyse : C'est une requête lourde.
        # Avant index : Scan complet + Tri mémoire (très lent).
        # Après index : Filtre efficace sur Base et Miles.
        "query": {
            "dispatching_base_num": "B02764",
            "trip_miles": { "$gte": 5, "$lte": 15 },
            "trip_time": { "$gte": 2000 }
        },
        "sort": { "trip_time": -1 },
        "index": {
            "dispatching_base_num": 1,
            "trip_miles": 1,
            "trip_time": 1
        }
    }
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
    cursor = coll.find(query)
    explain_data = cursor.explain()

    stats = explain_data.get("executionStats", {})
    planner = explain_data.get("queryPlanner", {})

    return {
        "executionTimeMillis": stats.get("executionTimeMillis"),
        "optimizationTimeMillis": planner.get("optimizationTimeMillis"),
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
    Supprime TOUS les index qui pourraient interférer avec le benchmark.
    
    Si on veut tester un index composé {A:1, B:1}, on doit supprimer
    non seulement les index commençant par A, mais aussi ceux commençant par B,
    car MongoDB pourrait les utiliser pour optimiser partiellement la requête.
    """
    try:
        info = collection.index_information()
        
        # On récupère TOUS les champs du futur index (ex: ['PULocationID', 'trip_time'])
        target_fields = list(index_param.keys())

        for index_name, meta in info.items():
            if index_name == "_id_":
                continue

            existing_keys = meta["key"] 
            existing_root = existing_keys[0][0] # Le premier champ de l'index existant

            # Si l'index existant commence par N'IMPORTE QUEL champ de notre futur index,
            # on le supprime. C'est la seule façon de garantir un COLLSCAN pur.
            if existing_root in target_fields:
                logger.warning(f"🧹 Dropping interfering index '{index_name}' (starts with '{existing_root}')...")
                collection.drop_index(index_name)

    except Exception as e:
        logger.error(f"Error checking indexes: {e}")
        
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

        # 1. D'ABORD on nettoie
        drop_conflicting_indexes(index_param) 

        # 2. ENSUITE on mesure (on est sûr que c'est lent maintenant)
        before = run_explain(query)
        time_before = before["executionTimeMillis"]

        logger.info(f"⏱ BEFORE = {time_before} ms")

        if time_before <= threshold_ms:
            logger.info(f"→ Query {name} is FAST (<{threshold_ms} ms). Skipped.")
            continue

        logger.warning(f"⚠ SLOW QUERY → Creating index {index_param}")

        collection.create_index(list(index_param.items()))

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
