import os

# def convert_parquet_to_json(df, output_folder):
    # df.to_json(output_path, orient='records', lines=True)

def convert_parquet_to_json(df, output_folder):
    i = 0
    batch_size = 2_068_170
    count = 0
    while i < len(df):
        batch = df.iloc[i:i+batch_size]
        json_path = os.path.join(output_folder, f"trips_{count}.json")
        batch.to_json(json_path, orient='records', lines=True, date_format="iso")
        i += batch_size 
        count +=1


# import dask.dataframe as dd
# def convert_parquet_to_json(df, json_path):
#     ddf = dd.from_pandas(df, npartitions=8)  
#     ddf.to_json(json_path, orient='records', lines=True)

# JSON_PATH = "data/processed"

# if os.path.isdir(JSON_PATH):
#     print("Directory exists")
# else:
#     print("Directory does NOT exist")