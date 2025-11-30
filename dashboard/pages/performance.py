import dash
from dash import html, dcc, dash_table, Input, Output, State, ctx
import pandas as pd
from utils.loader import load_benchmark
from utils.charts import make_comparison_bar, make_kpi_card,build_double_donut_chart,build_bar_chart

import json

dash.register_page(__name__, path="/performance", name="Performance")

# Chargement
data = load_benchmark('../results/benchmarking/hashed_index_2025-11-27_11-46-38.json')
before = data['results']['before']
after = data['results']['after']
print(after.get('executionStages', 'N/A').get('inputStage', 'N/A').get('indexName', 'N/A'))
# ============================================
# 1. Configuration des options
# ============================================

FIELDS = [
    {"label": "PULocationID", "value": "PULocationID"},
    {"label": "DOLocationID", "value": "DOLocationID"},
    {"label": "trip_time", "value": "trip_time"},
    {"label": "trip_miles", "value": "trip_miles"},
    {"label": "base_passenger_fare", "value": "base_passenger_fare"},
    {"label": "hvfhs_license_num", "value": "hvfhs_license_num"},
]

PRESET_QUERIES = {
    "simple": {
        "query": {"trip_time": {"$gte": 300}},
        "index": {"trip_time": 1},
        "name": "simple_index"
    },
    "compound": {
        "query": {
            "hvfhs_license_num": "HV0003",
            "PULocationID": 97
        },
        "index": {"hvfhs_license_num": 1, "PULocationID": 1},
        "name": "compound_index"
    },
    "hashed": {
        "query": {"PULocationID": 100},
        "index": {"PULocationID": "hashed"},
        "name": "hashed_index"
    }
}

BENCHMARK_QUERIES = {
    "simple": "db.fhvhv_trips_2021-10.find({ field: value })",
    "compound": "db.fhvhv_trips_2021-10.find({ field1: value1 }).sort({ field2: 1 })",
    "hashed": "db.fhvhv_trips_2021-10.find({ hashField: value })"
}

# ============================================
# 2. Header : UI de sélection (Mode + Query Builder)
# ============================================

query_controls = html.Div([

    # Mode FIND / EXIST
    html.Div([ 
        # LEFT SIDE → Execution Mode
        html.Div([
            html.Label("Execution Mode:"),
            dcc.RadioItems(
                id="mode-radio",
                options=[
                    {"label": " exist ", "value": "aggregate"},
                    {"label": " find ", "value": "find"},
                ],
                value="aggregate",
                inline=True
            ),
        ], style={
            "flex": "1",
            "marginRight": "20px"
        }),

        # MIDDLE SIDE → Search bar
        html.Div([
            dcc.Input(
                id="query-preview",
                type="text",
                placeholder="Benchmark query will appear here...",
                style={
                    "width": "800px",
                    "height": "38px",
                    "fontSize": "16px"
                }
            )
        ], style={
            "flex": "1",
            "display": "flex",
            "flexDirection": "column",
            "alignItems": "center"
        }),

        # RIGHT SIDE → Benchmark selector (ALIGNÉ À DROITE)
        html.Div([
            #html.Label("Choose a predefined benchmark:"),
            dcc.Dropdown(
                id="benchmark-dropdown",
                options=[
                    {"label": "Simple Index Query", "value": "simple"},
                    {"label": "Compound Index Query", "value": "compound"},
                    {"label": "Hashed Index Query", "value": "hashed"},
                ],
                value="simple",
                style={"width": "250px"}
            )
        ], style={
            "flex": "1",
            "display": "flex",
            "flexDirection": "column",
            "alignItems": "flex-end"
        }),

    ], style={
        "display": "flex",
        "gap": "20px",
        "alignItems": "center",
        "marginBottom": "20px"
    }),


    # --- Find Builder + Index Builder (ALIGNÉS À DROITE) ---
    html.Div([

        # Find Builder
        html.Div(id="find-builder", children=[
            html.Div([

                # FIELD
                html.Div([
                    html.Label("Field:", className="form-label"),
                    dcc.Dropdown(
                        id="find-field",
                        options=FIELDS,
                        placeholder="Select field...",
                        className="form-input"
                    )
                ], className="form-row"),

                # VALUE
                html.Div([
                    html.Label("Value:", className="form-label"),
                    dcc.Input(
                        id="value-input",
                        type="text",
                        style={
                            "width": "243px",
                            "height": "30px",
                            "fontSize": "16px"
                        }
                    )
                ], className="form-row"),

                # SORT ENABLE
                html.Div([
                    html.Label("Sort results?", className="form-label"),
                    dcc.Checklist(
                        id="sort-check",
                        options=[{"label": "Enable sort()", "value": "yes"}],
                        className="form-input"
                    )
                ], className="form-row"),

                # SORT OPTIONS BLOCK
                html.Div(id="sort-options"),

                # BOUTON SEARCH
                html.Button(
                    "Search",
                    id="search-btn",
                    className="btn-search"
                ),

            ], className="form-container"),

        ], className="card"
        ,style={"flex": "1", "marginRight": "20px"}),

        # INDEX BUILDER
        html.Div(
            id="index-builder",
            className="card",
            style={"flex": "1","padding": "20px"}
        )

        ], id="builder-container"
        , style={
            "display": "flex",
            "gap": "20px",
            "flexDirection": "row",
            "marginTop": "20px"
        })


    ], className="card")



