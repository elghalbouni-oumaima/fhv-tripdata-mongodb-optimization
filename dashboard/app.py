
import dash
from dash import html, dcc

# Initialisation
app = dash.Dash(__name__, use_pages=True,suppress_callback_exceptions=True)
server = app.server

# Layout Principal
app.layout = html.Div([
    # Navbar
    html.Nav([
        dcc.Link("DashBoard", href="/", className="nav-title"),
        html.Div([
            dcc.Link("Dataset", href="/", className="nav-link"),
            dcc.Link("Slow Queries Monitor", href="/slow-queries-monitor", className="nav-link"),
            dcc.Link("Performance", href="/performance", className="nav-link"),
        ])
    ], className="navbar"),
    
    # Contenu de la page
    html.Div([
        dash.page_container
    ], className="page-container")
])

if __name__ == '__main__':
    app.run(debug=True)
