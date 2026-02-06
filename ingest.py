import json
import os
from typing import List, Dict
from app.models import Property
import sys

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

if __name__ == "__main__":
    load_data(DATASET_PATH)
