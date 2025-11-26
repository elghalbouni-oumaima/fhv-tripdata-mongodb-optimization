import dash
from dash import dcc, html, Input, Output, State, dash_table
import dash_bootstrap_components as dbc
import plotly.express as px
import pandas as pd

# Initialize the App with a Bootstrap Theme (This replaces the DDK styling engine)
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.FLATLY])
server = app.server

# --- DATA PREPARATION ---
df = pd.read_csv('https://raw.githubusercontent.com/mcgovernplotly/DinoDashboard/main/DinoData.csv')

Period_list = list(df["Period"].unique())
Period_list.sort()
Type_list = list(df['Type'].unique())
Type_list.sort()

# --- LAYOUT ---
# We use dbc.Container instead of ddk.App
layout = dbc.Container([
    
    # 1. Header Section (Replaces ddk.Header)
    dbc.Row([
        dbc.Col([
            # Using a Flexbox layout to align logo and text
            html.Div([
                # Note: Ensure 'assets/trex.png' exists, or this alt text will show
                html.Img(src=app.get_asset_url('trex.png'), style={'height': '60px', 'marginRight': '15px'}),
                html.H1("Dino Fossil Data", style={'display': 'inline-block', 'verticalAlign': 'middle'})
            ], style={'display': 'flex', 'alignItems': 'center', 'justifyContent': 'center'})
        ], width=12)
    ], className="mb-4 mt-3"), # 'mb-4' adds margin-bottom, 'mt-3' adds margin-top

    # 2. Controls Section
    dbc.Row([
        # We center the card by using an empty column or justify_content on the Row
        dbc.Col([
            dbc.Card([
                dbc.CardHeader("Filter Data", className="bg-primary text-white"),
                dbc.CardBody([
                    html.Label('Dinosaur Type', className="h5 text-center d-block"),
                    dcc.Dropdown(
                        id='dinotype',
                        options=[{"label": i, "value": i} for i in Type_list],
                        multi=True,
                        value=Type_list,
                        clearable=True,
                        searchable=True,
                        className="mb-3"
                    ),
                    
                    html.Label("Select Dino Name", className="h5 text-center d-block"),
                    dcc.Dropdown(
                        id="name_dropdown",
                        # Populating options based on the whole DF initially
                        options=[{"label": i, "value": i} for i in sorted(df['Name'].unique())],
                        value="Segisaurus",
                        clearable=True,
                        searchable=True,
                    ),
                ])
            ], className="shadow") # 'shadow' adds a nice DDK-style depth
        ], width={"size": 6, "offset": 3}), # This centers the column (size 6) in the middle
    ], className="mb-4"),

    # 3. Output Section (Image) (Replaces ddk.Block)
    dbc.Row([
        dbc.Col([
            html.Div(id='image_placeholder', style={'textAlign': 'center'})
        ], width=12)
    ])

], fluid=True) # fluid=True makes the app stretch to full width like DDK

# --- CALLBACKS ---

# Callback to update the Image based on Name Selection
@app.callback(
    Output('image_placeholder', 'children'),
    Input('name_dropdown', 'value')
)
def display_cover(selected_dino):
    if not selected_dino:
        return html.Div("Please select a dinosaur.")
    
    # Get the link for the selected dinosaur
    dino_data = df[df['Name'] == selected_dino]
    
    if dino_data.empty:
        return html.Div("No data found for this dinosaur.")
    
    image_url = dino_data.iloc[0]['Link']
    
    # Return a styled image
    return html.Img(
        src=image_url,
        style={
            'maxHeight': '400px',
            'maxWidth': '100%',
            'border': '2px solid #ddd',
            'borderRadius': '10px',
            'padding': '5px'
        }
    )

if __name__ == "__main__":
    app.run(debug=True)