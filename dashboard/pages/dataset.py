import dash
from dash import html, dcc, callback, Input, Output
import plotly.express as px
import pandas as pd
import numpy as np
import json, os
from datetime import date
from plotly.subplots import make_subplots
import plotly.graph_objects as go
from functools import lru_cache
from shapely import wkt
import glob

dash.register_page(__name__, path='/', name='Dataset')

# --- Retrieve data from a JSON file ---
date_today = date.today()
folder = "dashboard/data/historical_data_json"
# os.makedirs(folder, exist_ok=True)


@lru_cache(maxsize=None)
def load_json_file(file_name):
    with open(file_name, "r", encoding="utf-8") as f:
        return json.load(f)

#############################
pattern = os.path.join(folder, "cart_visualization_*.json")
files_1 = glob.glob(pattern)
cart_data = load_json_file(files_1[0])

#############################
pattern_2 = os.path.join(folder, "trips_distance_time_by_company_*.json")
files_2 = glob.glob(pattern_2)
df_distance_time_by_company = pd.DataFrame(load_json_file(files_2[0]))
df_distance_time_by_company["AvgTimeMin"] = df_distance_time_by_company["AvgTime"] / 60

###############################
pattern_3 = os.path.join(folder, "total_profit_by_company_*.json")
files_3 = glob.glob(pattern_3)
profit = pd.DataFrame(load_json_file(files_3[0]))

def prepare_profit_pie_data(profit_df):
    df = profit_df.copy()
    df = df.rename(columns={"_id": "Company"})
    total = df["total_profit"].sum()
    df["percent"] = df["total_profit"] / total * 100

    df = df[["Company", "total_profit", "avg_profit", "trips", "percent"]]

    df["custom_data"] = df[["avg_profit", "trips", "percent"]].values.tolist()
    return df

pie_df = prepare_profit_pie_data(profit)

# Pie chart
fig = px.pie(
    pie_df,
    names="Company",
    values="total_profit",
    hole=0.4,
    title="Profit Distribution by Company",
    custom_data="custom_data"  
)
###############################
pattern_4 = os.path.join(folder, "Average_Price_driver_company_*.json")
files_4 = glob.glob(pattern_4)
prive_drive = pd.DataFrame(load_json_file(files_4[0]))
prive_drive = prive_drive.rename(columns={"_id": "Company"})

######### map ###############
df_locations = pd.read_csv("dashboard/data/taxi_zones.csv")
df_locations['geometry'] = df_locations['the_geom'].apply(wkt.loads)

df_locations['centroid'] = df_locations['geometry'].apply(lambda x: x.centroid)
df_locations['lat'] = df_locations['centroid'].apply(lambda x: x.y)
df_locations['lon'] = df_locations['centroid'].apply(lambda x: x.x)

df_locations_coords = df_locations[['LocationID', 'lat', 'lon']]

pattern_5 = os.path.join(folder, "trips_locations_*.json")
files_5 = glob.glob(pattern_5)
df_trips = pd.DataFrame(load_json_file(files_5[0]))

df_trips = df_trips.merge(df_locations_coords, how='left', left_on='PULocationID', right_on='LocationID')
df_trips.rename(columns={'lat': 'PU_lat', 'lon': 'PU_lon'}, inplace=True)
df_trips.drop(columns=['LocationID'], inplace=True)

df_trips = df_trips.merge(df_locations_coords, how='left', left_on='DOLocationID', right_on='LocationID')
df_trips.rename(columns={'lat': 'DO_lat', 'lon': 'DO_lon'}, inplace=True)
df_trips.drop(columns=['LocationID'], inplace=True)

###############################
pattern_6 = os.path.join(folder, "trips_per_day_by_company_*.json")
files_6 = glob.glob(pattern_6)

pattern_7 = os.path.join(folder, "trips_distance_total_by_day_*.json")
files_7 = glob.glob(pattern_7)
# --- Cartes (KPIs) ---
card_style = {
    'flex':'1', 
    'background-color':'#ffffff',  
    'padding':'20px', 
    'border-radius':'8px',
    'box-shadow':'0 2px 5px rgba(0,0,0,0.1)',
    'text-align':'center',
    'display':'flex',
    'flex-direction':'column',
    'justify-content':'center'
}

