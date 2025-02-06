import pandas as pd
import folium
import json
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots




def calculate_stats(df):
    return{
    'avg_visits': f"{df['visits_per_patient'].mean():.1f}",
    'median_income': f"${df['Median_Inc'].median():,.0f}",
    'avg_age': f"{df['AvgAge'].mean():.1f}",
    'diabetes_rate': f"{df['Diabetes_P'].mean():.1f}%",
    'total_population': f"{df['Population'].sum():.2f}"
    }

def create_utilization_charts(df):
    # 1. Visit Type Distribution
    utilization_fig = make_subplots(rows=1, cols=2,
    subplot_titles=('Visit Type Distribution', 'Patient Visit Frequency'))

    # Visit types comparison
    utilization_fig.add_trace(
        go.Bar(
            name='Total Visits',
            x=['Regular Visits', 'Large Facility Visits'],
            y=[df['Ct_Vst'].sum(), df['Ct_Vst_Lar'].sum()],
            hovertemplate="<b>%{x}</b><br>" +
                            "Visits: %{y:,.0f}<br>" +
                            "<extra></extra>",
        ),
        row=1, col=1
    )

    # Visits per patient distribution
    utilization_fig.add_trace(
        go.Histogram(
            x=df['visits_per_patient'],
            name='Visits per Patient',
            hovertemplate="Visits: %{x}<br>" +
                        "Count: %{y}<br>" +
                        "<extra></extra>"
        ),
        row=1, col=2)
    
    #Update layout for better apperance
    utilization_fig.update_layout(
        height=500,
        showlegend=True,
        legend=dict(
            yanchor="top",
            y=0.99,
            xanchor="left",
            x=0.1,
            bgcolor="rgba(255, 255, 255, 0.8)"
        ),
        margin=dict(l=20, r=20, t=40, b=20),
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)'
    )

    return utilization_fig

def create_interactive_map(df, geojson):
    m = folium.Map(location=[27.5, -99.5], zoom_start=10)
    
    # Add custom controls
    folium.plugins.Fullscreen().add_to(m)
    folium.plugins.MousePosition().add_to(m)
    
    # Add interactive choropleth
    choropleth = folium.Choropleth(
        geo_data=geojson,
        data=df,
        columns=['GEOID10', 'Ct_Vst'],
        key_on='feature.properties.GEOID10',
        fill_color='YlOrRd',
        fill_opacity=0.7,
        line_opacity=0.2,
        legend_name='Health Department Visits',
        highlight=True
    ).add_to(m)
    
    # Add tooltips
    choropleth.geojson.add_child(
        folium.features.GeoJsonTooltip(
            fields=['GEOID10', 'Ct_Vst'],
            aliases=['Area:', 'Visits:'],
            style=('background-color: white; color: #333333; font-family: arial; font-size: 12px; padding: 10px;')
        )
    )
    
    return m



