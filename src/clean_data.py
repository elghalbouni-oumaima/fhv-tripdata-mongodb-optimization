import pandas as pd
import os

def load_data(file_path):
    if  not os.path.exists(file_path):
        raise FileNotFoundError(f"The file {file_path} is notexist.")
    return pd.read_parquet(file_path)

def cast_column_float(df, typeData='float64'):
    for x in df:
        if df[x].dtype == typeData:
            df[x] = df[x].astype(typeData)
    return df

def cast_column_int(df, typeData='int64'):
    for x in df:
        if df[x].dtype == typeData:
            df[x] = df[x].astype(typeData)
    return df

def cast_column_datetime(df):
    for x in df:
        if df[x].dtype == 'datetime64[us]':
            df[x] = pd.to_datetime(df[x])
    return df

def remove_unnecessary_columns(df,columns_to_remove=None):
    df = df.drop(columns=columns_to_remove)
    return df

def clean_string_columns(df, column_to_clean=None):
    df[column_to_clean] = df[column_to_clean].str.upper().str.strip()
    return df

def encode_flags(df, flag_cols):
    df[flag_cols]= df[flag_cols].replace({'N':0,'Y':1})
    return df

def add_identifiers(df):
    df["row_id"] = df.index 
    return df

def run_cleaning_pipeline(input_path,columns_to_remove,columns_clean,flag_cols):
    try:
        df = load_data(input_path)
        df = cast_column_float(df)
        df = cast_column_int(df)
        df = cast_column_datetime(df)
        df = remove_unnecessary_columns(df, columns_to_remove)
        for col in columns_clean:
            df = clean_string_columns(df, col)
        df = encode_flags(df,flag_cols)
        df = add_identifiers(df)
        return df
        
    except Exception as e:
        print(f"An error occurred: {e}")
    
if __name__ == "__main__":
    INPUT_PATH = "../data/row/fhvhv_tripdata_2021-10.parquet"
    columns_to_remove =['originating_base_num', 'on_scene_datetime','access_a_ride_flag']
    columns_clean = ['hvfhs_license_num','dispatching_base_num']
    flag_cols = ['shared_request_flag','shared_match_flag', 'wav_request_flag',	'wav_match_flag']
    run_cleaning_pipeline(INPUT_PATH, columns_to_remove, columns_clean, flag_cols)