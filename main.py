from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
import pandas as pd
import requests
from io import StringIO

app = FastAPI()

# Enable CORS for all origins (helpful during development)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load CSV data from Google Drive
def load_data():
    file_id = "1CZYUf4QbmW8ObtEMCUcSM2QvVuGIrxfR"
    url = f"https://drive.google.com/uc?id={file_id}&export=download"
    
    response = requests.get(url)
    response.raise_for_status()
    
    df = pd.read_csv(StringIO(response.text))
    df.columns = df.columns.str.strip().str.lower()  # Normalize column names (e.g. "Title", "Ingredients")
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
def search_recipes(query: str = Query(..., description="Search by ingredients")):
    query = query.lower()
    if "ingredients" not in df.columns:
        return {"error": "Ingredients column missing from data"}
    matches = df[df["ingredients"].str.lower().str.contains(query, na=False)]
    return matches.to_dict(orient="records")
