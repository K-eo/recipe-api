from fastapi import FastAPI, HTTPException
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure
from dotenv import load_dotenv
import os

# Load environment variables from Railway-provided environment
load_dotenv()

# Connect to MongoDB
MONGO_URI = os.getenv("MONGO_URI")
if not MONGO_URI:
    raise Exception("MONGO_URI environment variable is not set")

client = MongoClient(MONGO_URI)
try:
    client.admin.command('ping')  # Test connection
except ConnectionFailure:
    raise Exception("Failed to connect to MongoDB")

# Access specific database and collection
db = client["FridgeChef"]
collection = db["RecipeList"]

app = FastAPI()

@app.get("/")
def root():
    return {"message": "Welcome to the FridgeChef API"}

@app.get("/recipes/")
def get_recipes(skip: int = 0, limit: int = 10):
    cursor = collection.find().skip(skip).limit(limit)
    recipes = [doc for doc in cursor]
    for recipe in recipes:
        recipe["_id"] = str(recipe["_id"])  # Convert ObjectId to string
    return {"recipes": recipes}

@app.get("/recipes/{recipe_id}")
def get_recipe_by_id(recipe_id: str):
    from bson import ObjectId
    if not ObjectId.is_valid(recipe_id):
        raise HTTPException(status_code=400, detail="Invalid ID format")
    recipe = collection.find_one({"_id": ObjectId(recipe_id)})
    if recipe is None:
        raise HTTPException(status_code=404, detail="Recipe not found")
    recipe["_id"] = str(recipe["_id"])
    return recipe
