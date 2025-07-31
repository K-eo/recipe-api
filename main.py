from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
import pandas as pd
import requests
from io import StringIO

app = FastAPI()

# CORS settings
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load CSV from Google Drive
def load_data():
    file_id = "1-B_3b1x2Klct6LdhmGIslKb6bTxDcJuK"
    url = f"https://drive.google.com/uc?id={file_id}&export=download"
    response = requests.get(url)
    response.raise_for_status()

    df = pd.read_csv(StringIO(response.text))
    df.columns = df.columns.str.strip()

    # No column dropping!
    return df

# Load once at startup
df = load_data()

@app.get("/")
def read_root():
    return {"message": "Recipe API is running!"}

@app.get("/recipes")
def get_all_recipes():
    return df.to_dict(orient="records")

@app.get("/recipes/{index}")
def get_recipe_by_index(index: int):
    if index < 0 or index >= len(df):
        return {"error": "Recipe not found"}
    return df.iloc[index].to_dict()

@app.get("/search")
def search_recipes(query: str = Query(..., min_length=1)):
    query = query.lower()
    results = []

    for _, row in df.iterrows():
        if any(query in str(row[col]).lower() for col in ['title', 'ingredients', 'NER', 'directions']):
            results.append(row.to_dict())

    return results