# ============================================
# 3. Layout principal
# ============================================

layout = html.Div([
    html.H2(f"Benchmark Index : {data.get('index_name', 'N/A')}"),
    
    # Badges
    html.Div([
        html.Span(f"Index: {after.get('executionStages', 'N/A').get('inputStage', 'N/A').get('indexName', 'N/A')}", className="badge-info"),
        html.Span(f"Time Optimization: {before.get('executionTimeMillis', 0) - after.get('executionTimeMillis', 0)} ms", className="badge-info"),
    ],id='badge-info', className="card"),
    query_controls,  
    # KPI Cards
    html.Div([
        make_kpi_card("Execution Time", before.get('executionTimeMillis'), after.get('executionTimeMillis'), "ms"),
        make_kpi_card("Optimisation Time", before.get('optimizationTimeMillis'), after.get('optimizationTimeMillis'), "ms"),
        make_kpi_card("Docs Examined", before.get('totalDocsExamined'), after.get('totalDocsExamined')),
        make_kpi_card("Keys Examined", before.get('totalKeysExamined'), after.get('totalKeysExamined')),
    ],id='cards-kpi', className="grid-4"),
    
    # Comparaison Graphique & Table
    html.Div([
        html.Div([
            html.H3("Performance Metrics Comparison (Before vs After Index)"),
            dcc.Graph(id='bar_chart',figure=build_bar_chart(before,after),style={'width': '100%'}),
        ], className="card"),
        
        html.Div([
            html.H3("Documents and Keys Examined"),
            html.Div([
                dcc.Graph(id='donut_chart',figure=build_double_donut_chart(before,after),style={'width': '100%'}),
            ],className="donut-card")
           
        ],className="card"),
        
        
    ], className="grid-2"),
    html.Div([
            html.H3("Détails Chiffrés"),
            #dcc.Graph(figure=make_comparison_bar(before, after, 'totalDocsExamined', "Documents Examinés")),
            dash_table.DataTable(
                id="details-table",
                data=[],
                style_cell={'textAlign': 'left', 'padding': '10px'},
                style_header={'backgroundColor': '#ecf0f1', 'fontWeight': 'bold'},
                style_as_list_view=True
            )
    ], className="card"),
    
    # Explain Tree
    # html.Div([
    #     html.H3("Explain Plan (Structure des Stages)"),
    #     html.Div([
    #         html.Div([
    #             html.H4("BEFORE (CollScan)"),
    #             generate_tree_html(before.get('executionStages'))
    #         ], style={'flex': 1}),
    #          html.Div([
    #             html.H4("AFTER (IndexScan)"),
    #             generate_tree_html(after.get('executionStages'))
    #         ], style={'flex': 1})
    #     ], style={'display': 'flex', 'justifyContent': 'space-around'})
    # ], className="card")
    # html.H2("Performance & Index Benchmark Visualization"),

    

    # html.Br(),

    # html.Div(id="benchmark-content")
])



