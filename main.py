from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from pymongo import MongoClient
from bson.json_util import dumps
import os
import re

from dotenv import load_dotenv
load_dotenv()

app = FastAPI()

# Allow all CORS (for dev or frontend testing)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# MongoDB connection
MONGO_URI = os.getenv("MONGO_URI")
client = MongoClient(MONGO_URI)
db = client["recipes_list"]
collection = db["recipes_data"]

@app.get("/")
def root():
    return {"message": "FridgeChef API is live!"}

@app.get("/search")
def search_recipes(query: str = Query(...), limit: int = 5):
    regex = re.compile(query, re.IGNORECASE)
    results = collection.find({
        "$or": [
            {"title": regex},
            {"ingredients": regex},
            {"directions": regex},
            {"NER": regex}
        ]
    }).limit(limit)
    return eval(dumps(results))  # convert BSON to JSON
