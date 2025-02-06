from api import ArcGISFetcher
import pandas as pd

# Import your original health data
health_data = pd.read_csv("C:\\Users\\rigor\\OneDrive\\Desktop\\202553ee-f06a-4109-820b-c2b548bddedc.csv")

#test fetcher
fetcher = ArcGISFetcher()

#Test raw data fetch
#arc_data = fetcher.get_gateway_patients()
'''This works because ArcGIS returns data in this format:
{
    "features": [
        {"attributes": {"field1": "value1", "field2": "value2"}},
        {"attributes": {"field1": "value3", "field2": "value4"}}
    ]
}
# For simple list of dictionaries
data = [
    {"name": "John", "age": 30},
    {"name": "Jane", "age": 25}
]
df = pd.DataFrame(data)

# For nested JSON
data = {
    "users": [
        {"info": {"name": "John", "age": 30}},
        {"info": {"name": "Jane", "age": 25}}
    ]
}
df = pd.DataFrame([user['info'] for user in data['users']])

# For complex nested structures
def flatten_json(nested_json):
    flat_data = []
    for record in nested_json:
        flat_record = {}
        for key, value in record.items():
            if isinstance(value, dict):
                for sub_key, sub_value in value.items():
                    flat_record[f"{key}_{sub_key}"] = sub_value
            else:
                flat_record[key] = value
        flat_data.append(flat_record)
    return pd.DataFrame(flat_data)'''
#arc_df = pd.DataFrame([f['attributes'] for f in arc_data['features']])

#Basic stats
##print("ArcGIS Analysis")
#print("----------------")
#print(f'Number of records: {len(arc_df)}')
#for column in arc_df.columns:
    #print(f'\n{column}')
    #print(arc_df[column].describe())
    #print('Missing Values:', arc_df[column].isnull().sum())

#arc_df.to_csv('gateway_patients.csv', index=False)

#if raw_data:
   # print("\nFeatures retrieved:", len(raw_data.get('features', [])))

# Test the merge function
#merged_data = fetcher.merge_with_health_data(health_data)

#if merged_data is not None:
   # print("\nMerged Data Shape:", merged_data.shape)
#test with health data
#if raw_data:
    #merged = fetcher.merge_with_health_data(health_data)

census_data = fetcher.get_census()
census_df = pd.DataFrame([f['attributes'] for f in census_data['features']])
#census_df.to_csv('census.csv', index=False)
print(f'Census Data Columns:{census_df.columns}')
print(census_df.describe())
#for column in census_df:
    #print(f'/n{census_df[column].describe()}')


#gatewayvisits_data = fetcher.get_gateway_visits()
#gatewayvisits_df = pd.DataFrame([f['attributes'] for f in gatewayvisits_data['features']])
#gatewayvisits_df.to_csv('gateway_visits.csv', index=False) 
print(f'Health Data Columns:{health_data.columns}')
print(health_data.describe())
#for column in health_data:
    #print(f'/n{health_data[column].describe()}')



new_gateway_data = fetcher.get_gateway_data()
new_gateway_data_df = pd.DataFrame([f['attributes'] for f in new_gateway_data['features']])
print(f'Gateway Data Columns:{census_df.columns}')
print(new_gateway_data_df.describe())
#for column in new_gateway_data_df:
    #print(f'/n{new_gateway_data_df[column].describe()}')

#print(arc_df.columns)
print(census_df.columns)
#print(gatewayvisits_df.columns)