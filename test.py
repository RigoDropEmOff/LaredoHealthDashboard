from api import ArcGISFetcher 
import pandas as pd
import requests

class ArcGISFetcher:
    def __init__(self):
        self.base_url = "https://services3.arcgis.com/h9QEFLHkUI1SIRs7/arcgis/rest/services/"
    
    def get_gateway_data(self):
        try:
            endpoint = f"{self.base_url}Gateway_Community_Data_by_Block_Group/FeatureServer/0/query"
            params = {
                'where': '1=1',
                'outFields': '*',
                'returnGeometry': 'true',
                'f': 'json',
                'returnCountOnly': 'false'
            }
            
            response = requests.get(endpoint, params=params)
            print(f"Request URL: {response.url}")
            print(f"Status code: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print("Response received:", data.keys())  # Debug line
                
                if 'features' in data:
                    return data
                else:
                    print("No features key in response. Response content:", data)
                    return None
            else:
                print(f"Request failed with status code: {response.status_code}")
                return None
                
        except requests.RequestException as e:
            print(f"Error fetching data: {e}")
            return None

# Create fetcher instance
fetcher = ArcGISFetcher()

# Get data
new_gateway_data = fetcher.get_gateway_data()
new_gateway_data_df = pd.DataFrame(new_gateway_data)



    