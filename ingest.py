import json
import os
from typing import List, Dict
from sentence_transformers import SentenceTransformer
from qdrant_client import QdrantClient
from qdrant_client.http import models
from app.models import Property
import sys

# Configuration
COLLECTION_NAME = "properties"
QDRANT_HOST = "localhost"
QDRANT_PORT = 6333
MODEL_NAME = "all-MiniLM-L6-v2"
DATASET_PATH = "../sample-dataset.json"

def load_data(path: str) -> List[Property]:
    print(f"Loading data from {path}...")
    try:
        with open(path, 'r') as f:
            data = json.load(f)
        return [Property(**item) for item in data]
    except FileNotFoundError:
        print(f"Error: File not found at {path}")
        sys.exit(1)
    except Exception as e:
        print(f"Error loading data: {e}")
        sys.exit(1)

def create_text_for_embedding(prop: Property) -> str:
    """
    Combines relevant fields into a single string for embedding.
    """
    amenities_str = ", ".join(prop.amenities)
    
    nearby_items = []
    for p in prop.nearby_places:
        nearby_items.append(f"{p.type} ({p.name})")
    nearby_str = ", ".join(nearby_items)
    
    # We want to capture the essence of the property
    # Title | Description | Neighborhood | Price | Bedrooms | Amenities | Nearby
    text = f"{prop.title}. {prop.description}. Located in {prop.neighborhood}, {prop.address}. " \
           f"Price: {prop.price}. Bedrooms: {prop.bedrooms}. " \
           f"Amenities: {amenities_str}. Nearby: {nearby_str}."
    return text

def ingest():
    # 1. Initialize Qdrant Client
    client = QdrantClient(host=QDRANT_HOST, port=QDRANT_PORT)
    
    # 2. Check if collection exists, recreate if needed
    collections = client.get_collections().collections
    exists = any(c.name == COLLECTION_NAME for c in collections)
    
    if exists:
        print(f"Collection '{COLLECTION_NAME}' exists. Recreating...")
        client.delete_collection(COLLECTION_NAME)
    
    print(f"Creating collection '{COLLECTION_NAME}'...")
    client.create_collection(
        collection_name=COLLECTION_NAME,
        vectors_config=models.VectorParams(size=384, distance=models.Distance.COSINE)
    )

    # 3. Load Data
    properties = load_data(DATASET_PATH)
    print(f"Loaded {len(properties)} properties.")

    # 4. Initialize Embedding Model
    print(f"Loading embedding model '{MODEL_NAME}'...")
    model = SentenceTransformer(MODEL_NAME)

    # 5. Generate Embeddings and Upsert
    points = []
    print("Generating embeddings and preparing points...")
    
    texts = [create_text_for_embedding(p) for p in properties]
    embeddings = model.encode(texts, show_progress_bar=True)

    for i, prop in enumerate(properties):
        # Convert property to dict for payload
        payload = prop.model_dump()
        
        point = models.PointStruct(
            id=i, 
            vector=embeddings[i].tolist(),
            payload=payload
        )
        points.append(point)

    # 6. Upload to Qdrant
    print(f"Uploading {len(points)} points to Qdrant...")
    client.upsert(
        collection_name=COLLECTION_NAME,
        points=points
    )
    print("Ingestion complete!")

if __name__ == "__main__":
    ingest()