# ============================================
# 4. Callbacks
# ============================================
@dash.callback(
    Output("badge-info", "children"),
    Input("benchmark-dropdown", "value")
)
def update_badge_info(input_value):
    if input_value == 'hashed':
        data = load_benchmark('../results/benchmarking/compound_index_2025-11-24_12-23-33.json')
    elif input_value == 'compound':
        data = load_benchmark('../results/benchmarking/hashed_index_2025-11-27_11-46-38.json')
    elif input_value == 'simple':
        data = load_benchmark('../results/benchmarking/hashed_index_2025-11-24_12-12-50.json')
    before = data['results']['before']
    after = data['results']['after']
    print(before.get('executionTimeMillis'))
    idx_name = after.get('executionStages', 'N/A').get('inputStage', 'N/A')
    if idx_name.get('indexName', 'N/A') == 'N/A':
        idx_name = idx_name.get('inputStage', 'N/A')
    dv =[
        html.Span(f"Index: {idx_name.get('indexName', 'N/A')}", className="badge-info"),
        html.Span(f"Time Optimization: {before.get('executionTimeMillis', 0) - after.get('executionTimeMillis', 0)} ms", className="badge-info"),
    ]
    return dv
@dash.callback(
    Output("cards-kpi", "children"),
    Input("benchmark-dropdown", "value")
)
def update_cards(input_value):
    if input_value == 'hashed':
        data = load_benchmark('../results/benchmarking/compound_index_2025-11-24_12-23-33.json')
    elif input_value == 'compound':
        data = load_benchmark('../results/benchmarking/hashed_index_2025-11-27_11-46-38.json')
    elif input_value == 'simple':
        data = load_benchmark('../results/benchmarking/hashed_index_2025-11-24_12-12-50.json')
    before = data['results']['before']
    after = data['results']['after']
    print(before.get('executionTimeMillis'))
    dv =[
        make_kpi_card("Execution Time", before.get('executionTimeMillis'), after.get('executionTimeMillis'), "ms"),
        make_kpi_card("Optimisation Time", before.get('optimizationTimeMillis'), after.get('optimizationTimeMillis'), "ms"),
        make_kpi_card("Docs Examined", before.get('totalDocsExamined'), after.get('totalDocsExamined')),
        make_kpi_card("Keys Examined", before.get('totalKeysExamined'), after.get('totalKeysExamined')),
    ]
    return dv

@dash.callback(
    Output("details-table", "data"),
    Input("benchmark-dropdown", "value")
)
def update_details_table(input_value):
    if input_value == 'hashed':
        data = load_benchmark('../results/benchmarking/compound_index_2025-11-24_12-23-33.json')
    elif input_value == 'compound':
        data = load_benchmark('../results/benchmarking/hashed_index_2025-11-27_11-46-38.json')
    elif input_value == 'simple':
        data = load_benchmark('../results/benchmarking/hashed_index_2025-11-24_12-12-50.json')
    before = data['results']['before']
    after = data['results']['after']
    dt=[
            {'Metric': 'Time (ms)', 'Before': before.get('executionTimeMillis'), 'After': after.get('executionTimeMillis')},
            {'Metric': 'Docs Examined', 'Before': before.get('totalDocsExamined'), 'After': after.get('totalDocsExamined')},
            {'Metric': 'Keys Examined', 'Before': before.get('totalKeysExamined'), 'After': after.get('totalKeysExamined')},
            {'Metric': 'nReturned', 'Before': before.get('nReturned'), 'After': after.get('nReturned')}
        ]
    return dt

