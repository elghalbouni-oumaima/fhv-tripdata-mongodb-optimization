import pandas as pd
import json
from clean_data import run_cleaning_pipeline


def convert_parquet_to_json(df, output_path):
    df.to_json(output_path, orient='records', lines=True)