# Create cards using the defined style
cards = [
    html.Div([
        html.H4("Total Trips", style={'margin':'0', 'font-weight':'500', 'color':'#333'}),
        html.P(f"{cart_data["total_trips"]:.2f} M", style={'margin':'0', 'font-size':'24px', 'font-weight':'600', 'color':'#111'})
    ], style=card_style),

    html.Div([
        html.H4("Document size", style={'margin':'0', 'font-weight':'500', 'color':'#333'}),
        html.P(f"{cart_data["document_size"]:.3f} GB", style={'margin':'0', 'font-size':'24px', 'font-weight':'600', 'color':'#111'})
    ], style=card_style),
    
    html.Div([
        html.H4("Moyenne Distance", style={'margin':'0', 'font-weight':'500', 'color':'#333'}),
        html.P(f"{cart_data["avg_distance"]:.3f} miles", style={'margin':'0', 'font-size':'24px', 'font-weight':'600', 'color':'#111'})
    ], style=card_style),
    
    html.Div([
        html.H4("Moyenne Temps", style={'margin':'0', 'font-weight':'500', 'color':'#333'}),
        html.P(f"{cart_data["avg_time"]:.3f} min", style={'margin':'0', 'font-size':'24px', 'font-weight':'600', 'color':'#111'})
    ], style=card_style),
    
    html.Div([
        html.H4("Company", style={'margin':'0', 'font-weight':'500', 'color':'#333'}),
        html.P(f"{cart_data["company_count"]}", style={'margin':'0', 'font-size':'24px', 'font-weight':'600', 'color':'#111'})
    ], style=card_style),
]

# Container for cards
html.Div(cards, style={
    'display':'flex', 
    'gap':'20px', 
    'margin-bottom':'30px',
    'width':'100%'
})

# --- Main Layout ---
layout = html.Div([
    html.H2("Dataset Exploration"),

    # --- KPI Cards ---
    html.Div(cards, className="kpi-grid", style={'display': 'flex', 'gap': '20px', 'margin-bottom':'30px'}),
    
    # --- Linear graph of 3 companies ---
    
    dcc.Graph(figure=px.line(load_json_file(files_6[0]), x='Date', y='Trips', color='Company', title="Trips per day and Company"), className="card", style={'margin-bottom':'30px'}),

    # --- Maps côte à côte  ---

    html.Div([
        # Pickup Map
        dcc.Graph(
            figure=px.scatter_mapbox(
                df_trips, 
                lat='PU_lat', 
                lon='PU_lon', 
                size='tripCount',         
                hover_name='PULocationID', 
                hover_data={'tripCount': True, 'PU_lat': False, 'PU_lon': False}, 
                color='tripCount',        
                color_continuous_scale='Viridis',
                zoom=10,
                height=600,
                mapbox_style="open-street-map", 
                title="Pickups per zone"
            ),
            className="card",
            style={'flex': '1 1 48%'}
        ),

        # Dropoff Map
        dcc.Graph(
            figure=px.scatter_mapbox(
                df_trips, 
                lat='DO_lat', 
                lon='DO_lon', 
                size='tripCount',
                hover_name='DOLocationID',
                hover_data={'tripCount': True, 'DO_lat': False, 'DO_lon': False},
                color='tripCount',
                color_continuous_scale='Viridis',
                zoom=10,
                height=600,
                mapbox_style="open-street-map", 
                title="Dropoffs per zone"
            ),
            className="card",
            style={'flex': '1 1 48%'}
        ),
    ], style={'display': 'flex', 'gap':'10px', 'margin-bottom':'30px'}),
    # --- Donut / Pie charts ---
    html.Div([
        dcc.Graph(figure=fig, className="card",style={ 'flex': '1 1 48%'}),
        dcc.Graph(figure=px.bar(prive_drive,x="AvgDriverPay", y="Company",orientation='h', title="Average pay per driver per company"),className="card",style={'margin-bottom':'30px', 'flex': '1 1 48%'} )
    ], style={'display':'flex', 'gap':'10px', 'margin-bottom':'30px'}),

    # --- Bar chart distance vs temps ---
    dcc.Graph(figure=px.bar(df_distance_time_by_company, x='Company', y=['AvgDistance','AvgTimeMin'], barmode='group', title="Distance (miles) vs. Time (minutes) by Company"), className="card", style={'margin-bottom':'30px'}),

    # --- Distance par jour ---
    dcc.Graph(figure=px.line(load_json_file(files_7[0]),x='Date',y='AvgDistance',title="Total distance per day"),className="card"),

])
