from fastapi import FastAPI, Query
from pymongo import MongoClient
from pymongo.errors import ServerSelectionTimeoutError
from typing import List
from fastapi.middleware.cors import CORSMiddleware
import os
import re

app = FastAPI()

# Allow all CORS (customize for production)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# MongoDB setup
MONGO_URI = os.getenv("MONGO_URI")
client = MongoClient(MONGO_URI)
db = client["recipes_list"]
collection = db["recipes_data"]

@app.get("/search")
def search_recipes(query: str = Query(...), limit: int = 5):
    try:
        regex = re.compile(query, re.IGNORECASE)
        results = list(collection.find({
            "$or": [
                {"title": {"$regex": regex}},
                {"ingredients": {"$elemMatch": {"$regex": regex}}},
                {"NER": {"$elemMatch": {"$regex": regex}}},
                {"directions": {"$elemMatch": {"$regex": regex}}}
            ]
        }).limit(limit))

        # Convert ObjectId to string for JSON serialization
        for doc in results:
            doc["_id"] = str(doc["_id"])

        return results

    except ServerSelectionTimeoutError:
        return {"error": "Database connection failed"}
