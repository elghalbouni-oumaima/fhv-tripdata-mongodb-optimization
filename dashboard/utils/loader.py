
import pandas as pd
import json
import os
import re

# -- CORRECTION: Gestion des chemins absolus --
# On récupère le dossier où se trouve loader.py (dashboard/utils)
current_dir = os.path.dirname(os.path.abspath(__file__))
# On remonte d'un niveau pour avoir la racine du projet (dashboard)
project_root = os.path.dirname(current_dir)

def get_path(relative_path):
    # Construit le chemin absolu: dashboard/data/sample_dataset.csv
    return os.path.join(project_root, relative_path)

def load_dataset(path):
    full_path = get_path(path)
    try:
        print(f"Chargement CSV depuis : {full_path}")
        df = pd.read_csv(full_path, parse_dates=['pickup_datetime', 'dropoff_datetime'])
        return df
    except Exception as e:
        print(f"ERREUR CRITIQUE chargement dataset: {e}")
        return pd.DataFrame()

def load_benchmark(path):
    full_path = get_path(path)
    try:
        with open(full_path, 'r') as f:
            data = json.load(f)
        return data
    except Exception as e:
        print(f"ERREUR CRITIQUE chargement benchmark: {e}")
        return {}
def get_file(input_value):
    if input_value == 'hashed':
        data = load_benchmark('../results/benchmarking/hashed_index_2025-11-30_15-27-30.json')
    elif input_value == 'compound':
        data = load_benchmark('../results/benchmarking/compound_index_2025-11-30_15-26-24.json')
    elif input_value == 'simple':
        data = load_benchmark('../results/benchmarking/simple_index_2025-11-30_15-25-32.json')
    return data
   
def load_latest_benchmark(index_type):

    folder = os.path.abspath(
        os.path.join(os.path.dirname(__file__), "..", "..", "results", "benchmarking")
    )

    pattern = re.compile(rf"{index_type}_index_.*\.json")

    candidates = [f for f in os.listdir(folder) if pattern.match(f)]

    if not candidates:
        return None, f"No benchmark file found for index type: {index_type}"

    candidates.sort(reverse=True)
    latest_file = os.path.join(folder, candidates[0])
    return latest_file, None
