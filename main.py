from fastapi import FastAPI, Query
from pymongo import MongoClient
from pymongo.errors import ServerSelectionTimeoutError
from dotenv import load_dotenv
import os

# Load environment variables (e.g., MONGO_URI from .env or Railway settings)
load_dotenv()
app = FastAPI()

# Connect to MongoDB
MONGO_URI = os.getenv("MONGO_URI")
client = MongoClient(MONGO_URI)
db = client["fridgechef"]  # Replace if your DB is named differently
collection = db["recipes_data"]

# Search endpoint
@app.get("/search")
def search_recipes(q: str = Query(..., min_length=1)):
    try:
        results = collection.find(
            { "$text": { "$search": q } },
            { "score": { "$meta": "textScore" }, "_id": 0 }
        ).sort([("score", { "$meta": "textScore" })]).limit(20)
        return list(results)
    except ServerSelectionTimeoutError:
        return { "error": "Could not connect to MongoDB." }
