import pandas as pd
import os

data_dir = os.path.join(os.path.dirname(__file__), 'data')
health_data = pd.read_csv(os.path.join(data_dir, 'health_data.csv'))
census_data = pd.read_csv(os.path.join(data_dir, 'census.csv'))
gateway_data = pd.read_csv(os.path.join(data_dir, 'new_gateway_data.csv'))

def analyze_numeric_columns(df):
    """Analyze numeric columns that might represent the same data"""
    visit_columns = ['HD_Visits', 'Ct_Vst', 'Ct_Vst_Lar', 'Ct_Pts']
    population_columns = ['Count_', 'Population', 'Total_HHs']
    area_columns = ['Shape_Area', 'Shape__Area']

    print("\nVisit-related columns:")
    print("-" * 50)
    for col in visit_columns:
        if col in df.columns:
            print(f"\n{col} statistics:")
            print(df[col].describe())

    # Print correlations between visit columns that exist
    existing_visit_cols = [col for col in visit_columns if col in df.columns]
    if len(existing_visit_cols) > 1:
        print("\nVisit columns correlation:")
        correlation_matrix = df[existing_visit_cols].corr()
        print(correlation_matrix)

    print("\nArea-related columns correlation:")
    print(df[['Shape_Area', 'Shape_Area']].corr())

def analyze_location_columns(df):
    """Analyze location identifier columns"""
    location_columns = ['GEOID10', 'Geography', 'NAMELSAD10']
    
    print("\nLocation columns sample:")
    for col in location_columns:
        if col in df.columns:
            print(f"\n{col} first 5 values:")
            print(df[col].head())


def process_data():
    #Use relative paths
    #data_dir = os.path.join(os.path.dirname(__file__), 'data')

    #health_data = pd.read_csv(os.path.join(data_dir, 'health_data.csv'))
    #census_data = pd.read_csv(os.path.join(data_dir, 'census.csv'))
    #gateway_data = pd.read_csv(os.path.join(data_dir, 'new_gateway_data.csv'))
    

    # Print shapes for debugging
    print("Original shapes:")
    print(f"Health data: {health_data.shape}")
    print(f"Census data: {census_data.shape}")
    print(f"Visits data: {gateway_data.shape}")

    # Before merging, analyze columns
    print("Analyzing original health data:")
    analyze_numeric_columns(health_data)
    
    print("\nAnalyzing visits data:")
    analyze_numeric_columns(gateway_data)

    # Census columns (primary source for demographics)
    census_cols = [
        'GEOID10',  # Primary key for merging
        'Median_Inc', 'Population', 'Total_HHs', 'Total_Fami',
        'Fam_Avg_Si', 'Fam_Marrie', 'Fam_Single', 'Fam_Sing_1', 'Total_NonF',
        'NonFam_Avg', 'Fam_Sing_2', 'Fam_Sing_3', 'POV_Famili', 'POV_HH',
        'POV_Marrie', 'POV_Single', 'POV_Sing_1', 'POV_Sing_2', 'POV_Sing_3',
        'Pov_Sing_4', 'POV_Fami_1', 'POV_Fami_2', 'POV_HH_Abo', 'Emp_Popula',
        'Emp_Labor_', 'Emp_Not_La', 'Emp_Employ', 'Emp_Unempl', 'Emp_Unem_1',
        'Ed_Populat', 'Ed_Pop_Mal', 'Ed_Male_Co', 'Ed_Pop_Fem', 'Ed_Female_',
        'Ed_Total_C', 'Ed_Total_1', 'Ed_At_Leas', 'Ed_HS_or_H', 
        'education_total_pct'
    ]
    # Health data columns
    health_cols = [
        'GEOID10',
        'HD_Visits',
        'Sum_Age',
        'AvgAge',
        'Diabetes_P',
        'Count_'
    ]
    
    # Gateway columns (only unique/healthcare-specific ones)
    gateway_cols = [
        'GEOID10',
        'Estimate_T',
        'Ct_Vst_Dia',
        'Ct_Vst',        # Add this
        'Ct_Vst_Lar',    # Add this
        'Ct_Pts',     
        'STATEFP10',
        'COUNTYFP10',
        'TRACTCE10',
        'BLKGRPCE10',
        'NAMELSAD10',
        'ALAND10',
        'AWATER10',
        'INTPTLAT10',
        'INTPTLON10'
        #'Exp_Single',
        #'Exp_Sing_1',
        #'Exp_Sing_2',
        #'Exp_Sing_3'
    ]

    #create new DataFrame
    census_subset = census_data[census_cols].copy()
    health_subset = health_data[health_cols].copy()
    gateway_subset = gateway_data[gateway_cols].copy()

    print('Starting to merge.....')
    print(f"Initial shapes - Census: {census_subset.shape}, Health: {health_subset.shape}, Gateway: {gateway_subset.shape}")

    #merge census with health data
    merged_df = census_subset.merge(
        health_subset,
        on='GEOID10',
        how='outer',
        indicator=True,
        suffixes=('', '_health')
    )
    print(f"\nAfter first merge: {merged_df.shape}")
    print("Merge indicator counts:")
    print(merged_df['_merge'].value_counts())

     # Drop the _merge column before the second merge
    merged_df = merged_df.drop(columns=['_merge'])

    #then merge with gateway data
    final_df = merged_df.merge(
        gateway_subset,
        on='GEOID10',
        how='outer',
        indicator=True,
        suffixes=('', '_gateway')
    )
    print(f"\nAfter second merge: {final_df.shape}")
    print("Final merge indicator counts:")
    print(final_df['_merge'].value_counts())

    # Add validation of visit counts
    print("\nValidating visit counts across datasets:")
    if 'HD_Visits' in final_df.columns and 'Ct_Vst' in final_df.columns:
        print("\nVisit count summary:")
        print("Health Data Visits (HD_Visits):")
        print(final_df['HD_Visits'].describe())
        print("\nGateway Visits (Ct_Vst):")
        print(final_df['Ct_Vst'].describe())
    
    return final_df
    
    
   

def standardized_visit_data(df):
    print('\nVisit Data Comparison:')
    print(f'HD_Visits range: {df['HD_Visits'].min()} - {df['HD_Visits'].max()}')
    print(f'CT_Vst range: {df['Ct_Vst'].min()} - {df['Ct_Vst'].max()}')

    #Calculate correlation
    correlation = df["HD_Visits"].corr(df['Ct_Vst'])
    print(f'Correlation between visits metrics: {correlation}')



#test processing py
if __name__ == '__main__':
    df = process_data()
    # For debugging, add this after running process_data():
    #print("\nColumn names in each dataset:")
    #print("\nCensus columns:", census_data.columns.tolist())
    #print("\nHealth columns:", health_data.columns.tolist())
    #print("\nGateway columns:", gateway_data.columns.tolist())
    print(df.columns.tolist())
    