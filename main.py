from fastapi import FastAPI, Query
from pymongo import MongoClient
from fastapi.middleware.cors import CORSMiddleware
from typing import List
import os

app = FastAPI()

# Allow CORS (for Swagger UI or browser testing)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# MongoDB connection
MONGO_URI = os.getenv("MONGO_URI", "your-mongodb-uri")  # Replace with your URI in Railway ENV
client = MongoClient(MONGO_URI)
db = client["recipes_list"]
collection = db["recipes_data"]

@app.get("/search")
def search_recipes(query: str = Query(...), limit: int = 5):
    # Use regex on the NER field (list of strings)
    results = collection.find(
        { "NER": { "$regex": query, "$options": "i" } }
    ).limit(limit)

    return list(results)
