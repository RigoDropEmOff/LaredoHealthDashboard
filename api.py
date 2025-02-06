import requests
import pandas as pd

#This is a common pattern for organizing API calls
#The class helps encapsulate all API-related functionality
#base_url is stored as an instance variable to avoid repetition
class ArcGISFetcher:
    def __init__(self):
        self.base_url = "https://services3.arcgis.com/h9QEFLHkUI1SIRs7/arcgis/rest/services/"
        #self.layer_id = "0"
    
    def get_gateway_patients(self):
        '''Each API has its own parameters
            Parameters are sent as a dictionary'''
        try:
            params = {
                'where': '1=1', #query parameters
                'outFields': '*', #what fields to return
                'returnGeometry': 'true', #additional options
                'f': 'json',
                'returnCountOnly': 'false'
            }
            '''requests is the standard Python library for API calls
            Different APIs might use different HTTP methods (GET, POST, PUT, etc.)'''
            response = requests.get(f'{self.base_url}Gateway_Community_Layer_by_Block_Group/FeatureServer/0/query', params=params)
            print(f"Request URL: {response.url}")
            
            '''Always include error handling for API calls
            Check status codes (200 = success)
            Handle different types of errors'''

            if response.status_code == 200:
                data = response.json()
                print("Response keys:", data.keys())
                return data
                
                # Better error handling
                 # Different error checking patterns
            if 'error' in data:  # ArcGIS style
                print("Error:", data['error'])
                return None
            elif 'errors' in data:  # Another API style
                print("Errors:", data['errors'])
                return None
            elif data.get('success') == False:  # Third style
                print("Failed:", data.get('message'))
                return None
                #print("Response keys:", data.keys())
                #return data
            else:
                print(f"Error status code: {response.status_code}")
                return None

        except requests.RequestException as e:
            print(f"Error fetching data: {e}")
            return None
    
    def get_gateway_visits(self):
        try:
            params = {
                'where': '1=1',
                'outFields': '*',
                'returnGeometry': 'true',
                'f': 'json',
                'returnCountOnly': 'false'
            }

            #get response
            response = requests.get(f'{self.base_url}Gateway_Community_Visits_by_Block_Group/FeatureServer/0/query', params=params)
            print(f'request Url: {response.url}')

            if response.status_code == 200:
                data = response.json()
                if 'error' in data:
                    print('API Error:', data['error'])
                    return None
                print("Response Keys:", data.keys()) #since in json format
                return data
            else:
                print(f'Error Status Code {response.status_code}')
                return None
        except requests.RequestException as e:
            print('Error fetching data {e}')
            return None



    def get_census(self):
        try:
            params = {
                'where': '1=1',
                'outFields': '*',
                'returnGeometry': 'true',
                'f': 'json',
                'returnCountOnly': 'false'
            }

            #get response
            response = requests.get(f'{self.base_url}Census_Important_Facts_by_Block_Groups/FeatureServer/0/query', params=params)
            print(f'request URL: {response.url}')

            if response.status_code == 200: #200 = success
                data = response.json()
            
                #error handling
                if 'error' in data:
                    print('Api Error:', data['error'])
                    return None
                #if no error
                print("Response Keys:", data.keys())
                return data
            else:
                print(f'Error status code: {response.status_code}')
                return None
        except requests.RequestException as e:
            print('Error fetching data: {e}')
            return None
    
    def get_gateway_data(self):
        try:
            params = {
                'where': '1=1',
                'outFields': '*',
                'returnGeometry': 'true',
                'f': 'json',
                'returnCountOnly': 'false'
            }
            response = requests.get(f'{self.base_url}Gateway_Community_Data_by_Block_Group/FeatureServer/0/query', params=params)
            print(f'Request Url:{response.url}')
            if response.status_code == 200:
                data = response.json()
                if 'error' in data:
                    print(f'Api Error,', data['error'])
                    return None
                print("Response Keys:", data.keys())
                return data
            else:
                print(f'Error status code: {response.status_code}')
                return None
        except requests.RequestException as e:
            print('Error fetching data {e}')
            return None







    def merge_with_health_data(self, health_data):
        #get ArcGIS data
        arc_data= self.get_demographic_data()
        
        if arc_data and 'features' in arc_data:
            #convert features to dataframe
            features_df = pd.DataFrame([f['attributes'] for f in arc_data['features']])

            print("ArcGIS Columns:", features_df.columns)
            print("\nHealth Data Columns:", health_data.columns)

            # Preview data before merge
            print("\nArcGIS Data Preview:")
            print(features_df.head())
            
            return features_df  # For now, just return ArcGIS data to examine
    