import json
from pymongo import MongoClient


def connect_to_mongo(db_name):
    """Connect to MongoDB and return the database object."""
    try:
        client = MongoClient(uri= "")
        db = client[db_name]
        print(f"Connected to MongoDB database: {db_name}")
    except Exception as e:
        print(f"An error occurred while connecting to MongoDB: {e}")
        raise e
    
    return db


def load_dictionary(file_path):
    """Load JSON data from a file."""
    try:
        print(f"Lecture du fichier JSON Lines : {file_path}")
        docs = []
        with open(file_path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line:                      # ignorer lignes vides
                    try:
                        docs.append(json.loads(line))
                    except json.JSONDecodeError as jde:
                        print(f"Erreur de décodage JSON : {jde} dans la ligne: {line}")

        print(f"{len(docs)} documents chargés.")
        return docs
    
    except Exception as e:
        print(f"An error occurred while loading JSON data: {e}")
        raise e


def insert_data_to_collection(collection, data, batch_size=50000):
    """Insert data into the specified MongoDB collection."""
    print(f"Inserting {len(data)} records into the collection.")

    total = len(data)

    try:
        for i in range(0, total, batch_size):
            batch = data[i:i + batch_size]
            try:
                collection.insert_many(batch)
                print(f"Inserted records {i + 1} to {min(i + batch_size, total)}")
            except Exception as e:
                print(f"An error occurred while inserting batch starting at record {i + 1}: {e}")
        
        print("Insertion terminée.")

    except Exception as e:
        print(f"An error occurred while inserting data: {e}")
        raise e


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

    print(f"\n Importation de {json_file_path} vers MongoDB terminée avec succès !")
   