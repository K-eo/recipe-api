from fastapi import FastAPI, Query
import pandas as pd
import os
import requests

app = FastAPI()

CSV_URL = "https://drive.google.com/uc?export=download&id=1-B_3b1x2Klct6LdhmGIslKb6bTxDcJuK"
CSV_FILE = "recipes.csv"

# Download the CSV if it doesn't exist locally
if not os.path.exists(CSV_FILE):
    print("Downloading recipes.csv...")
    try:
        r = requests.get(CSV_URL)
        with open(CSV_FILE, "wb") as f:
            f.write(r.content)
        print("Download complete.")
    except Exception as e:
        raise RuntimeError(f"Failed to download CSV: {e}")

# Load the CSV
try:
    df = pd.read_csv(CSV_FILE)
except Exception as e:
    raise RuntimeError(f"Failed to load CSV: {e}")

@app.get("/search")
def search_recipes(ingredients: str = Query(..., description="Comma-separated list of ingredients")):
    try:
        terms = [term.strip().lower() for term in ingredients.split(",")]

        def matches(row):
            ner_list = row["NER"].strip("[]").replace("'", "").split(", ")
            return all(any(term in ing.lower() for ing in ner_list) for term in terms)

        results = df[df.apply(matches, axis=1)]
        return results[["title", "NER", "directions"]].head(5).to_dict(orient="records")

    except Exception as e:
        return {"error": str(e)}
