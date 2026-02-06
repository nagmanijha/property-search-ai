from fastapi import FastAPI, HTTPException
from contextlib import asynccontextmanager
from qdrant_client import QdrantClient
from sentence_transformers import SentenceTransformer
from typing import List
from app.models import SearchResponse, Property, SearchResult, ParsedQuery, Explanation

# Configuration
QDRANT_HOST = "localhost"
QDRANT_PORT = 6333
COLLECTION_NAME = "properties"
MODEL_NAME = "all-MiniLM-L6-v2"

# Global state
class State:
    qdrant_client: QdrantClient = None
    embedding_model: SentenceTransformer = None

app_state = State()

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    print("Initializing Qdrant Client...")
    app_state.qdrant_client = QdrantClient(host=QDRANT_HOST, port=QDRANT_PORT)
    
    print(f"Loading Embedding Model {MODEL_NAME}...")
    app_state.embedding_model = SentenceTransformer(MODEL_NAME)
    
    yield
    # Shutdown
    print("Shutting down...")

app = FastAPI(title="Property Search AI", lifespan=lifespan)

@app.post("/search")
async def search_properties(query_text: str):
    if not query_text:
        raise HTTPException(status_code=400, detail="Query text cannot be empty")

    # 1. Embed Query
    query_vector = app_state.embedding_model.encode(query_text).tolist()
    
    # 2. Vector Search
    search_result = app_state.qdrant_client.search(
        collection_name=COLLECTION_NAME,
        query_vector=query_vector,
        limit=20
    )
    
    # 3. Simple Return
    results = []
    for hit in search_result:
        results.append({
            "score": hit.score,
            "payload": hit.payload
        })

    return {"results": results}
