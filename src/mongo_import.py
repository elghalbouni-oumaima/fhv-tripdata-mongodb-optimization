import json
from pymongo import MongoClient
from logger import logger

def connect_to_mongo(db_name):
    """Connect to MongoDB and return the database object."""
    try:
        client = MongoClient(uri= "")
        db = client[db_name]
        logger.info(f"connect_to_mongo() : Connected to MongoDB database: {db_name}")
    except Exception as e:
        logger.error(f"connect_to_mongo() : An error occurred while connecting to MongoDB: {e}")
    return db


def load_dictionary(file_path):
    """Load JSON data from a file."""
    try:
        logger.info(f"load_dictionary() : Lecture du fichier JSON Lines : {file_path}")
        docs = []
        with open(file_path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line:                      # ignorer lignes vides
                    try:
                        docs.append(json.loads(line))
                    except json.JSONDecodeError as jde:
                        logger.error(f"load_dictionary() : Erreur de décodage JSON : {jde} dans la ligne: {line}")

        logger.info(f"load_dictionary() : {len(docs)} documents chargés.")
        return docs
    
    except Exception as e:
        logger.error(f"load_dictionary() : An error occurred while loading JSON data: {e}")

def insert_data_to_collection(collection, data, batch_size=50000):
    """Insert data into the specified MongoDB collection."""
    logger.info(f"insert_data_to_collection() : Inserting {len(data)} records into the collection.")

    total = len(data)

    try:
        for i in range(0, total, batch_size):
            batch = data[i:i + batch_size]
            try:
                collection.insert_many(batch)
                logger.info(f"insert_data_to_collection() : Inserted records {i + 1} to {min(i + batch_size, total)}")
            except Exception as e:
                logger.error(f"insert_data_to_collection() : An error occurred while inserting batch starting at record {i + 1}: {e}")
        logger.info(f"insert_data_to_collection() : Insertion terminée.")

    except Exception as e:
        logger.error(f"insert_data_to_collection() :An error occurred while inserting data: {e}")


def import_json_to_mongodb(json_file_path, database_name, collection_name):

    #Connect to MongoDB
    client = connect_to_mongo(database_name)

    # Select the database and collection
    db = client[database_name]
    collection = db[collection_name]

    # Load JSON data
    data = load_dictionary(json_file_path)

    # Insert data into MongoDB collection
    insert_data_to_collection(collection, data)
    logger.info(f"insert_data_to_collection() : Import of {json_file_path} to MongoDB completed successfully!")   