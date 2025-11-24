from src.mongo_import import connect_to_mongo
import json
from datetime import datetime
import os
from src.logger import logger

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
RESULTS_DIR = os.path.join(BASE_DIR, "json_files")

DB_NAME = "trips_db"
COLLECTION_NAME = "fhvhv_trips_2021-10"
db = connect_to_mongo(DB_NAME)
collection = db[COLLECTION_NAME]


def  run_explain(query, coll=collection ,sort=None, typeOfQuery = "find"):
    #Build the query
    
    if typeOfQuery == "find":
        cursor = coll.find(query)
    elif typeOfQuery == "aggregate":
        cursor = coll.aggregate(query)
    else:
        raise ValueError(f"Unsupported query type: {typeOfQuery}")

    #Add sorting if provided
    if sort is not None:
        cursor = cursor.sort(sort)

    #lauch explain with execution statistics
    explain_data = cursor.explain()

    planner = explain_data.get("queryPlanner", {})
    winning_plan = planner.get("winningPlan", {})
    stats = explain_data.get("executionStats", {})

    def parse_stage(stage):
       #detailed dictionary of each stage
        result = stage.copy()
        if "inputStage" in stage:
            # Appel récursif pour traiter le stage interne
            result["inputStage"] = parse_stage(stage["inputStage"])
        # If several nested stages
        if "inputStages" in stage:
            result["inputStages"] = [parse_stage(s) for s in stage["inputStages"]]
        return result
    
    execution_stages = parse_stage(stats.get("executionStages", {}))

    # Secure extraction of certain metrics from the main stage
    index_name = None
    index_bounds = None
    def extract_index_info(stage):
        nonlocal index_name, index_bounds
        if stage.get("stage") == "IXSCAN":
            index_name = stage.get("indexName")
            index_bounds = stage.get("indexBounds")
        # Check the sub-internships
        if "inputStage" in stage:
            extract_index_info(stage["inputStage"])
        if "inputStages" in stage:
            for s in stage["inputStages"]:
                extract_index_info(s)

    extract_index_info(execution_stages)  
    # Final report with all the important metrics
    return {
        "namespace": planner.get("namespace"),
        "parsedQuery": planner.get("parsedQuery"),
        "optimizationTimeMillis": planner.get("optimizationTimeMillis"),
        "rejectedPlans": planner.get("rejectedPlans", []),
        "executionSuccess": stats.get("executionSuccess"),
        "nReturned": stats.get("nReturned"),
        "executionTimeMillis": stats.get("executionTimeMillis"),
        "totalDocsExamined": stats.get("totalDocsExamined"),
        "totalKeysExamined": stats.get("totalKeysExamined"),
        "executionStages": execution_stages,
        "indexName": index_name,
        "indexBounds": index_bounds,
        "memoryUsageBytesEstimate": stats.get("executionStages", {}).get("maxMemoryUsageBytes"),
        "sortPattern": explain_data.get("sortPattern")
    }

def save_metrics(metrics, index_param, index_name, filename=None):

    #Ensure results folder exists
    os.makedirs(RESULTS_DIR, exist_ok=True)

    #If no file provided then create a new file
    if filename is None:
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        filename = f"{index_name}_{timestamp}.json"
        filepath = os.path.join(RESULTS_DIR, filename)
        logger.info(f"Creating new benchmark file: {filepath}")

        content = {
            "index_name": index_name,
            "index_param": index_param,
            "results": {
                "before": metrics,
                "after": None
            }
        }

    else:
        # append AFTER metrics
        filepath = os.path.join(RESULTS_DIR, filename)

        if os.path.exists(filepath):
            with open(filepath, "r") as f:
                content = json.load(f)
            logger.info(f"Appending AFTER metrics to existing file: {filepath}")

            content["results"]["after"] = metrics

        else:
            # File missing then recreate structure
            logger.warning(f"Expected file not found. Recreating: {filepath}")
            content = {
                "index_name": index_name,
                "index_param": index_param,
                "results": {
                    "before": metrics,
                    "after": None
                }
            }

    # Save JSON back
    with open(filepath, "w") as f:
        json.dump(content, f, indent=4)

    logger.info(f"Metrics saved → {filepath}")

    return filename

def create_index(index_param):
    collection.create_index(index_param)

def run_benchmark(query, index_param, index_name):
    #Before Index
    metrics_before = run_explain(query)
    filename = save_metrics( metrics_before, index_param, index_name, filename=None)

    #After Index
    create_index(index_param)
    metrics_after = run_explain(query)
    save_metrics( metrics_after, index_param, index_name , filename=filename)

if __name__ == "__main__":
    logger.info("===== Starting manual benchmark tests =====")


    # # SIMPLE INDEX TEST
    # logger.info("Running SIMPLE INDEX benchmark...")
    # run_benchmark(
    #     query={},
    #     index_param={},
    #     index_name="simple_index"
    # )


    # # COMPOUND INDEX TEST
    # logger.info("Running COMPOUND INDEX benchmark...")
    # run_benchmark(
    #     query={},
    #     index_param={},
    #     index_name="compound_index"
    # )


    # HASHED INDEX TEST
    logger.info("Running HASHED INDEX benchmark...")
    run_benchmark(
        query={"PULocationID": 100},
        index_param={"PULocationID": "hashed"},
        index_name="hashed_index"
    )

    logger.info("===== All benchmarks completed successfully =====")
