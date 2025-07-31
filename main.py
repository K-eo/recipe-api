from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import pandas as pd
import requests
from io import StringIO

app = FastAPI()

# Allow CORS for frontend access
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
    df.columns = df.columns.str.strip()  # clean column names
    return df

# Load data once at startup
df = load_data()

@app.get("/")
def read_root():
    return {"message": "Recipe API is running!"}

@app.get("/recipes")
def get_all_recipes():
    return df.to_dict(orient="records")

@app.get("/recipes/{index}")
def get_recipe_by_index(index: int):
    try:
        return df.iloc[index].to_dict()
    except IndexError:
        return {"error": "Recipe not found"}

@app.get("/search")
def search_recipes(query: str):
    query_lower = query.lower()
    filtered = df[df.apply(
        lambda row: query_lower in str(row['title']).lower()
        or query_lower in str(row['ingredients']).lower()
        or query_lower in str(row['directions']).lower(),
        axis=1
    )]
    return filtered.to_dict(orient="records")
