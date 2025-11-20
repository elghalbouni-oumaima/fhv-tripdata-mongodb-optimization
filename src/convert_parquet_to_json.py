import pandas as pd

def convert_parquet_to_json(df, output_path):
    df.to_json(output_path, orient='records', lines=True)
