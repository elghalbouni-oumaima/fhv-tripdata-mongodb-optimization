
import pandas as pd
import json
import os

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
