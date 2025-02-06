from flask import Flask, redirect, render_template, url_for, jsonify, request
import folium.features
import folium.plugins
import pandas as pd
import folium
import json
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from sklearn.linear_model import LinearRegression
from data_processing import process_data
from visuals import (calculate_stats, create_utilization_charts)

def clean_data(df):
    df['Population'] = df['Population'].fillna(df["Population"].mean())
    df['Ct_Pts'] = df['Ct_Pts'].fillna(df['Ct_Pts'].mean())
    return df

#load the data
df = process_data()
df = clean_data(df)

#Engineered Features#
# Calculate visits per patient
df['visits_per_patient'] = df['Ct_Vst'] / df['Ct_Pts']
# Create meaningful categories
df['family_size_category'] = pd.qcut(df['Fam_Avg_Si'], 
                                   q=4, 
                                   labels=['Small', 'Medium', 'Large', 'Very Large'])
df['income_category'] = pd.qcut(df['Median_Inc'],
                              q=5,
                              labels=['Very Low', 'Low', 'Medium', 'High', 'Very High'])
df['income_quintile'] = pd.qcut(df['Median_Inc'], 5, 
                               labels=['Lowest 20%', 'Lower 20%', 'Middle 20%', 
                                     'Upper 20%', 'Highest 20%'])


def create_overview_charts():
    #move code into functions to be called later on in the separate routes
    # Calculate key statistics
    stats_data = {
    'avg_visits': f"{df['visits_per_patient'].mean():.1f}",
    'median_income': f"${df['Median_Inc'].median():,.0f}",
    'avg_age': f"{df['AvgAge'].mean():.1f}",
    'diabetes_rate': f"{df['Diabetes_P'].mean():.1f}%",
    'total_population': f"{df['Population'].sum():,.0f}"
    }

    #create visualizations

    #1.Folium Map
   # Create interactive map with tooltips
    m = folium.Map(
        location=[27.5, -99.5], 
        zoom_start=10,
        tiles='cartodbpositron'
    )

    # Load GeoJSON
    with open("data/census_blocks.geojson") as f:
        geojson = json.load(f)

   
    # Create the choropleth with the correct column name
    choropleth = folium.Choropleth(
        geo_data=geojson,
        data=df,
        columns=['GEOID10', 'HD_Visits'],  # Using HD_VISITS
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
            fields=['GEOID10', 'HD_Visits', 'AvgAge', 'Diabetes_P', 'Count_'],  # Using HD_VISITS
            aliases=['Area ID:', 'Visits:', 'Average Age:', 'Diabetes Rate (%):', 'Patient Count'],
            style="""
                background-color: white;
                color: #333333;
                font-family: arial;
                font-size: 12px;
                padding: 10px;
                border-radius: 3px;
             box-shadow: 0 1px 2px rgba(0,0,0,0.1);
         """
        )
    )

    # Add interactive controls
    folium.plugins.Fullscreen().add_to(m)
    folium.plugins.MousePosition().add_to(m)

    map_html = m._repr_html_()

   # 1. Visit Type Distribution
    utilization_fig = make_subplots(rows=1, cols=2,
    subplot_titles=('Visit Type Distribution', 'Patient Visit Frequency'))

    # Visit types comparison
    utilization_fig.add_trace(
        go.Bar(
            name='Total Visits',
            x=['Regular Visits', 'Large Facility Visits'],
            y=[df['Ct_Vst'].sum(), df['Ct_Vst_Lar'].sum()],
        ),
        row=1, col=1
    )

    # Visits per patient distribution
    utilization_fig.add_trace(
        go.Histogram(
            x=df['visits_per_patient'],
            name='Visits per Patient'
        ),
        row=1, col=2)
    utilization_fig.update_layout(
        bargap=0.1
    )
    
    utilization_charts = utilization_fig.to_html(full_html=False,
                                                 config={
                                            'displayModeBar': True,
                                            'responsive': True,
                                            'displaylogo': False,
                                            'modeBarButtonsToRemove': ['select2d', 'lasso2d'],
                                            'toImageButtonOptions': {
                                            'format': 'png',
                                            'filename': 'health_utilization',
                                            'height': 500,
                                            'width': 700,
                                            'scale': 2
                                            }
                                        } )
    return utilization_charts, stats_data, map_html

