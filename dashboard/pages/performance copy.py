
import dash
from dash import html, dcc, dash_table
import pandas as pd
from utils.loader import load_benchmark
from utils.charts import  make_kpi_card,build_double_donut_chart,build_bar_chart

dash.register_page(__name__, path='/performance', name='Performance')

# Chargement
data = load_benchmark('../results/benchmarking/hashed_index_2025-11-24_12-12-50.json')
before = data['results']['before']
after = data['results']['after']

# Helper pour Explain Tree
def generate_tree_html(stage_info):
    # Fonction récursive simple ou statique pour l'exemple
    if not stage_info: return html.Div("Pas de données de stage")
    
    nodes = []
    
    # Simplification : on parcourt juste la racine et inputStage si présent
    current = stage_info
    while current:
        name = current.get('stage', 'UNKNOWN')
        details = current.get('indexName', '')
        nodes.append(html.Div([
            html.Div(name, style={'fontSize': '1.2rem'}),
            html.Div(details, style={'fontSize': '0.8rem', 'color': '#7f8c8d'})
        ], className="tree-node"))
        
        if 'inputStage' in current:
            nodes.append(html.Div("↑", className="tree-arrow"))
            current = current['inputStage']
        else:
            current = None
            
    return html.Div(list(reversed(nodes))) # On inverse pour avoir la feuille en bas ou haut selon préférence

layout = html.Div([
    html.H2(f"Benchmark Index : {data.get('index_name', 'N/A')}"),
    
    # Badges
    html.Div([
        html.Span(f"Index: {after.get('indexName', 'N/A')}", className="badge-info"),
        html.Span(f"Time Optimization: {before.get('executionTimeMillis', 0) - after.get('executionTimeMillis', 0)} ms", className="badge-info"),
    ], className="card"),
    
    # KPI Cards
    html.Div([
        make_kpi_card("Execution Time", before.get('executionTimeMillis'), after.get('executionTimeMillis'), "ms"),
        make_kpi_card("Docs Examined", before.get('totalDocsExamined'), after.get('totalDocsExamined')),
        make_kpi_card("Keys Examined", before.get('totalKeysExamined'), after.get('totalKeysExamined')),
    ], className="grid-3"),
    
    # Comparaison Graphique & Table
    html.Div([
        html.Div([
            html.H3("Performance Metrics Comparison (Before vs After Index)"),
            #dcc.Graph(figure=make_comparison_bar(before, after, 'executionTimeMillis', "Temps d'exécution (ms)")),
            dcc.Graph(figure=build_bar_chart(),style={'width': '100%'}),
        ], className="card"),
        
        html.Div([
            html.H3("Documents and Keys Examined"),
            html.Div([
                dcc.Graph(figure=build_double_donut_chart(),style={'width': '100%'}),
            ],className="donut-card")
           
        ],className="card"),

        # html.Div([
        #     html.H3("Comparaison Visuelle"),
        #     dcc.Graph(figure=make_comparison_bar(before, after, 'totalDocsExamined', "Documents Examinés"))
        # ], className="card"),
        
        
    ], className="grid-2"),
    html.Div([
            html.H3("Détails Chiffrés"),
            #dcc.Graph(figure=make_comparison_bar(before, after, 'totalDocsExamined', "Documents Examinés")),
            dash_table.DataTable(
                data=[
                    {'Metric': 'Time (ms)', 'Before': before.get('executionTimeMillis'), 'After': after.get('executionTimeMillis')},
                    {'Metric': 'Docs Examined', 'Before': before.get('totalDocsExamined'), 'After': after.get('totalDocsExamined')},
                    {'Metric': 'Keys Examined', 'Before': before.get('totalKeysExamined'), 'After': after.get('totalKeysExamined')},
                    {'Metric': 'nReturned', 'Before': before.get('nReturned'), 'After': after.get('nReturned')}
                ],
                style_cell={'textAlign': 'left', 'padding': '10px'},
                style_header={'backgroundColor': '#ecf0f1', 'fontWeight': 'bold'},
                style_as_list_view=True
            )
    ], className="card"),
    
    # Explain Tree
    html.Div([
        html.H3("Explain Plan (Structure des Stages)"),
        html.Div([
            html.Div([
                html.H4("BEFORE (CollScan)"),
                generate_tree_html(before.get('executionStages'))
            ], style={'flex': 1}),
             html.Div([
                html.H4("AFTER (IndexScan)"),
                generate_tree_html(after.get('executionStages'))
            ], style={'flex': 1})
        ], style={'display': 'flex', 'justifyContent': 'space-around'})
    ], className="card")
])
