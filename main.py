import os
from fastapi import FastAPI
from pymongo import MongoClient
from dotenv import load_dotenv
from typing import List
from fastapi.responses import JSONResponse

# Load environment variables
load_dotenv()

# Get MongoDB URI from environment variable
MONGO_URI = os.getenv("MONGO_URI")
if not MONGO_URI:
    raise ValueError("MONGO_URI not set in environment variables")

# Connect to MongoDB
client = MongoClient(MONGO_URI)
db = client["FridgeChef"]
collection = db["RecipeList"]

# Create FastAPI app
app = FastAPI()

@app.get("/")
def read_root():
    return {"message": "FridgeChef API is running."}

@app.get("/recipes", response_class=JSONResponse)
def get_recipes(skip: int = 0, limit: int = 10):
    """Fetch a limited list of recipes."""
    try:
        recipes = list(collection.find().skip(skip).limit(limit))
        for recipe in recipes:
            recipe["_id"] = str(recipe["_id"])  # Convert ObjectId to string for JSON serialization
        return recipes
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})

@app.get("/recipes/{recipe_id}")
def get_recipe(recipe_id: str):
    """Fetch a single recipe by its ID."""
    from bson import ObjectId
    try:
        recipe = collection.find_one({"_id": ObjectId(recipe_id)})
        if recipe:
            recipe["_id"] = str(recipe["_id"])
            return recipe
        return JSONResponse(status_code=404, content={"error": "Recipe not found"})
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})
