from fastapi import FastAPI, HTTPException
from contextlib import asynccontextmanager
from qdrant_client import QdrantClient
from sentence_transformers import SentenceTransformer
from typing import List, Dict, Any
import os

from app.models import SearchResponse, SearchResult, ParsedQuery, Property
from app.parser import parse_query
from app.ranking import Ranker

# Configuration
QDRANT_HOST = "localhost"
QDRANT_PORT = 6333
COLLECTION_NAME = "properties"
MODEL_NAME = "all-MiniLM-L6-v2"

# Global state
class State:
    qdrant_client: QdrantClient = None
    embedding_model: SentenceTransformer = None
    ranker: Ranker = None

app_state = State()

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    print("Initializing Qdrant Client...")
    app_state.qdrant_client = QdrantClient(host=QDRANT_HOST, port=QDRANT_PORT)
    
    print(f"Loading Embedding Model {MODEL_NAME}...")
    app_state.embedding_model = SentenceTransformer(MODEL_NAME)
    
    print("Initializing Ranker...")
    app_state.ranker = Ranker()
    
    yield
    # Shutdown
    print("Shutting down...")

app = FastAPI(title="Property Search AI", lifespan=lifespan)

@app.post("/search", response_model=SearchResponse)
async def search_properties(query_text: str):
    """
    Search for properties using natural language.
    """
    if not query_text:
        raise HTTPException(status_code=400, detail="Query text cannot be empty")

    # 1. Parse Query
    parsed_query = parse_query(query_text)
    
    # 2. Embed Query
    query_vector = app_state.embedding_model.encode(query_text).tolist()
    
    # 3. Vector Search
    # Fetch top 50 candidates
    search_result = app_state.qdrant_client.search(
        collection_name=COLLECTION_NAME,
        query_vector=query_vector,
        limit=50
    )
    
    # 4. Convert to Property objects
    properties: List[Property] = []
    semantic_scores: List[float] = []
    
    for hit in search_result:
        # payload is a dict, we convert to Property
        # Qdrant payload comes back as dict
        try:
            prop = Property(**hit.payload)
            properties.append(prop)
            semantic_scores.append(hit.score)
        except Exception as e:
            print(f"Error parsing property {hit.id}: {e}")
            continue

    # 5. Hybrid Ranking
    ranked_results = app_state.ranker.rank(properties, semantic_scores, parsed_query)
    
    # 6. Return Response
    # Return top 20 maybe? Prompt says we return results with explanations.
    return SearchResponse(
        results=ranked_results[:20],
        parsed_query=parsed_query
    )

@app.get("/")
def health_check():
    return {"status": "ok", "service": "Property Search AI"}
