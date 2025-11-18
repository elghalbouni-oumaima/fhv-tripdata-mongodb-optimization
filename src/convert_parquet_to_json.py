import pandas as pd
import json
from clean_data import run_cleaning_pipeline


def convert_parquet_to_json(df, output_path):
    df.to_json(output_path, orient='records', lines=True)

if __name__ == "__main__":
    output_json_path = '../data/processed/trips.json'
    INPUT_PATH = "../data/row/fhvhv_tripdata_2021-10.parquet"
    columns_to_remove =['originating_base_num', 'on_scene_datetime','access_a_ride_flag']
    columns_clean = ['hvfhs_license_num','dispatching_base_num']
    flag_cols = ['shared_request_flag','shared_match_flag', 'wav_request_flag',	'wav_match_flag']
    df = run_cleaning_pipeline(INPUT_PATH, columns_to_remove, columns_clean, flag_cols)
    convert_parquet_to_json(df, output_json_path)
