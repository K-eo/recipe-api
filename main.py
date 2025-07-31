from fastapi import FastAPI, Query
from fastapi.responses import JSONResponse
import pandas as pd
import requests
from io import StringIO

app = FastAPI()

CSV_URL = "https://drive.google.com/uc?export=download&id=1-B_3b1x2Klct6LdhmGIslKb6bTxDcJuK"

def load_data():
    response = requests.get(CSV_URL)
    if response.status_code != 200:
        raise Exception("Failed to download CSV")

    # Use only the 4 relevant columns
    df = pd.read_csv(StringIO(response.text), usecols=['title', 'ingredients', 'NER', 'directions'])

    # Convert NER column from string to list
    df['NER'] = df['NER'].apply(eval)

    # Drop rows with missing data in key columns
    df.dropna(subset=['NER', 'title', 'directions'], inplace=True)
    return df

df = load_data()

@app.get("/")
def root():
    return {"message": "Recipe API is running!"}

@app.get("/search")
def search(ingredients: str = Query(..., description="Comma-separated ingredients")):
    try:
        input_ingredients = [ing.strip().lower() for ing in ingredients.split(",")]
        results = []

        for _, row in df.iterrows():
            ner_ingredients = [item.lower() for item in row['NER']]
            if all(ing in ner_ingredients for ing in input_ingredients):
                results.append({
                    "title": row['title'],
                    "ingredients": row['ingredients'],
                    "directions": row['directions']
                })

        return {"results": results if results else "No matching recipes found."}
    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)
