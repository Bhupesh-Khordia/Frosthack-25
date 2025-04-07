import os
import time
import faiss
import numpy as np
from typing import Optional

from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain.text_splitter import CharacterTextSplitter
from uagents import Agent, Context, Model

from db import txt_collection, embedding_collection  # ✅ Using centralized DB setup

# Initialize Agent
class Query(Model):
    query: str

class PathResponse(Model):
    timestamp: int
    text: str
    agent_address: str
    path: Optional[str] = None


class DummyRequest(Model):
    pass

class FileListResponse(Model):
    files: list[str]



agent = Agent(name="Rest API", seed="embed", port=8002, endpoint=["http://localhost:8002/submit"])

# Embedding model and splitter
embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-mpnet-base-v2")
splitter = CharacterTextSplitter()

def preprocess_text(text: str) -> str:
    return text.lower().replace("\n", " ").strip()

def load_and_store_embeddings():
    if txt_collection.count_documents({}) == 0:
        print("No text documents found in MongoDB.")
        return

    txt_docs = txt_collection.find()

    text_chunks = []
    chunk_map = []

    for doc in txt_docs:
        narration = doc.get("content")
        filename = doc.get("filename")

        if not narration or not filename:
            print(f"[WARN] Skipping document due to missing fields: {doc}")
            continue

        chunks = splitter.split_text(narration)
        chunks = [preprocess_text(chunk) for chunk in chunks]
        text_chunks.extend(chunks)
        chunk_map.extend([filename] * len(chunks))

    if not text_chunks:
        print("[WARN] No valid chunks found.")
        return []

    # Generate normalized embeddings
    embeddings_array = np.array(embeddings.embed_documents(text_chunks))
    embeddings_array = embeddings_array / np.linalg.norm(embeddings_array, axis=1, keepdims=True)

    # Store index in FAISS
    index = faiss.IndexFlatIP(embeddings_array.shape[1])
    index.add(embeddings_array)

    # Convert to bytes
    index_data = faiss.serialize_index(index)

    # Store index and chunk map in MongoDB
    embedding_collection.delete_many({})
    embedding_collection.insert_one({
        "index": index_data.tobytes(),
        "chunk_map": chunk_map
    })

    print(f"[INFO] Stored {len(chunk_map)} chunks in MongoDB.")
    return chunk_map

def search_documents(query: str, top_k: int = 1):
    record = embedding_collection.find_one()
    if not record:
        print("[WARN] No embeddings found. Rebuilding...")
        load_and_store_embeddings()
        record = embedding_collection.find_one()
        if not record:
            print("[ERROR] Still no embeddings found.")
            return None

    index_data = record["index"]
    chunk_map = record["chunk_map"]

    index = faiss.deserialize_index(np.frombuffer(index_data, dtype=np.uint8))

    query_vec = np.array([embeddings.embed_query(preprocess_text(query))])
    query_vec = query_vec / np.linalg.norm(query_vec)

    distances, indices = index.search(query_vec, top_k)

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
                timestamp=int(time.time())
            )
        return PathResponse(
            text="Retrieved closest statement successfully",
            agent_address=ctx.agent.address,
            path=closest_file,
            timestamp=int(time.time())
        )
    except Exception as e:
        ctx.logger.error(f"Error: {e}")
        return PathResponse(
            text=f"An error occurred: {e}",
            agent_address=ctx.agent.address,
            path=None,
            timestamp=int(time.time())
        )
    
@agent.on_rest_post("/rest/list_files", DummyRequest, FileListResponse)
async def list_files(ctx: Context, req: DummyRequest) -> FileListResponse:
    try:
        files = txt_collection.distinct("filename")
        return FileListResponse(files=files)
    except Exception as e:
        ctx.logger.error(f"Error listing files: {e}")
        return FileListResponse(files=[])

if __name__ == "__main__":
    load_and_store_embeddings()
    agent.run()
