import pandas as pd
import numpy as np

df = pd.read_csv("C:\\Users\\rigor\\OneDrive\\Desktop\\202553ee-f06a-4109-820b-c2b548bddedc.csv")

#df.head()
df.info()
max_visits = df['HD_Visits'].max()
print(max_visits)

all_visists = df['HD_Visits'].sum()
print(all_visists)


blocks = df.groupby('GEOID10')['HD_Visits'].sum()


print(df.head())