def create_demographic_charts():
    #Continous value so need to
    df['Age_group'] = pd.cut(df['AvgAge'],
                             bins=[0,10,20,30,40,50,60, float('inf')],
                             labels=['0-10', '11-20', '21-30', '31-40','41-50','51-60', '60+'])
    #Healthcare Visist by Age Group
    #Age bar chart
    age_group_sum = df.groupby('Age_group')['Ct_Vst'].sum().reset_index()
    age_visits_fig = px.bar(age_group_sum,
        x='Age_group',
        y='Ct_Vst',
        title='Healthcare Visits by Age Group',
        labels={
        'age_group': 'Age Group',
        'Ct_Vst': 'Average Visits'
    }
)
    age_barchart = age_visits_fig.to_html(full_html=False)

    #Age Bubble chart
    age_visits_fig =px.scatter(df,
                               x='AvgAge',
                               y='Ct_Vst',
                               size='Population',
                               size_max=50,
                               color='Median_Inc',
                               hover_data=['NAMELSAD10'],
                               title='Healthcare Utilization by Age',
                               labels = {
                                   'AvgAge': 'Average Age',
                                   'Ct_Vst': 'Total Visits',
                                   'Median_Inc': 'Median Income ($)',
                                   'NAMELSAD10': 'Geographic Area'
                               })
    age_scatter = age_visits_fig.to_html(full_html=False)

    #Education Level Analisys
    
    # Calculate average visits and income for each education level
    edu_data = (df.groupby('Ed_Total_C')
            .agg({
                'visits_per_patient': 'mean',
                'Median_Inc': 'mean'
            })
            .reset_index())

    # Clean up education level names
    education_mapping = {
    'Total_12th_no_diploma': 'No Diploma',
    'Total_HS_GED': 'High School/GED',
    'Total_5th_and_6th': 'Elementary (5-6th)',
    'Total_7th_and_8th': 'Middle School (7-8th)',
    'Total_9th': '9th Grade',
    'Total_bachelors_degree': "Bachelor's Degree",
    'Total_nursery_to_4th': 'Early Education',
    'Total_Some_college_1_or_more_years_no_degree': 'Some College'
}

    edu_data['Education_Level'] = edu_data['Ed_Total_C'].map(education_mapping)

    # Sort by education progression
    education_order = [
    'Early Education',
    'Elementary (5-6th)',
    'Middle School (7-8th)',
    '9th Grade',
    'No Diploma',
    'High School/GED',
    'Some College',
    "Bachelor's Degree"
]

    edu_data['Education_Level'] = pd.Categorical(
        edu_data['Education_Level'], 
        categories=education_order, 
        ordered=True
    )

# Create bar chart with income shown through color
    edu_visits = px.bar(
        edu_data.sort_values('Education_Level'),
        x='Education_Level',
        y='visits_per_patient',
        color='Median_Inc',  # Color bars by median income
        title='Healthcare Utilization and Income by Education Level',
        labels={
            'Education_Level': 'Education Level',
            'visits_per_patient': 'Average Visits per Patient',
            'Median_Inc': 'Median Income ($)',
            'Count_': 'Patient Count:'
    },
    color_continuous_scale='Viridis'  # Green-yellow color scale
)

    # Update layout
    edu_visits.update_layout(
        height=500,
        width=900,
        title_x=0.5,
        plot_bgcolor='white',
        xaxis_tickangle=-45,
        coloraxis_colorbar_title="Median<br>Income ($)",
    )

    # Update axes
    edu_visits.update_xaxes(title_font=dict(size=12))
    edu_visits.update_yaxes(
    title_font=dict(size=12),
    gridcolor='lightgrey',
    range=[0, max(edu_data['visits_per_patient']) * 1.1]
)
    
    education_html = edu_visits.to_html(full_html=False)

    #Family Size Impact
    # Analyze how family structure affects healthcare usage
    family_analysis = px.scatter(df,
        x='Fam_Avg_Si',  # Average family size
        y='Ct_Vst',
        size=df['Total_Fami'].fillna(df['Total_Fami'].mean()),  # Total families
        color='Median_Inc',  
        hover_data=['POV_Famili'],  # Poverty rate for families
        title='Family Structure and Healthcare Utilization'
    )
    fam_html = family_analysis.to_html(full_html=False)




    return age_barchart, age_scatter, education_html, fam_html

