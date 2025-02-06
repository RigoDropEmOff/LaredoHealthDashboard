import plotly.express as px
import pandas as pd
import json
import shutil
import os
#import geopandas as gpd

#Load the data
#health_data = pd.read_csv("C:\\Users\\rigor\\OneDrive\\Desktop\\202553ee-f06a-4109-820b-c2b548bddedc.csv")
#blocks = gpd.read_file("C:\\Users\\rigor\\OneDrive\\Desktop\\Health_Department_Data_by_Census_Block_Group.geojson")

#basic visual
#plt.figure(figsize=(10,6))
#plt.bar(health_data['GEOID10'], health_data['HD_Visits'])
#plt.title('Health Department Visits by Block Group')
#plt.xticks(rotation=45)
#plt.show()
#moving gejson to vs code directory for deployment
current_dir = os.path.dirname(__file__) #gets dict of current script
data_dir = os.path.join(current_dir, 'data')
os.makedirs(data_dir, exist_ok=True)

source = "C:\\Users\\rigor\\OneDrive\\Desktop\\Health_Department_Data_by_Census_Block_Group.geojson"
destination = 'data/census_blocks.geojson'
shutil.copy2(source, destination)