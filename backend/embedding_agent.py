import os
import time
import faiss
import numpy as np
from typing import Any, Dict, Optional

from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain.text_splitter import CharacterTextSplitter

from uagents import Agent, Context, Model

# File paths
OUTPUT_FOLDER = r"C:\Users\Siddhant\Desktop\Frosthack-25\backend\output"
EMBEDDINGS_FILE = r"C:\Users\Siddhant\Desktop\Frosthack-25\backend\embeddings.index"
CHUNK_MAP_FILE = r"C:\Users\Siddhant\Desktop\Frosthack-25\backend\chunk_map.txt"

# Initialize Agent
class Query(Model):
    query: str

class PathResponse(Model):
    timestamp: int
    text: str
    agent_address: str
    path: Optional[str] = None 

agent = Agent(name="Rest API", seed="embed", port=8002, endpoint=["http://localhost:8002/submit"])

# Load Embedding Model
embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-mpnet-base-v2")
splitter = CharacterTextSplitter()

def preprocess_text(text):
    text = text.lower().replace("\n", " ")
    return text.strip()

def load_and_store_embeddings():
    if not os.path.exists(OUTPUT_FOLDER):
        return []

    texts, filenames = [], []

    for file in os.listdir(OUTPUT_FOLDER):
        if file.endswith(".txt"):
            with open(os.path.join(OUTPUT_FOLDER, file), "r", encoding="utf-8") as f:
                texts.append(f.read())
                filenames.append(file)

    if not texts:
        return []

    text_chunks = []
    chunk_map = []
    for i, text in enumerate(texts):
        chunks = splitter.split_text(text)
        chunks = [preprocess_text(chunk) for chunk in chunks]
        text_chunks.extend(chunks)
        chunk_map.extend([filenames[i]] * len(chunks))

    embeddings_array = np.array(embeddings.embed_documents(text_chunks))
    embeddings_array = embeddings_array / np.linalg.norm(embeddings_array, axis=1, keepdims=True)

    index = faiss.IndexFlatIP(embeddings_array.shape[1])
    index.add(embeddings_array)
    faiss.write_index(index, EMBEDDINGS_FILE)

    with open(CHUNK_MAP_FILE, "w", encoding="utf-8") as f:
        for chunk_filename in chunk_map:
            f.write(chunk_filename + "\n")

    print(f"[INFO] Index and chunk map rebuilt with {len(chunk_map)} chunks.")
    return filenames

def search_documents(query: str, top_k: int = 1):
    # ✅ Automatically rebuild if missing
    if not os.path.exists(EMBEDDINGS_FILE) or not os.path.exists(CHUNK_MAP_FILE):
        print("[WARN] Index or chunk map missing. Rebuilding...")
        load_and_store_embeddings()

    if not os.path.exists(EMBEDDINGS_FILE) or not os.path.exists(CHUNK_MAP_FILE):
        print("[ERROR] Rebuild failed or no data found.")
        return None

    index = faiss.read_index(EMBEDDINGS_FILE)
    query = preprocess_text(query)
    query_embedding = np.array([embeddings.embed_query(query)])
    query_embedding = query_embedding / np.linalg.norm(query_embedding)

    distances, indices = index.search(query_embedding, k=top_k)

    with open(CHUNK_MAP_FILE, "r", encoding="utf-8") as f:
        chunk_map = [line.strip() for line in f.readlines()]

    if not chunk_map:
        print("[ERROR] Chunk map is empty after rebuild")
        return None

    results = [(chunk_map[i], distances[0][j]) for j, i in enumerate(indices[0]) if i < len(chunk_map)]

    return results[0][0] if results else None

@agent.on_rest_post("/rest/retrieve_closest", Query, PathResponse)
async def retrieve_closest(ctx: Context, req: Query) -> PathResponse:
    ctx.logger.info(f"Received query: {req.query}")
    try:
        closest_file = search_documents(req.query)
        if not closest_file:
            return PathResponse(
                text="Query not found in the documents",
                agent_address=ctx.agent.address,
                path=None,
                timestamp=int(time.time()),
            )
        return PathResponse(
            text="Retrieved closest statement successfully",
            agent_address=ctx.agent.address,
            path=closest_file,
            timestamp=int(time.time()),
        )
    except Exception as e:
        ctx.logger.error(f"Error: {e}")
        return PathResponse(
            text=f"An error occurred: {e}",
            agent_address=ctx.agent.address,
            path=None,
            timestamp=int(time.time()),
        )

# # ✅ Optional: expose manual trigger if needed
# @agent.on_rest_post("/rest/refresh_index")
# async def manual_refresh_index(ctx: Context, _msg: Dict[str, Any]):
#     filenames = load_and_store_embeddings()
#     return {"status": "refreshed", "files_indexed": filenames}

if __name__ == "__main__":
    load_and_store_embeddings()
    agent.run()
