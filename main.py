from fastapi import FastAPI, Query
from pymongo import MongoClient
from dotenv import load_dotenv
from bson import ObjectId
import os

# Load environment variables
load_dotenv()

# Connect to MongoDB using MONGO_URI from Railway environment variable
MONGO_URI = os.getenv("MONGO_URI")
client = MongoClient(MONGO_URI)

# Explicitly select your DB and collection
db = client["FridgeChef"]
collection = db["RecipeList"]

app = FastAPI()

def serialize(doc):
    doc["_id"] = str(doc["_id"])
    return doc

@app.get("/")
def home():
    return {"message": "FridgeChef API is running!"}

@app.get("/count")
def count_recipes():
    count = collection.count_documents({})
    return {"total_recipes": count}

@app.get("/recipes")
def get_recipes(limit: int = 20):
    recipes = collection.find().limit(limit)
    return [serialize(r) for r in recipes]

@app.get("/search")
def search(query: str = Query(...), limit: int = 20):
    results = collection.find({"NER": {"$regex": query, "$options": "i"}}).limit(limit)
    return [serialize(r) for r in results]

@app.get("/recipes/{id}")
def get_recipe_by_id(id: str):
    try:
        recipe = collection.find_one({"_id": ObjectId(id)})
        return serialize(recipe) if recipe else {"error": "Recipe not found"}
    except Exception:
        return {"error": "Invalid ID format"}
