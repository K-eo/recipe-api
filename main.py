from fastapi import FastAPI, HTTPException, Query
from pymongo import MongoClient
from dotenv import load_dotenv
from pymongo.errors import ServerSelectionTimeoutError
import os

# Load environment variables
load_dotenv()

# Get Mongo URI from env
MONGO_URI = os.getenv("MONGO_URI")
if not MONGO_URI:
    raise RuntimeError("MONGO_URI not found in environment variables")

# Connect to MongoDB
try:
    client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=5000)
    db = client["fridgechef"]
    collection = db["RecipeList"]
    client.server_info()  # Force connection on startup to catch config issues
except ServerSelectionTimeoutError as err:
    raise RuntimeError(f"MongoDB connection failed: {err}")

# Create FastAPI app
app = FastAPI()

@app.get("/")
def root():
    return {"message": "FridgeChef API is live!"}

@app.get("/search")
def search(query: str = Query(..., min_length=1), limit: int = 20):
    try:
        results = collection.find(
            {"$text": {"$search": query}},
            {"score": {"$meta": "textScore"}, "_id": 0}
        ).sort([("score", {"$meta": "textScore"})]).limit(limit)
        return list(results)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
