# db.py
import os
from pymongo import MongoClient
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()

# Replace with your actual MongoDB connection URI
MONGO_URI = os.getenv("MONGODB_URI")

# Create client and select DB
client = MongoClient(MONGO_URI)
db = client['frosthack_db']  # Use your preferred database name

# Define collections
pdf_collection = db['pdf_files']
json_collection = db['json_files']
txt_collection = db['txt_files']
embedding_collection = db['embeddings'] 