def create_socioeconomic_charts():
    #Healthcare access patterns
    # Create two side-by-side bar charts with error bars to show variation
    income_analysis = make_subplots(rows=1, cols=2,
    subplot_titles=('Patient Distribution by Income Level', 
                   'Healthcare Usage Intensity by Income Level'))

    # First subplot: Patient counts with standard deviation
    income_groups = df.groupby('income_category').agg({
    'Ct_Pts': ['mean', 'std'],
    'visits_per_patient': ['mean', 'std']
    }).reset_index()

    # Patient Distribution
    income_analysis.add_trace(
    go.Bar(
        x=income_groups['income_category'],
        y=income_groups['Ct_Pts']['mean'],
        error_y=dict(
            type='data',
            array=income_groups['Ct_Pts']['std']
        ),
        name='Average Patients'
    ),
    row=1, col=1
    )

    # Healthcare Usage
    income_analysis.add_trace(
    go.Bar(
        x=income_groups['income_category'],
        y=income_groups['visits_per_patient']['mean'],
        error_y=dict(
            type='data',
            array=income_groups['visits_per_patient']['std']
        ),
        name='Visits per Patient',
        marker_color='coral'
    ),
    row=1, col=2
    )

    # Update layout
    income_analysis.update_layout(
        height=500,
        width=1000,
        showlegend=False,
        title_text="Healthcare Access Patterns Across Income Levels"
    )

    # Update axes
    income_analysis.update_yaxes(title_text="Average Number of Patients", row=1, col=1)
    income_analysis.update_yaxes(title_text="Average Visits per Patient", row=1, col=2)
    income_analysis.update_xaxes(title_text="Income Level", row=1, col=1)
    income_analysis.update_xaxes(title_text="Income Level", row=1, col=2)
    
    income_figs = income_analysis.to_html(full_html=False)

    #2. Income Level vs Healthcare Utilization
    income_visits_fig = px.scatter(df,
                        x='Median_Inc',
                        y='Ct_Vst',
                        size='Population',
                        hover_data=['NAMELSAD10', 'Ct_Pts'],
                        title='Healthcare Visits vs Median Income',
                        labels= {
                            'Median_Inc': 'Median Income ($)',
                            'Ct_Vst': 'Total Visits',
                            'Population': 'Population Size'
                        },
                        trendline='ols') #Add trendline to show correlation
    income_visits_chart = income_visits_fig.to_html(full_html=False)

    #Family size and Income
    utilization_patterns = px.bar(
        df.groupby(['family_size_category', 'income_category'])['Ct_Vst'].mean().reset_index(),
        x='family_size_category',
        y='Ct_Vst',
        color='income_category',
        title='Healthcare Usage by Family Size and Income',
        barmode='group'
    )
    up_html = utilization_patterns.to_html(full_html=False)

    #Employment Bubble
    df['employment_rate'] = (df['Emp_Labor_'] / df['Population']) * 100

    employment_bubble = px.scatter(df,
    x='employment_rate',
    y='visits_per_patient',
    size='Population',
    size_max=30,
    color='Median_Inc',
    color_continuous_scale='viridis',
    title='Healthcare Utilization vs Employment Rate',
    labels={
        'employment_rate': 'Employment Rate (%)',
        'visits_per_patient': 'Visits per patient',
        'Population': 'Population Size',
        'Median_Inc': 'Median Income ($)'
    },
    hover_data=['NAMELSAD10', 'Population']
    )
    #Add trendline
    employment_bubble.add_traces(
        px.scatter(df,
        x='employment_rate',
        y='visits_per_patient',
        trendline='ols').data
    )
    # Update layout for better readability
    employment_bubble.update_layout(
        height=600,
        width=900,
        plot_bgcolor='white',
        title_x=0.5,  # Center title
        showlegend=True,
        legend=dict(
        yanchor="top",
        y=0.99,
        xanchor="right",
        x=0.99
        )
    )

    # Update axes
    employment_bubble.update_xaxes(
        title_text="Employment Rate (%)",
        showgrid=True,
        gridwidth=1,
        gridcolor='LightGray',
        range=[15, 65],
        dtick=5
    )

    employment_bubble.update_yaxes(
        title_text="Average Visits per Patient",
        showgrid=True,
        gridwidth=1,
        gridcolor='LightGray',
        range=[2,12],
        dtick=2
    )
    employment_bubble_chart = employment_bubble.to_html(full_html=False)


    return income_figs, income_visits_chart, up_html, employment_bubble_chart

