import dash
from dash import html, dcc, dash_table, Input, Output, State, ctx
from utils.loader import load_benchmark,load_latest_benchmark
from utils.charts import make_comparison_bar,make_query_card, make_kpi_card,build_double_donut_chart,build_bar_chart
import json
from dash_svg import Svg, Line, Polygon
import os

dash.register_page(__name__, path="/slow-queries-monitor", name="Slow Queries Monitor")
last_file, error = load_latest_benchmark('q7')
data = load_benchmark(last_file) if last_file else {}
before = data.get('results', {}).get('before', {})
after = data.get('results', {}).get('after', {})

queries = [

    {"name": "q1_triptime_range",
     "query": '{"trip_time": {"$gte": 60, "$lte": 1200}}',
     "index": '{"trip_time": 1}'},

    {"name": "q2_tripmiles_large",
     "query": '{"trip_miles": {"$gte": 1, "$lte": 20}}',
     "index": '{"trip_miles": 1}'},

    {"name": "q3_fare_range",
     "query": '{"base_passenger_fare": {"$gte": 5, "$lte": 50}}',
     "index": '{"base_passenger_fare": 1}'},

    {"name": "q4_license_time_miles",
     "query": '{"hvfhs_license_num": "HV0003","trip_time": {"$gte": 300},"trip_miles": {"$gte": 5}}',
     "index": '{"hvfhs_license_num": 1, "trip_time": 1, "trip_miles": 1}'},

    {"name": "q5_base_num",
     "query": '{"dispatching_base_num": "B02764"}',
     "index": '{"dispatching_base_num": 1}'},

    {"name": "q6_time_filtered_sorted",
     "query": '{"trip_time": {"$gte": 300}}',
     "sort": '{"trip_miles": -1}',
     "index": '{"trip_time": 1, "trip_miles": -1}'},

    {"name": "q7_PULoc_time",
     "query": '{"PULocationID": 132,"trip_miles": {"$gte": 2, "$lte": 15}}',
     "index": '{"PULocationID": 1, "trip_miles": 1}'},

    {"name": "q8_DOLocation",
     "query": '{"DOLocationID": 230}',
     "index": '{"DOLocationID": 1}'},

    {"name": "q9_flags",
     "query": '{"shared_request_flag": true,"wav_request_flag": false}',
     "index": '{"shared_request_flag": 1, "wav_request_flag": 1}'},

    {"name": "q10_license_time",
     "query": '{"hvfhs_license_num": "HV0005","trip_time": {"$gte": 600, "$lte": 2400},"trip_miles": {"$gte": 3}}',
     "index": '{"hvfhs_license_num": 1, "trip_time": 1, "trip_miles": 1}'},

]


# average Excution Time
execution_time_file = load_benchmark('../results/benchmarking/execution_time.json') 
# print(execution_time_file)
s = 0
SlowedQuery = 0
for i in range(len(execution_time_file)):
    s += execution_time_file[i]['executionTimeMillis']
    queries[i]['executionTimeMillis'] = execution_time_file[i]['executionTimeMillis']
    if execution_time_file[i]['executionTimeMillis'] > 200:
        SlowedQuery +=1
avrg_time = s/len(execution_time_file)
queries = [
    {k: v for k, v in q.items() if k != "name"} 
    for q in queries
]
queries = [
    {
        "Query tested": q.get("query"),
        "Appropriate index to optimize the query": q.get("index"),
        **{k: v for k, v in q.items() if k not in ["query", "index", "name"]}
    }
    for q in queries
]


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
            html.H3("Executed Queries"),
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

