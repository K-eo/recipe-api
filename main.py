from fastapi import FastAPI, Query
import pandas as pd
import os

app = FastAPI()

DATA_DIR = "./data"
CSV_CACHE = {}  # Lazy-loaded cache


def get_all_dataframes():
    if CSV_CACHE:
        return CSV_CACHE.values()

    for filename in sorted(os.listdir(DATA_DIR)):
        if filename.endswith(".csv"):
            path = os.path.join(DATA_DIR, filename)
            df = pd.read_csv(path)
            CSV_CACHE[filename] = df
    return CSV_CACHE.values()


@app.get("/")
def read_root():
    return {"message": "Recipe API is running"}


@app.get("/count")
def get_count():
    total = 0
    files = 0
    for df in get_all_dataframes():
        total += len(df)
        files += 1
    return {"files_loaded": files, "total_rows": total}


@app.get("/search")
def search_recipes(query: str = Query(...), limit: int = 20):
    results = []
    for df in get_all_dataframes():
        matches = df[df["NER"].str.contains(query, case=False, na=False)]
        results.extend(matches.to_dict(orient="records"))
        if len(results) >= limit:
            break
    return results[:limit]


@app.get("/recipes")
def get_all_recipes(limit: int = 100):
    all_data = []
    for df in get_all_dataframes():
        all_data.extend(df.to_dict(orient="records"))
        if len(all_data) >= limit:
            break
    return all_data[:limit]


@app.get("/recipes/{global_index}")
def get_recipe(global_index: int):
    count = 0
    for df in get_all_dataframes():
        if global_index < count + len(df):
            return df.iloc[global_index - count].to_dict()
        count += len(df)
    return {"error": "Recipe not found"}
