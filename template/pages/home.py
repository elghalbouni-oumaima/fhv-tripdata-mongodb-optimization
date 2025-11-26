import dash
from dash import dcc, html, Input, Output, State
import dash_bootstrap_components as dbc
import plotly.express as px
import pandas as pd
import plotly.graph_objects as go

# Initialize App with a modern theme (FLATLY mimics the clean DDK look)
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.FLATLY])
server = app.server

# --- DATA PREPARATION ---
df = pd.read_csv('https://raw.githubusercontent.com/mcgovernplotly/DinoDashboard/main/DinoData.csv')

# Prepare initial lists
Period_list = sorted(list(df["Period"].unique()))
Type_list = sorted(list(df["Type"].unique()))
totalFossilsFounds = len(df)

# --- REUSABLE COMPONENTS ---

def make_card(title, content):
    """Helper to create a styled Card similar to DDK"""
    return dbc.Card([
        dbc.CardHeader(title, className="bg-primary text-white"),
        dbc.CardBody(content)
    ], className="shadow mb-4", style={'height': '100%'})

def make_kpi_card(title, value):
    """Helper to create a DataCard"""
    return dbc.Card([
        dbc.CardHeader(title, className="text-center"),
        dbc.CardBody(
            html.H2(str(value), className="text-center text-primary", style={'fontSize': '3rem'})
        )
    ], className="shadow mb-4")

# --- LAYOUT ---
layout = dbc.Container([
    
    # 1. Header (Replaces ddk.Header)
    dbc.Row([
        dbc.Col([
            html.Div([
                # Ensure 'assets/trex.png' exists for the image to show, otherwise alt text appears
                html.Img(src=app.get_asset_url('trex.png'), style={'height': '50px', 'marginRight': '15px'}),
                html.H2("Dino Fossil Analytics", className="display-6", style={'display': 'inline-block', 'verticalAlign': 'middle'})
            ], className="d-flex align-items-center")
        ], width=12)
    ], className="mb-4 mt-3 border-bottom pb-2"),

    # 2. Main Content Grid
    dbc.Row([
        
        # --- LEFT COLUMN: CONTROLS & KPI ---
        dbc.Col([
            
            # KPI Card (Replaces ddk.DataCard)
            make_kpi_card("Total Fossils Found", totalFossilsFounds),

            # Controls Card
            make_card("Filter Settings", [
                html.Label('Select Period', className="fw-bold"),
                dcc.Dropdown(
                    id='period',
                    options=[{"label": i, "value": i} for i in Period_list],
                    multi=True,
                    value=Period_list,
                    clearable=True,
                    searchable=True,
                    className="mb-3"
                ),
                
                html.Label('Select Dino Type', className="fw-bold"),
                dcc.Dropdown(
                    id='display-type',
                    options=[], # Populated by callback
                    multi=True,
                    value=[],
                    className="mb-3"
                ),
                html.Small("Note: Dino Type options update based on selected Period.", className="text-muted")
            ])
        ], width=12, lg=3), # 3 columns on large screens, full width on mobile

        # --- RIGHT COLUMN: VISUALIZATIONS ---
        dbc.Col([
            
            # Row for Map
            dbc.Row([
                dbc.Col([
                    make_card("Fossil Locations (Global)", 
                        dcc.Graph(id='display-map', style={'height': '400px'})
                    )
                ], width=12)
            ]),

            # Row for Bar Chart
            dbc.Row([
                dbc.Col([
                    make_card("Distribution by Country", 
                        dcc.Graph(id='display-scatter', style={'height': '350px'})
                    )
                ], width=12)
            ])

        ], width=12, lg=9) # 9 columns on large screens

    ])

], fluid=True)

# --- CALLBACKS ---

# 1. Chain Callback: Update Dino Type options based on Period selection
@app.callback(
    Output('display-type', 'options'),
    [Input('period', 'value')],
)
def set_type_options(chosen_period):
    if not chosen_period:
        return []
    dff = df[df['Period'].isin(chosen_period)]
    unique_types = sorted(dff['Type'].unique())
    return [{'label': c, 'value': c} for c in unique_types]

# 2. Chain Callback: Select all Types by default when options change
@app.callback(
    Output('display-type', 'value'),
    Input('display-type', 'options'),
)
def set_type_value(available_options):
    return [x['value'] for x in available_options]

# 3. Main Graph Callback: Update Map and Bar Chart
@app.callback(
    Output('display-scatter', 'figure'),
    Output('display-map', 'figure'),
    Input('display-type', 'value'),
    Input('period', 'value')
)
def update_graph(selected_type, selected_period):
    if not selected_type or not selected_period:
        return dash.no_update, dash.no_update
    
    # Filter Data
    dff = df[(df.Period.isin(selected_period)) & (df.Type.isin(selected_type))]
    
    if dff.empty:
         # Return empty figures if no data
        return {}, {}

    # --- Prepare Map Data ---
    # Group by location to get counts for bubble size
    # We use 'Name' to count occurrences since 'name_old' wasn't in the provided CSV structure
    df_map = dff.groupby(['Latitude', 'Longitude', 'Period', 'Country'], as_index=False)['Name'].count()
    df_map.rename(columns={'Name': 'Count'}, inplace=True)

    # 1. Map Figure
    fig_map = px.scatter_geo(
        df_map, 
        lat='Latitude', 
        lon='Longitude', 
        color="Period", 
        size='Count',
        hover_name="Country",
        projection="orthographic", # The globe view
        title="Fossils Found by Location"
    )
    fig_map.update_layout(margin={"r":0,"t":30,"l":0,"b":0})

    # 2. Bar Chart Figure
    # (The original code called this 'display-scatter' but used px.bar)
    fig_bar = px.bar(
        dff, 
        x='Country',
        color='Period',
        title="Count of Fossils by Country",
        barmode='group'
    )
    fig_bar.update_layout(xaxis={'categoryorder':'total descending'})

    return fig_bar, fig_map

if __name__ == "__main__":
    app.run(debug=True)