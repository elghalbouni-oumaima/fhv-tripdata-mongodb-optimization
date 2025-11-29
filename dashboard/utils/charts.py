import plotly.express as px
import plotly.graph_objects as go
from dash import html
import pandas as pd
from plotly.subplots import make_subplots



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




# def build_donut_chart():
#     # Shared labels
#     labels = ["Jan", "Feb", "Mar"]

#     # Different values for each donut
#     before_values = [20, 35, 30]
#     after_values = [30, 25, 45]

#     # Create subplot with 1 row and 2 columns, both donut style
#     fig = make_subplots(
#         rows=1, cols=2,
#         specs=[[{'type':'domain'}, {'type':'domain'}]],
#         subplot_titles=("Before Index", "After Index")
#     )

#     # Donut 1
#     fig.add_trace(
#         go.Pie(
#             labels=labels,
#             values=before_values,
#             hole=0.5,
#             name="Before"
#         ),
#         row=1, col=1
#     )

#     # Donut 2
#     fig.add_trace(
#         go.Pie(
#             labels=labels,
#             values=after_values,
#             hole=0.5,
#             name="After"
#         ),
#         row=1, col=2
#     )

#     fig.update_layout(
#         title_text="Comparison Donut Charts",
#         legend_title="Months",
#         showlegend=True
#     )

#     return fig



import plotly.graph_objects as go
from plotly.subplots import make_subplots

# def build_double_donut_chart():
#     # Shared Labels
#     labels = ["Metric A", "Metric B", "Metric C"]

#     # Different Values
#     before = [40, 30, 30]
#     after = [25, 50, 25]

#     # Create subplot (1 row, 2 columns)
#     fig = make_subplots(
#         rows=1, cols=2,
#         specs=[[{"type": "domain"}, {"type": "domain"}]],
#         subplot_titles=("Before Index", "After Index")
#     )

#     # First donut
#     fig.add_trace(go.Pie(
#         labels=labels,
#         values=before,
#         hole=0.5,
#         name="Before"
#     ), row=1, col=1)

#     # Second donut
#     fig.add_trace(go.Pie(
#         labels=labels,
#         values=after,
#         hole=0.5,
#         name="After"
#     ), row=1, col=2)

#     # Shared legend + nicer style
#     fig.update_layout(
#         legend_title="Metrics",
#         showlegend=True
#     )

#     return fig



def build_double_donut_chart():
    labels = ["totalKeysExamined", "totalDocsExamined", "nReturned"]

    before_values = [20, 35, 30]
    after_values = [30, 25, 45]

    fig = go.Figure()

    # Donut 1: Before Index
    fig.add_trace(go.Pie(
        labels=labels,
        values=before_values,
        name="Before Index",
        hole=0.55,
        domain={'x': [0, 0.45]},  # left position
        textinfo="percent"
    ))

    # Donut 2: After Index
    fig.add_trace(go.Pie(
        labels=labels,
        values=after_values,
        name="After Index",
        hole=0.55,
        domain={'x': [0.55, 1]},  # right position
        textinfo="percent"
    ))

    fig.update_layout(
        
        # legend
        legend_title="Categories",
        showlegend=True,

        # Legend position
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=-0.15,
            xanchor="center",
            x=0.5,
            title_text=""
        )
    )
    fig.update_layout(
        width=500,   # width in pixels
        height=450,  # height in pixels
        legend_title="Metrics",
        showlegend=True,
        margin=dict(t=0, l=0, r=0, b=0), # control whitespace
        title_text=""
    )

    # Titles above each donut
    fig.add_annotation(x=0.22, y=1.1, text="Before Index", showarrow=False, font=dict(size=14))
    fig.add_annotation(x=0.78, y=1.1, text="After Index", showarrow=False, font=dict(size=14))

    return fig

# def build_donut_charts():
#     labels = ["Category A", "Category B", "Category C"]

#     # Before value distribution
#     values_before = [50, 30, 20]
#     fig_before = px.pie(
#         values=values_before,
#         hole=0.5,  # Donut style
#         title="Before Index"
#     )

#     # After value distribution
#     values_after = [30, 45, 25]
#     fig_after = px.pie(
#         values=values_after,
#         hole=0.5,
#         title="After Index"
#     )

#     fig_before.update_layout(legend_title=None)
#     fig_after.update_layout(legend_title=None)

#     return fig_before, fig_after


def build_bar_chart():
    data = {
        "": [
            "works",
            "needTime",
            "executionTimeMillis",
            "optimizationTimeMillis"
        ],
        "Before Index": [100, 250, 60, 40],
        "After Index": [50, 150, 30, 20]
    }

    df = pd.DataFrame(data)

    fig = px.bar(
        df,
        x=["Before Index", "After Index"],
        y="",
        barmode="group",
        orientation="h",
    )

    fig.update_layout(
        # height=350,               # control height
        # bargap=0.25,              # reduce spacing between groups
        # bargroupgap=0.05,         # reduce spacing inside group
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=-0.25,              # push legend further down
            xanchor="center",
            x=0.5,
            title_text=""
        ),
        width=1100, 
        xaxis_title="",
    )

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