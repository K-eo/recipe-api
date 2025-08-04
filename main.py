from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from pymongo import MongoClient
from bson import ObjectId
import os

app = FastAPI()

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Use Railway's env variable or fallback
MONGO_URI = os.getenv("MONGO_URI", "your fallback URI")

# Connect to DB
client = MongoClient(MONGO_URI)
db = client["recipes_list"]  # IMPORTANT: Explicitly define database
collection = db["recipes_data"]


@app.get("/search")
def search(query: str = Query(...), limit: int = Query(10)):
    results = collection.find(
        {
            "$or": [
                {"title": {"$regex": query, "$options": "i"}},
                {"ingredients": {"$regex": query, "$options": "i"}},
                {"directions": {"$regex": query, "$options": "i"}},
                {"NER": {"$regex": query, "$options": "i"}},
            ]
        }
    ).limit(limit)

    # Convert ObjectId to string
    return [{**doc, "_id": str(doc["_id"])} for doc in results]
