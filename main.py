from fastapi import FastAPI, Query
import pandas as pd
import os

app = FastAPI()

# Path to your data folder
data_dir = "./data"
dataframes = []

# Load all CSV files at startup
for filename in sorted(os.listdir(data_dir)):
    if filename.endswith(".csv"):
        path = os.path.join(data_dir, filename)
        try:
            df = pd.read_csv(path)
            df.columns = df.columns.str.strip()
            dataframes.append(df)
        except Exception as e:
            print(f"Error reading {filename}: {e}")

@app.get("/")
def read_root():
    return {"message": "Recipe API is running"}

@app.get("/count")
def get_count():
    total = sum(len(df) for df in dataframes)
    return {"files_loaded": len(dataframes), "total_rows": total}

@app.get("/recipes")
def get_all_recipes(limit: int = 100):
    all_recipes = []
    for df in dataframes:
        all_recipes.extend(df.to_dict(orient="records"))
        if len(all_recipes) >= limit:
            break
    return all_recipes[:limit]

@app.get("/recipes/{global_index}")
def get_recipe_by_index(global_index: int):
    count = 0
    for df in dataframes:
        if global_index < count + len(df):
            return df.iloc[global_index - count].to_dict()
        count += len(df)
    return {"error": "Recipe not found"}

@app.get("/search")
def search_recipes(query: str = Query(..., description="Search term in NER field"), limit: int = 20):
    results = []
    for df in dataframes:
        if "NER" in df.columns:
            matches = df[df["NER"].str.contains(query, case=False, na=False)]
            results.extend(matches.to_dict(orient="records"))
            if len(results) >= limit:
                break
    return results[:limit]
