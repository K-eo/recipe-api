from fastapi import FastAPI, Query
from fastapi.responses import JSONResponse
from pymongo import MongoClient
from dotenv import load_dotenv
import os

load_dotenv()

app = FastAPI()

# Set up MongoDB connection
MONGO_URI = os.getenv("MONGO_URI")
client = MongoClient(MONGO_URI)

# ✅ Specify the DB and collection explicitly
db = client["recipes_list"]
collection = db["recipes_data"]

@app.get("/")
def root():
    return {"message": "FridgeChef API is live"}

@app.get("/search")
def search_recipes(query: str = Query(..., min_length=1), limit: int = 10):
    regex_query = {"$regex": query, "$options": "i"}

    results = collection.find(
        {
            "$or": [
                {"title": regex_query},
                {"ingredients": {"$elemMatch": regex_query}},
                {"directions": {"$elemMatch": regex_query}},
                {"NER": {"$elemMatch": regex_query}},
            ]
        }
    ).limit(limit)

    return JSONResponse([
        {
            "title": r.get("title"),
            "ingredients": r.get("ingredients"),
            "directions": r.get("directions"),
            "NER": r.get("NER")
        } for r in results
    ])
