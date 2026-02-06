import json
import os
from typing import List, Dict
from sentence_transformers import SentenceTransformer
from app.models import Property
import sys

DATASET_PATH = "../sample-dataset.json"
MODEL_NAME = "all-MiniLM-L6-v2"

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
    properties = load_data(DATASET_PATH)
    print(f"Loading embedding model '{MODEL_NAME}'...")
    model = SentenceTransformer(MODEL_NAME)
    
    texts = [create_text_for_embedding(p) for p in properties]
    embeddings = model.encode(texts, show_progress_bar=True)
    print(f"Generated {len(embeddings)} embeddings.")

if __name__ == "__main__":
    ingest()
