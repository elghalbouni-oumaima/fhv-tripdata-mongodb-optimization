import plotly.express as px
import plotly.graph_objects as go
from dash import html

COLOR_PRIMARY = '#2c3e50'
COLOR_SECONDARY = '#18bc9c'
CHART_HEIGHT = 320 # <-- C'est cette ligne qui empêche le scroll infini

def update_common_layout(fig):
    fig.update_layout(
        paper_bgcolor='rgba(0,0,0,0)', 
        plot_bgcolor='rgba(0,0,0,0)',
        height=CHART_HEIGHT,
        margin=dict(l=20, r=20, t=40, b=20)
    )

def make_histogram(data, column, title):
    fig = px.histogram(data, x=column, title=title, 
                       color_discrete_sequence=[COLOR_PRIMARY])
    update_common_layout(fig)
    return fig

def make_boxplot(data, column, title):
    fig = px.box(data, y=column, title=title,
                 color_discrete_sequence=[COLOR_SECONDARY])
    update_common_layout(fig)
    return fig

def make_heatmap(data, title):
    matrix = data.groupby(['PULocationID', 'DOLocationID']).size().reset_index(name='count')
    pivot = matrix.pivot(index='PULocationID', columns='DOLocationID', values='count').fillna(0)
    fig = px.imshow(pivot, title=title, color_continuous_scale='Viridis')
    update_common_layout(fig)
    return fig

def make_timeline(data, title):
    df_temp = data.copy()
    df_temp['hour'] = df_temp['pickup_datetime'].dt.hour
    counts = df_temp.groupby('hour').size().reset_index(name='trips')
    
    fig = px.line(counts, x='hour', y='trips', title=title, markers=True,
                  line_shape='spline')
    fig.update_traces(line_color=COLOR_PRIMARY, line_width=3)
    update_common_layout(fig)
    return fig

def make_comparison_bar(before, after, metric_key, title):
    val_b = before.get(metric_key, 0)
    val_a = after.get(metric_key, 0)
    
    fig = go.Figure(data=[
        go.Bar(name='Before', x=['Comparaison'], y=[val_b], marker_color='#e74c3c'),
        go.Bar(name='After', x=['Comparaison'], y=[val_a], marker_color='#27ae60')
    ])
    fig.update_layout(barmode='group', title=title)
    update_common_layout(fig)
    return fig

def make_kpi_card(title, before_val, after_val, unit=""):
    diff = after_val - before_val
    diff_pct = (diff / before_val * 100) if before_val != 0 else 0
    color_class = "diff-good" if diff <= 0 else "diff-bad"
    if "Keys" in title and diff > 0: color_class = "diff-good"
    
    return html.Div([
        html.Div(title, className="kpi-title"),
        html.Div(f"{before_val} → {after_val} {unit}", className="kpi-value-main"),
        html.Div(f"{diff:+d} ({diff_pct:.1f}%)", className=f"kpi-diff {color_class}")
    ], className="card kpi-card")