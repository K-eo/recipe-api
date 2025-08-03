import os
import json
import shutil
from fastapi import FastAPI, HTTPException, Query
from typing import List

app = FastAPI()

DATA_FOLDER = "data"
VOLUME_MOUNT = "/mnt/stunning-volume"

# Copy all JSON files from data folder to volume, only if they don't exist yet
def initialize_volume():
    os.makedirs(VOLUME_MOUNT, exist_ok=True)
    for filename in os.listdir(DATA_FOLDER):
        if filename.endswith(".json"):
            src = os.path.join(DATA_FOLDER, filename)
            dst = os.path.join(VOLUME_MOUNT, filename)
            if not os.path.exists(dst):
                shutil.copyfile(src, dst)

# Load all recipes from volume
def load_all_recipes():
    recipes = []
    for filename in os.listdir(VOLUME_MOUNT):
        if filename.endswith(".json"):
            path = os.path.join(VOLUME_MOUNT, filename)
            with open(path, "r", encoding="utf-8") as f:
                try:
                    data = json.load(f)
                    recipes.append(data)
                except json.JSONDecodeError:
                    continue  # Skip broken JSON
    return recipes

# Run on app startup
@app.on_event("startup")
def startup_event():
    initialize_volume()

@app.get("/")
def root():
    return {"message": "Recipe API is live."}

@app.get("/recipes", response_model=List[dict])
def get_all_recipes(limit: int = 20):
    recipes = load_all_recipes()
    return recipes[:limit]

@app.get("/recipes/search")
def search_recipes(query: str = Query(...)):
    results = []
    for recipe in load_all_recipes():
        name = recipe.get("name", "").lower()
        if query.lower() in name:
            results.append(recipe)
    return results

@app.get("/recipes/{recipe_id}")
def get_recipe_by_id(recipe_id: str):
    file_path = os.path.join(VOLUME_MOUNT, f"{recipe_id}.json")
    if os.path.exists(file_path):
        with open(file_path, "r", encoding="utf-8") as f:
            return json.load(f)
    raise HTTPException(status_code=404, detail="Recipe not found")
