from mongo_import import connect_to_mongo
import json
from datetime import datetime
import os
from logger import logger

RESULTS_DIR = "benchmarks/json_files"

DB_NAME = "trips_db"
COLLECTION_NAME = "fhvhv_trips_2021-10"
db = connect_to_mongo(DB_NAME)
collection = db[COLLECTION_NAME]

def run_explain(query):
    pass

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

def run_benchmark(query, index_param,json_file, index_name):
    #Before Index
    metrics_before = run_explain(query)
    filename = save_metrics( metrics_before, index_param, index_name, filename=None)

    #After Index
    create_index(index_param)
    metrics_after = run_explain(query)
    save_metrics( metrics_after, index_param, index_name , filename=filename)

    