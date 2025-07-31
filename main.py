from fastapi import FastAPI, Query
from typing import List
import pandas as pd
import requests
from io import StringIO

app = FastAPI()

# Load data from Google Drive CSV
def load_data():
    file_id = "1-B_3b1x2Klct6LdhmGIslKb6bTxDcJuK"
    url = f"https://drive.google.com/uc?id={file_id}&export=download"
    response = requests.get(url)
    response.raise_for_status()

    df = pd.read_csv(StringIO(response.text), index_col=0)
    df.columns = df.columns.str.strip()  # Ensure no leading/trailing spaces
    df = df[['title', 'ingredients', 'NER', 'directions']]
    return df

# Load once on startup
df = load_data()

@app.get("/")
def root():
    return {"message": "Welcome to the Recipe API!"}

@app.get("/search")
def search(ingredients: List[str] = Query(...)):
    try:
        results = df[df['NER'].apply(
            lambda ner: all(ingredient.lower() in ner.lower() for ingredient in ingredients)
        )]
        return {"results": results.to_dict(orient="records")}
    except Exception as e:
        return {"error": str(e)}
