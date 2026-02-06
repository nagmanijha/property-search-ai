# Natural Language Property Search AI

An intelligent property search API that uses **Vector Search (Qdrant)** and **Hybrid Ranking** to understand natural language queries.

## Features

- **Semantic Search**: Understands queries like "cozy home near park" using `sentence-transformers`.
- **Hybrid Ranking**: Combines vector similarity with structured fields (price, location, amenities).
- **Smart Parsing**: Extracts structured constraints (Price < 40k, 2BHK) from free text.
- **Explainable AI**: Returns detailed scores explaining why a property was recommended.

## Tech Stack

- **Python 3.11**
- **FastAPI**
- **Qdrant** (Vector Database)
- **Sentence-Transformers** (`all-MiniLM-L6-v2`)

## Setup Instructions

### 1. Prerequisites
- Docker & Docker Compose
- Python 3.10+

### 2. Installation
1. Clone the repository:
   ```bash
   git clone https://github.com/rag/property-search-ai.git
   cd property-search-ai
   ```

2. Create a virtual environment (optional but recommended):
   ```bash
   python -m venv venv
   source venv/bin/activate  # Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

### 3. Start Qdrant
Run the vector database using Docker:
```bash
docker-compose up -d
```
Qdrant will be available at `http://localhost:6333`.

### 4. Ingest Data
Load the sample dataset into Qdrant:
```bash
python ingest.py
```
This will:
- Load properties from `../sample-dataset.json`
- Generate embeddings
- Store vectors in Qdrant

### 5. Run the API
Start the FastAPI server:
```bash
uvicorn app.main:app --reload
```
The API will be available at `http://127.0.0.1:8000`.

## API Usage

### Search Endpoint
**POST** `/search?query_text=...`

#### Example Query
`POST /search?query_text=2BHK under 40k near Pine Street with parking`

**Response:**
```json
{
  "results": [
    {
      "id": "prop_002",
      "title": "2BHK near Pine Street Market",
      "score": 0.85,
      "explanation": {
        "semantic_similarity": 0.81,
        "location_boost": 0.1,
        "amenity_match": 0.05,
        "price_match": 0.0,
        "total_boost": 0.15
      },
      "metadata": { ... }
    }
  ],
  "parsed_query": {
    "location": "Pine Street",
    "max_price": 40000,
    "bedrooms": 2,
    "amenities": ["parking"]
  }
}
```

## Design Decisions

### Query Parsing
We use a lightweight **Regex + Rule-based parser** (`app/parser.py`) to extract high-confidence signals:
- **Price**: "under 40k", "max 50000"
- **Bedrooms**: "2BHK", "3 bedrooms"
- **Amenities**: Matches keywords like "gym", "parking" against a predefined list.
- **Location**: Heuristic mapping specifically for "near [X]" patterns.

### Hybrid Ranking Strategy
We don't rely solely on vector search. The final score is calculated as:
`Score = (0.75 * Semantic) + Boosts`

Boosts include:
- **Location**: +0.10 for substring match.
- **Amenities**: +0.05 (scaled by overlap).
- **Price/Bedrooms**: +0.05 if strict constraints are met.
- **Proximity Preferences**: +0.02 each for requested nearby places (School, Transit).

This checks for both "meaning" (vectors) and "hard facts" (price/beds) to give the best user experience.
