import os
from fastapi import FastAPI, Query, HTTPException
from pymongo import MongoClient
from bson import ObjectId

app = FastAPI()

# Grab your full URI (with /recipes_list) from Railway’s env
MONGO_URI = os.getenv(
    "MONGO_URI",
    "mongodb+srv://FridgeChef:TheRECIPEapp@cluster0.gaeubs.mongodb.net/recipes_list?retryWrites=true&w=majority"
)

# Connect & pick the exact DB & collection
client = MongoClient(MONGO_URI)
db = client["recipes_list"]
collection = db["recipes_data"]


@app.get("/search")
def search(query: str = Query(..., min_length=1), limit: int = Query(10, ge=1, le=100)):
    """
    Search for recipes whose title OR any element of ingredients/directions/NER
    contains `query` (case-insensitive). Returns up to `limit` docs.
    """
    try:
        cursor = collection.find(
            {
                "$or": [
                    {"title": {"$regex": query, "$options": "i"}},
                    {"ingredients": {"$elemMatch": {"$regex": query, "$options": "i"}}},
                    {"directions": {"$elemMatch": {"$regex": query, "$options": "i"}}},
                    {"NER": {"$elemMatch": {"$regex": query, "$options": "i"}}},
                ]
            }
        ).limit(limit)
    except Exception as e:
        raise HTTPException(500, f"DB query failed: {e}")

    results = []
    for doc in cursor:
        doc["_id"] = str(doc["_id"])
        results.append(doc)
    return results


@app.get("/recipes/{number}")
def get_recipe(number: int):
    """
    Fetch a single recipe by its `number` field.
    """
    doc = collection.find_one({"number": number})
    if not doc:
        raise HTTPException(404, "Recipe not found")
    doc["_id"] = str(doc["_id"])
    return doc


@app.get("/")
def home():
    return {"ok": True, "message": "FridgeChef API is alive!"}