@dash.callback(
    Output(component_id='bar_chart', component_property='figure'),
    Input(component_id='benchmark-dropdown', component_property='value')
)
def update_bar_chart(input_value):
    if input_value == 'hashed':
        data = load_benchmark('../results/benchmarking/compound_index_2025-11-24_12-23-33.json')
    elif input_value == 'compound':
        data = load_benchmark('../results/benchmarking/hashed_index_2025-11-27_11-46-38.json')
    elif input_value == 'simple':
        data = load_benchmark('../results/benchmarking/hashed_index_2025-11-24_12-12-50.json')
    before = data['results']['before']
    after = data['results']['after']
    return build_bar_chart(before,after)


@dash.callback(
    Output(component_id='donut_chart', component_property='figure'),
    Input(component_id='benchmark-dropdown', component_property='value')
)
def update_donut_chart(input_value):
    if input_value == 'hashed':
        data = load_benchmark('../results/benchmarking/compound_index_2025-11-24_12-23-33.json')
    elif input_value == 'compound':
        data = load_benchmark('../results/benchmarking/hashed_index_2025-11-27_11-46-38.json')
    elif input_value == 'simple':
        data = load_benchmark('../results/benchmarking/hashed_index_2025-11-24_12-12-50.json')
    before = data['results']['before']
    after = data['results']['after']
    return build_double_donut_chart(before,after)


# Afficher / cacher le FIND builder
@dash.callback(
    Output("query-preview", "value"),
    Input("benchmark-dropdown", "value")
)
def update_preview(selected_benchmark):
    return BENCHMARK_QUERIES.get(selected_benchmark, "")


# Afficher les options de tri
@dash.callback(
    Output("sort-options", "children"),
    Input("sort-check", "value")
)
def toggle_sort(enabled):
    if enabled and "yes" in enabled:
        return html.Div([

            html.Div([

                html.Div([
                    html.Label("Sort field:", className="form-label"),
                    dcc.Dropdown(
                        id="sort-field",
                        options=FIELDS,
                        placeholder="Select...",
                        className="form-input"
                    )
                ], className="form-row-inline"),

                html.Div([
                    html.Label("Order:", className="form-label"),
                    dcc.Dropdown(
                        id="sort-order",
                        options=[
                            {"label": "Ascending (1)", "value": 1},
                            {"label": "Descending (-1)", "value": -1}
                        ],
                        placeholder="Select...",
                        className="form-input"
                    )
                ], className="form-row-inline"),

            ], className="form-inline-container")

        ])
    return []

@dash.callback(
    Output("builder-container", "style"),
    Input("mode-radio", "value")
)
def toggle_builder_container(mode):
    if mode == "find":
        return {"display": "flex", "gap": "20px", "marginTop": "20px"}
    return {"display": "none"}

ROW_STYLE = {
    "display": "flex",
    "flexDirection": "row",
    "alignItems": "center",
    "gap": "20px",
    "marginBottom": "15px"
}

COL_STYLE = {"display": "flex", "flexDirection": "column"}

