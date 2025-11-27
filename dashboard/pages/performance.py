import dash
from dash import html, dcc, dash_table, Input, Output, State, ctx
import pandas as pd
from utils.loader import load_benchmark
from utils.charts import make_comparison_bar, make_kpi_card
import json

dash.register_page(__name__, path="/performance", name="Performance")


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
        ], style={"flex": "1", "marginRight": "20px"}),

        # RIGHT SIDE → Benchmark selector
        html.Div([
            html.Label("Choose a predefined benchmark:"),
            dcc.Dropdown(
                id="benchmark-dropdown",
                options=[
                    {"label": "Simple Index Query", "value": "simple"},
                    {"label": "Compound Index Query", "value": "compound"},
                    {"label": "Hashed Index Query", "value": "hashed"},
                ],
                value="simple"
            )
        ], style={"flex": "1"}),

    ], style={
        "display": "flex",
        "gap": "20px",
        "alignItems": "center",
        "marginBottom": "20px"
    }),

    # Find Builder
    html.Div(id="find-builder", children=[

        # Field
        html.Div([
            html.Label("Field:"),
            dcc.Dropdown(id="find-field", options=FIELDS, style={"width": "30%"})
        ], style={"display": "inline-block", "marginRight": "1rem"}),

        # Value
        html.Div([
            html.Label("Value:"),
            dcc.Input(id="find-value", type="text", style={"width": "150px"})
        ], style={"display": "inline-block", "marginRight": "1rem"}),

        # Sort enable
        html.Div([
            html.Label("Sort results?"),
            dcc.Checklist(
                id="sort-check",
                options=[{"label": "Enable sort()", "value": "yes"}],
                inline=True
            )
        ], style={"marginTop": "1rem"}),

        html.Div(id="sort-options", children=[], style={"marginTop": "1rem"}),

        html.Button(
            "Search",
            id="search-btn",
            className="card",
            style={"padding": "8px 20px", "marginTop": "1rem"}
        ),

    ], className="card"),

], className="card")



# ============================================
# 3. Layout principal
# ============================================

layout = html.Div([
    html.H2("Performance & Index Benchmark Visualization"),

    query_controls,  # <-- ajouté ici

    html.Br(),

    html.Div(id="benchmark-content")
])



# ============================================
# 4. Callbacks
# ============================================

# Afficher / cacher le FIND builder
@dash.callback(
    Output("find-builder", "style"),
    Input("mode-radio", "value")
)
def toggle_find_builder(mode):
    return {"display": "block"} if mode == "find" else {"display": "none"}


# Afficher les options de tri
@dash.callback(
    Output("sort-options", "children"),
    Input("sort-check", "value")
)
def toggle_sort(enabled):
    if enabled and "yes" in enabled:
        return html.Div([
            html.Label("Sort field:"),
            dcc.Dropdown(id="sort-field", options=FIELDS, style={"width": "40%"}),

            html.Br(),

            html.Label("Order:"),
            dcc.Dropdown(
                id="sort-order",
                options=[
                    {"label": "Ascending (1)", "value": 1},
                    {"label": "Descending (-1)", "value": -1}
                ],
                style={"width": "20%"}
            )
        ])
    return []


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
