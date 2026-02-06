from fastapi import FastAPI, HTTPException
from contextlib import asynccontextmanager
from qdrant_client import QdrantClient
from sentence_transformers import SentenceTransformer
from typing import List
from app.models import SearchResponse, Property, SearchResult, ParsedQuery
from app.parser import parse_query

# Configuration
QDRANT_HOST = "localhost"
QDRANT_PORT = 6333
COLLECTION_NAME = "properties"
MODEL_NAME = "all-MiniLM-L6-v2"

class State:
    qdrant_client: QdrantClient = None
    embedding_model: SentenceTransformer = None

app_state = State()

@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Initializing Qdrant Client...")
    app_state.qdrant_client = QdrantClient(host=QDRANT_HOST, port=QDRANT_PORT)
    print(f"Loading Embedding Model {MODEL_NAME}...")
    app_state.embedding_model = SentenceTransformer(MODEL_NAME)
    yield
    print("Shutting down...")

app = FastAPI(title="Property Search AI", lifespan=lifespan)

@app.post("/search")
async def search_properties(query_text: str):
    if not query_text:
        raise HTTPException(status_code=400, detail="Query text cannot be empty")

    # 1. Parse Query
    parsed_query = parse_query(query_text)
    
    # 2. Embed Query
    query_vector = app_state.embedding_model.encode(query_text).tolist()
    
    # 3. Vector Search
    search_result = app_state.qdrant_client.search(
        collection_name=COLLECTION_NAME,
        query_vector=query_vector,
        limit=50
    )
    
    # 4. Return with Parsed Info (No ranking yet)
    results = []
    for hit in search_result:
        results.append({
            "score": hit.score,
            "payload": hit.payload
        })

    return {
        "results": results[:20],
        "parsed_query": parsed_query
    }