@dash.callback(
    Output("index-builder", "children"),
    Input("benchmark-dropdown", "value")
)
def show_index_builder(selected_index):

    # --- Simple Index ---
    if selected_index == "simple":
        return html.Div([
            html.H4("Create a Simple Index"),

            html.Div([
                html.Div([
                    html.Label("Field name:"),
                    dcc.Dropdown(
                        id="simple-index-field",
                        options=FIELDS,
                        placeholder="Select field",
                        style={"width": "250px"}
                    )
                ], style=COL_STYLE),

                html.Div([
                    html.Label("Order:"),
                    dcc.Dropdown(
                        id="simple-index-order",
                        options=[
                            {"label": "Ascending (1)", "value": 1},
                            {"label": "Descending (-1)", "value": -1}
                        ],
                        placeholder="Select order",
                        style={"width": "200px"}
                    )
                ], style=COL_STYLE),

            ], style=ROW_STYLE)

        ], style={"padding": "10px"})

    # --- Compound Index ---
    if selected_index == "compound":
        return html.Div([
            html.H4("Create a Compound Index"),

            # FIRST ROW
            html.Div([
                html.Div([
                    html.Label("Field 1:"),
                    dcc.Dropdown(
                        id="cmp-field1",
                        options=FIELDS,
                        placeholder="Select field 1",
                        style={"width": "250px"}
                    )
                ], style=COL_STYLE),

                html.Div([
                    html.Label("Order 1:"),
                    dcc.Dropdown(
                        id="cmp-order1",
                        options=[
                            {"label": "Ascending (1)", "value": 1},
                            {"label": "Descending (-1)", "value": -1}
                        ],
                        placeholder="Order",
                        style={"width": "200px"}
                    )
                ], style=COL_STYLE),
            ], style=ROW_STYLE),

            # SECOND ROW
            html.Div([
                html.Div([
                    html.Label("Field 2:"),
                    dcc.Dropdown(
                        id="cmp-field2",
                        options=FIELDS,
                        placeholder="Select field 2",
                        style={"width": "250px"}
                    )
                ], style=COL_STYLE),

                html.Div([
                    html.Label("Order 2:"),
                    dcc.Dropdown(
                        id="cmp-order2",
                        options=[
                            {"label": "Ascending (1)", "value": 1},
                            {"label": "Descending (-1)", "value": -1}
                        ],
                        placeholder="Order",
                        style={"width": "200px"}
                    )
                ], style=COL_STYLE),
            ], style=ROW_STYLE)

        ], style={"padding": "10px"})

    # --- Hashed Index ---
    if selected_index == "hashed":
        return html.Div([
            html.H4("Create a Hashed Index"),

            html.Div([
                html.Div([
                    html.Label("Field name:"),
                    dcc.Dropdown(
                        id="hashed-index-field",
                        options=FIELDS,
                        placeholder="Select field",
                        style={"width": "250px"}
                    )
                ], style=COL_STYLE),

                html.Div([
                    html.Label("Index type:"),
                    dcc.Input(
                        value="hashed",
                        disabled=True,
                        style={"width": "150px", "background": "#eee"}
                    )
                ], style=COL_STYLE),
            ], style=ROW_STYLE)

        ], style={"padding": "10px"})

    # Default
    return html.Div("Select an index type.")


# ============================================
# 5. Callback pour charger et afficher le fichier JSON sélectionné
# ============================================

@dash.callback(
    Output("benchmark-content", "children"),
    Input("benchmark-dropdown", "value")
)
def update_benchmark_display(selection):
    if not selection:
        return html.Div("Select a benchmark to display results.", className="card")

    file_path = f"data/sample_benchmark.json"  # tu remplaceras par ton vrai chemin
    data = load_benchmark(file_path)

    before = data["results"]["before"]
    after = data["results"]["after"]

    return html.Div([

        html.Div([
            html.H3(f"Index benchmark: {data['index_name']}"),
            html.Span(f"Index: {after.get('indexName', 'N/A')}",
                      className="badge-info")
        ], className="card"),

        # KPIs
        html.Div([
            make_kpi_card("Execution Time", before["executionTimeMillis"], after["executionTimeMillis"], "ms"),
            make_kpi_card("Docs Examined", before["totalDocsExamined"], after["totalDocsExamined"]),
            make_kpi_card("Keys Examined", before["totalKeysExamined"], after["totalKeysExamined"])
        ], className="grid-3"),

        # Charts
        html.Div([
            dcc.Graph(figure=make_comparison_bar(before, after, "executionTimeMillis", "Execution Time")),
            dcc.Graph(figure=make_comparison_bar(before, after, "totalDocsExamined", "Documents Examined")),
        ], className="grid-2"),

        # Explain Plan
        html.Div([
            html.H3("Explain Plan"),
            html.Pre(json.dumps(before["executionStages"], indent=2)),
            html.Hr(),
            html.Pre(json.dumps(after["executionStages"], indent=2))
        ], className="card")

    ])



# ============================================
# FIN DU FICHIER
# ============================================
