from src.clean_data import run_cleaning_pipeline
from src.convert_parquet_to_json import convert_parquet_to_json
from src.mongo_import import import_json_to_mongodb
from src.logger import logger
import glob
INPUT_PATH = "data/raw/fhvhv_tripdata_2021-10.parquet"
JSON_PATH = "data/processed/trips_.json"
JSON_PATH_ALL = "data/processed/trips_*.json"
JSON_FOLDER_PATH = "data/processed/"

columns_to_remove =[
    'originating_base_num', 
    'on_scene_datetime',
    'access_a_ride_flag'
]

columns_clean = [
    'hvfhs_license_num',
    'dispatching_base_num'
]

flag_cols = [
    'shared_request_flag',
    'shared_match_flag', 
    'wav_request_flag',	
    'wav_match_flag'
]

DB_NAME = "trips_db"
COLLECTION_NAME = "fhvhv_trips_2021-10"

def run_full_pipeline():
    if not any(glob.glob(JSON_PATH_ALL)):
        # Step 1: Clean the data and get a DataFrame
        df = run_cleaning_pipeline(INPUT_PATH, columns_to_remove, columns_clean, flag_cols)
        # Step 2: Convert the cleaned DataFrame to JSON Lines format
        convert_parquet_to_json(df, JSON_FOLDER_PATH)

    # Step 3: Import the JSON Lines data into MongoDB
    # import_json_to_mongodb(JSON_PATH, DB_NAME, COLLECTION_NAME)
    json_files = sorted(glob.glob(JSON_PATH_ALL))
    for json_file in json_files:
        print(f"Importing {json_file} to MongoDB...")
        import_json_to_mongodb(json_file, DB_NAME, COLLECTION_NAME)

if __name__ == "__main__":
    run_full_pipeline()
    logger.info(f"runApplication.py : Full pipeline from Parquet to MongoDB completed successfully!")
