from fastapi import FastAPI, Query
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure
from fastapi.middleware.cors import CORSMiddleware
from bson.json_util import dumps
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

# Connect to MongoDB
MONGO_URI = os.getenv("MONGO_URI")
client = MongoClient(MONGO_URI)
try:
    client.admin.command("ping")
except ConnectionFailure:
    raise Exception("MongoDB connection failed.")

# Select database and collection
db = client["FridgeChef"]
collection = db["RecipeList"]

# Initialize FastAPI
app = FastAPI()

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Home route
@app.get("/")
def read_root():
    return {"message": "FridgeChef API is live."}

# Search route
@app.get("/search")
def search_recipes(query: str = Query(..., min_length=1), limit: int = 10):
    results = collection.find(
        {"$text": {"$search": query}},
        {"score": {"$meta": "textScore"}}
    ).sort([("score", {"$meta": "textScore"})]).limit(limit)
    return list(results)
