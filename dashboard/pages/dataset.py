import dash
from dash import html, dcc, callback, Input, Output
import pandas as pd
from utils.loader import load_dataset
from utils.charts import make_histogram, make_boxplot, make_heatmap, make_timeline

dash.register_page(__name__, path='/', name='Dataset')

# Chargement données
df = load_dataset('data/sample_dataset.csv')

if df.empty:
    layout = html.Div([html.H2("Erreur de chargement")])
else:
    # Calcul TOP 10
    try:
        top_zones = df['PULocationID'].value_counts().head(10).reset_index()
        top_zones.columns = ['ZoneID', 'Courses']
        # On utilise bar pour le top 10 pour changer
        top_fig = make_histogram(top_zones, 'ZoneID', 'TOP 10 Pickup Zones') 
    except:
        top_fig = {}

    layout = html.Div([
        html.H2("Exploration du Dataset Uber"),
        
        # Contrôles
        html.Div([
            html.Label("Choisir une variable pour l'histogramme :"),
            dcc.Dropdown(
                id='variable-dropdown',
                options=[
                    {'label': 'Distance (miles)', 'value': 'trip_miles'},
                    {'label': 'Durée (sec)', 'value': 'trip_time'},
                    {'label': 'Tarif ($)', 'value': 'base_passenger_fare'}
                ],
                value='trip_miles',
                clearable=False
            )
        ], className="card", style={'maxWidth': '400px'}),
        
        # Grille 2x2 (Équilibrée)
        html.Div([
            # Col 1
            html.Div([
                dcc.Graph(id='main-hist', className="card"),
                dcc.Graph(figure=make_heatmap(df, "Heatmap Pickup -> Dropoff"), className="card")
            ]),
            # Col 2
            html.Div([
                dcc.Graph(figure=make_boxplot(df, 'base_passenger_fare', "Distribution des tarifs"), className="card"),
                dcc.Graph(figure=make_timeline(df, "Courses par heure"), className="card")
            ])
        ], className="grid-2"),
        
        # Ligne du bas : Top 10 (Full width)
        html.Div([
            dcc.Graph(figure=top_fig, className="card")
        ], className="full-width")
    ])

    @callback(
        Output('main-hist', 'figure'),
        Input('variable-dropdown', 'value')
    )
    def update_hist(col):
        if df.empty: return {}
        return make_histogram(df, col, f"Distribution : {col}")