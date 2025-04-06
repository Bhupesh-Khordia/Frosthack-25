import os
import faiss
import numpy as np
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain.text_splitter import CharacterTextSplitter

# Define correct file paths
OUTPUT_FOLDER = r"C:\Users\Siddhant\Desktop\Frosthack-25\backend\output"
EMBEDDINGS_FILE = r"C:\Users\Siddhant\Desktop\Frosthack-25\backend\embeddings.index"
CHUNK_MAP_FILE = r"C:\Users\Siddhant\Desktop\Frosthack-25\backend\chunk_map.txt"

# Ensure the output folder exists
if not os.path.exists(OUTPUT_FOLDER):
    # print(f"Error: Folder '{OUTPUT_FOLDER}' does not exist.")
    exit(1)

# Initialize HuggingFace Embeddings model
embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-mpnet-base-v2")

# Text splitter to process large documents
splitter = CharacterTextSplitter()

# Function to preprocess text
def preprocess_text(text):
    text = text.lower()  # Convert to lowercase
    text = text.replace("\n", " ")  # Remove newlines
    return text.strip()

# Function to load and embed documents
def load_and_store_embeddings():
    texts = []
    filenames = []

    # Read and store document content
    for file in os.listdir(OUTPUT_FOLDER):
        if file.endswith(".txt"):
            filepath = os.path.join(OUTPUT_FOLDER, file)
            with open(filepath, "r", encoding="utf-8") as f:
                content = f.read()
                texts.append(content)
                filenames.append(file)

    if not texts:
        # print("No text files found in the output folder.")
        return

    # Split text into chunks
    text_chunks = []
    chunk_map = []  # To map chunks back to filenames
    for i, text in enumerate(texts):
        chunks = splitter.split_text(text)
        chunks = [preprocess_text(chunk) for chunk in chunks]  # Preprocess each chunk
        text_chunks.extend(chunks)
        chunk_map.extend([filenames[i]] * len(chunks))  # Maintain mapping

    # Compute embeddings
    embeddings_array = np.array(embeddings.embed_documents(text_chunks))

    # Normalize embeddings for cosine similarity
    embeddings_array = embeddings_array / np.linalg.norm(embeddings_array, axis=1, keepdims=True)

    # Store embeddings using FAISS (cosine similarity)
    index = faiss.IndexFlatIP(embeddings_array.shape[1])  # Inner Product for cosine similarity
    index.add(embeddings_array)
    faiss.write_index(index, EMBEDDINGS_FILE)

    # Store chunk-filename mapping
    with open(CHUNK_MAP_FILE, "w", encoding="utf-8") as f:
        for chunk_filename in chunk_map:
            f.write(chunk_filename + "\n")

    return filenames

import sys

# Function to process queries
def search_documents(top_k=1):
    if not os.path.exists(EMBEDDINGS_FILE):
        # print("Error: Embeddings file not found. Run load_and_store_embeddings() first.")
        return []

    # Load stored embeddings
    index = faiss.read_index(EMBEDDINGS_FILE)

    if len(sys.argv) < 2:
        # print("Error: No query provided.")
        return

    query = sys.argv[1] 

    # Preprocess and embed query
    query = preprocess_text(query)
    query_embedding = np.array([embeddings.embed_query(query)])

    # Normalize query embedding for cosine similarity
    query_embedding = query_embedding / np.linalg.norm(query_embedding)

    # Perform search
    distances, indices = index.search(query_embedding, k=top_k)

    # Retrieve filenames of matched documents
    with open(CHUNK_MAP_FILE, "r", encoding="utf-8") as f:
        chunk_map = [line.strip() for line in f.readlines()]

    results = [(chunk_map[i], distances[0][j]) for j, i in enumerate(indices[0]) if i < len(chunk_map)]

    # Print results with similarity scores for debugging
    # print("Top Matches (with scores):", results)

    return [x[0] for x in results]

# Run embedding process
if __name__ == "__main__":
    load_and_store_embeddings()
    results = search_documents()
    print(results[0])
