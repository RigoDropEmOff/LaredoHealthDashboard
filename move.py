import shutil
import os

#Create dic if it doesnt exist
os.makedirs('data', exist_ok=True)

#Move my csv files
for file in os.listdir():
    if file.endswith('.csv'):
        shutil.move(file, os.path.join('data', file))