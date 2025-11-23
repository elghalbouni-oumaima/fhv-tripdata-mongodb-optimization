from mongo_import import connect_to_mongo

DB_NAME = "trips_db"
COLLECTION_NAME = "fhvhv_trips_2021-10"
db = connect_to_mongo(DB_NAME)
collection = db[COLLECTION_NAME]

def run_explain(query):
    pass

def save_metrics(metrics,json_file):
    pass

def create_index(index_param):
    collection.create_index(index_param)

def run_benchmark(query, index_param,json_file):
    #Before Index
    metrics = run_explain(query)
    save_metrics(metrics,json_file)

    #After Index
    create_index(index_param)
    metrics = run_explain(query)
    save_metrics(metrics,json_file)

    