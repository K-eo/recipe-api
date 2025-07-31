from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import pandas as pd
import requests
from io import StringIO

app = FastAPI()

# CORS setup
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

def load_data():
    file_id = "1-B_3b1x2Klct6LdhmGIslKb6bTxDcJuK"
    url = f"https://drive.google.com/uc?export=download&id={file_id}"

    response = requests.get(url)
    content = response.text

    # Try to detect if it’s accidentally HTML (which Google returns sometimes)
    if "<html" in content.lower():
        raise ValueError("Failed to download CSV – Google Drive returned HTML instead. Make sure file is publicly shared.")

    df = pd.read_csv(StringIO(content))

    # Show actual columns in log
    print("Columns found:", df.columns.tolist())

    # Only select expected columns if they exist
    expected_cols = ['title', 'ingredients', 'NER', 'directions']
    missing = [col for col in expected_cols if col not in df.columns]
    if missing:
        raise ValueError(f"Missing expected columns in CSV: {missing}")

    return df[expected_cols]

df = load_data()

@app.get("/")
def read_root():
    return {"message": "Recipe API running"}

@app.get("/recipes")
def get_recipes():
    return df.to_dict(orient="records")
