from fastapi import FastAPI, Query
from pymongo import MongoClient
import os

app = FastAPI()

# Get Mongo URI from environment variable
MONGO_URI = os.environ.get("MONGO_URI")

# Ensure it exists
if not MONGO_URI:
    raise RuntimeError("MONGO_URI environment variable not set")

# Extract database name from the URI
db_name = MONGO_URI.rsplit("/", 1)[-1].split("?")[0]
client = MongoClient(MONGO_URI)
db = client[db_name]
collection = db["recipes"]  # assuming collection is called 'recipes'

@app.get("/")
def root():
    return {"message": "Recipe API is connected to MongoDB!"}

@app.get("/count")
def count_recipes():
    return {"total_recipes": collection.count_documents({})}

@app.get("/search")
def search(query: str = Query(..., description="Keyword to search in NER field"), limit: int = 20):
    results = collection.find({"NER": {"$regex": query, "$options": "i"}}).limit(limit)
    return [r for r in results]

@app.get("/recipes")
def get_all(limit: int = 100):
    return [r for r in collection.find().limit(limit)]

@app.get("/recipes/{index}")
def get_by_index(index: int):
    result = collection.find().skip(index).limit(1)
    item = list(result)
    if item:
        return item[0]
    return {"error": "Recipe not found"}