def create_health_outcomes_charts():
    #3, Diabetes Analysis
    diabetes_fig = px.scatter(df,
                    x='Median_Inc',
                    y="Diabetes_P",
                    size='Ct_Pts',
                    color='visits_per_patient',
                    #size_max=50,
                    hover_data=['NAMELSAD10'],
                    title='Diabetes Prevalence vs Income with Healthcare Utilization',
                    labels={
                        'Median_Inc': 'Median Income ($)',
                        'Diabetes_P': 'Diabetes Prevalence (%)',
                        'visits_per_patient': 'Visits per Patient'
                    })
    diabetes_chart = diabetes_fig.to_html(full_html=False)

    # Improved Diabetes Prevalence vs Age visualization
    diabetes_age_fig = px.scatter(df,
        x='AvgAge',
        y='Diabetes_P',
        size='Population',  # Add population size for context
        color='visits_per_patient',
        color_continuous_scale='YlOrRd',  # Yellow to Red scale for better visibility
        hover_data=['NAMELSAD10', 'Median_Inc'],
        title='Diabetes Prevalence by Age with Healthcare Utilization',
        labels={
        'AvgAge': 'Average Age',
        'Diabetes_P': 'Diabetes Prevalence (%)',
        'visits_per_patient': 'Visits per Patient',
        'Median_Inc': 'Median Income ($)'
        }
    )
    # Add trendline
    diabetes_age_fig.add_traces(px.scatter(df, x='AvgAge', y='Diabetes_P', trendline="ols").data)

    diabetes_chart_age = diabetes_age_fig.to_html(full_html=False)

       #Correlation Matrix
    # Create correlation matrix
    # Create education level mapping (numeric values for education levels)
    education_mapping = {
        'Total_nursery_to_4th': 1,
        'Total_5th_and_6th': 2,
        'Total_7th_and_8th': 3,
        'Total_9th': 4,
        'Total_12th_no_diploma': 5,
        'Total_HS_GED': 6,
        'Total_Some_college_1_or_more_years_no_degree': 7,
        'Total_bachelors_degree': 8
}

    # Create new numeric education column
    df['education_numeric'] = df['Ed_Total_C'].map(education_mapping)

    correlation_vars = {
        'Median_Inc': 'Median Income',
        'education_numeric': 'Education Level',
        'AvgAge': 'Average Age',
        'visits_per_patient': 'Visits per Patient',
        'Diabetes_P': 'Diabetes Rate'
    }

    corr_df = df[correlation_vars.keys()].corr()

    # Create heatmap
    corr_matrix = px.imshow(
        corr_df,
        x=list(correlation_vars.values()),
        y=list(correlation_vars.values()),
        color_continuous_scale='RdBu_r',
        aspect='auto',
        title='Correlation Matrix of Key Health Indicators'
    )

    # Update layout
    corr_matrix.update_layout(
        width=700,
        height=600,
        title_x=0.5,
    )

    # Add correlation values as text
    for i in range(len(corr_df.columns)):
        for j in range(len(corr_df.index)):
            corr_matrix.add_annotation(
                x=i,
                y=j,
                text=f"{corr_df.iloc[i, j]:.2f}",
                showarrow=False,
                font=dict(color='black' if abs(corr_df.iloc[i, j]) < 0.7 else 'white')
            )
    corr_html = corr_matrix.to_html(full_html=False)



    return diabetes_chart, diabetes_chart_age, corr_html


app=Flask(__name__)


@app.route('/')
@app.route('/overview')
def index():
    utilization_charts, stats_data, map_html = create_overview_charts()
    return render_template('index.html',
                           stats_data = stats_data,
                           utilization_charts = utilization_charts,
                           map_html = map_html
                           )
                         
    
@app.route('/demographics')
def demographics():
    age_barchart, age_scatter, education_html, fam_html = create_demographic_charts()
    return render_template('demographics.html',
                           age_barchart = age_barchart,
                           age_scatter = age_scatter,
                           education_html = education_html,
                           fam_html = fam_html)

@app.route('/socioeconomic')
def socioeconomic():
    income_figs, income_visits_charts, up_html, employment_bubble_chart = create_socioeconomic_charts()
    return render_template('socioeconomic.html',
                           income_figs = income_figs,
                           income_visits_charts = income_visits_charts,
                           up_html = up_html,
                           employment_bubble_chart = employment_bubble_chart)

@app.route('/health_outcomes')
def health_outcomes():
    diabetes_chart, diabetes_chart_age, corr_html = create_health_outcomes_charts()
    return render_template('health_outcomes.html',
                           diabetes_chart = diabetes_chart,
                           diabetes_chart_age = diabetes_chart_age,
                           corr_html = corr_html)


@app.route('/map')
def view_map():
    return render_template('map.html')

if __name__ == "__main__":
    app.run(debug=True)




