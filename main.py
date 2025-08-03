from fastapi import FastAPI, Query
import pandas as pd
import os
import shutil

app = FastAPI()

# Define repo and volume paths
REPO_DATA_DIR = os.path.join(os.path.dirname(__file__), "data")
VOLUME_PATH = "/mnt/stunning-volume"

# Ensure the volume directory exists
os.makedirs(VOLUME_PATH, exist_ok=True)

# Copy CSV files to the Railway volume (only if volume is empty)
if not os.listdir(VOLUME_PATH):
    for filename in sorted(os.listdir(REPO_DATA_DIR)):
        if filename.endswith(".csv"):
            shutil.copy(os.path.join(REPO_DATA_DIR, filename), VOLUME_PATH)

# Lazy-load CSVs from volume
def get_all_dataframes():
    dataframes = []
    for filename in sorted(os.listdir(VOLUME_PATH)):
        if filename.endswith(".csv"):
            path = os.path.join(VOLUME_PATH, filename)
            df = pd.read_csv(path)
            dataframes.append(df)
    return dataframes

@app.get("/")
def root():
    return {"message": "Recipe API is running."}

@app.get("/count")
def count():
    total = sum(len(df) for df in get_all_dataframes())
    return {"total_recipes": total, "files_loaded": len(get_all_dataframes())}

@app.get("/search")
def search(query: str = Query(...), limit: int = 20):
    results = []
    for df in get_all_dataframes():
        matches = df[df["NER"].str.contains(query, case=False, na=False)]
        results.extend(matches.to_dict(orient="records"))
        if len(results) >= limit:
            break
    return results[:limit]

@app.get("/recipes")
def all_recipes(limit: int = 100):
    all_data = []
    for df in get_all_dataframes():
        all_data.extend(df.to_dict(orient="records"))
        if len(all_data) >= limit:
            break
    return all_data[:limit]

@app.get("/recipes/{global_index}")
def get_by_index(global_index: int):
    count = 0
    for df in get_all_dataframes():
        if global_index < count + len(df):
            return df.iloc[global_index - count].to_dict()
        count += len(df)
    return {"error": "Recipe not found"}
