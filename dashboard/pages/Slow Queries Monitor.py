import dash
from dash import html, dcc, dash_table, Input, Output, State, ctx
from utils.loader import load_benchmark,load_latest_benchmark
from utils.charts import make_comparison_bar,make_query_card, make_kpi_card,build_double_donut_chart,build_bar_chart
import json
from dash_svg import Svg, Line, Polygon
import os

dash.register_page(__name__, path="/slow-queries-monitor", name="Slow Queries Monitor")
last_file, error = load_latest_benchmark('simple')
data = load_benchmark(last_file) if last_file else {}
before = data.get('results', {}).get('before', {})
after = data.get('results', {}).get('after', {})

queries=[
    {"Query Tested": '{"trip_time": {"$gte": 300}}', "index": '{"trip_time": 1}'},
    {"Query Tested": '{"PULocationID": 100}', "index": '{"PULocationID": "hashed"}'},
    {"Query Tested": '{"hvfhs_license_num": "HV0003", "PULocationID": 97}',
     "index": '{"hvfhs_license_num": 1, "PULocationID": 1}'},
    {"Query Tested":'{"trip_miles": {"$gte": 5, "$lte": 10}}',
     "index": '{"trip_miles": 1}'},
    {"Query Tested": '{"trip_miles": {"$gte": 5}, "trip_time": {"$gte": 1200}}',
     "index": '{"trip_miles": 1, "trip_time": -1}'},
    {"Query Tested": '{"dispatching_base_num": "B02764"}',
     "index":' {"dispatching_base_num": 1}'},
    {"Query Tested":'{"base_passenger_fare": {"$gte": 20}}',
     "index": '{"base_passenger_fare": 1}'},
    {"Query Tested":'{"hvfhs_license_num": "HV0003", "trip_miles": {"$gte": 10}, "trip_time": {"$gte": 1800}}',
     "index": '{"hvfhs_license_num": 1, "trip_miles": 1, "trip_time": -1}'},
    {"Query Tested": ' {"DOLocationID": 85}', "index": '{"DOLocationID": 1}'},
    {"Query Tested":' {"hvfhs_license_num": "HV0005"}', "index": '{"hvfhs_license_num": 1}'},
]

# average Excution Time
execution_time_file = load_benchmark('../results/benchmarking/execution_time.json') 
print(execution_time_file)
s = 0
SlowedQuery = 0
for i in range(len(execution_time_file)):
    s += execution_time_file[i]['executionTimeMillis']
    if execution_time_file[i]['executionTimeMillis'] >200:
        SlowedQuery +=1
avrg_time = s/len(execution_time_file)

#Slowed Query

layout = html.Div([
    html.H2(f"Identifying and analyzing queries with high execution time"),
    # KPI Cards
    html.Div([
        make_query_card("Nomber of querey tested ", len(execution_time_file)),
        make_query_card("Slowed query",SlowedQuery),
        make_query_card("FAst query", len(execution_time_file) - SlowedQuery),
        make_query_card("Average execution time",avrg_time,'ms'),
    ],id='cards-kpi', className="grid-4"),    
    html.Div([
            html.H3("Détails Chiffrés"),
            #dcc.Graph(figure=make_comparison_bar(before, after, 'totalDocsExamined', "Documents Examinés")),
            dash_table.DataTable(
                id="details-table",
                data=queries,
                style_cell={'textAlign': 'left', 'padding': '10px'},
                style_header={'backgroundColor': '#ecf0f1', 'fontWeight': 'bold'},
                style_as_list_view=True
            )
    ], className="card"),
    

   
])

