import pandas as pd
import os
from src.logger import logger
import pyarrow.parquet as pq

def load_data(file_path):
    if not os.path.exists(file_path):
        logger.warning(f"clean_data.py : The file {file_path} does not exist.")
        return None
    parquet_file = pq.ParquetFile(file_path)
    df_list = []
    batch_size = 500_000
    for batch in parquet_file.iter_batches(batch_size=batch_size):
        df_list.append(batch.to_pandas())
    df = pd.concat(df_list, ignore_index=True)

    return df


def cast_column_float(df):
    for x in df:
        if pd.api.types.is_float_dtype(df[x]):
            df[x] = df[x].astype(float)
    return df

def cast_column_int(df):
    for x in df:
        if pd.api.types.is_integer_dtype(df[x]):
            df[x] = df[x].astype(int)
    return df

def cast_column_datetime(df):
    for x in df:
        if pd.api.types.is_datetime64_any_dtype(df[x]):
            df[x] = pd.to_datetime(df[x])
    return df

def remove_unnecessary_columns(df,columns_to_remove=None):
    df = df.drop(columns=columns_to_remove)
    return df

def clean_string_columns(df, column_to_clean=None):
    df[column_to_clean] = df[column_to_clean].str.upper().str.strip()
    return df

def encode_flags(df, flag_cols):
    pd.set_option('future.no_silent_downcasting', True)
    df[flag_cols]= df[flag_cols].replace({'N':0,'Y':1})
    return df

def run_cleaning_pipeline(input_path,columns_to_remove,columns_clean,flag_cols):
    try:
        df = load_data(input_path)
        df = remove_unnecessary_columns(df, columns_to_remove)
        df = cast_column_float(df)
        df = cast_column_int(df)
        df = cast_column_datetime(df)
        for col in columns_clean:
            df = clean_string_columns(df, col)
        df = encode_flags(df,flag_cols)
        return df
        
    except Exception as e:
        logger.error(f"clean_data.py :An error occurred: {e}")
