import requests
import json

BASE_URL = "http://localhost:8000"

def test_query(query: str):
    print(f"\nQUERY: {query}")
    try:
        response = requests.post(f"{BASE_URL}/search", params={"query_text": query})
        response.raise_for_status()
        data = response.json()
        
        print(f"Parsed: {json.dumps(data['parsed_query'], indent=2)}")
        print(f"Top Result Score: {data['results'][0]['score'] if data['results'] else 'No results'}")
        
        for res in data['results'][:3]:
            print(f"- {res['title']} (Score: {res['score']})")
            print(f"  Explanation: {res['explanation']}")
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    queries = [
        "2BHK under 40k near Pine Street with parking",
        "I recently shifted to Pine Street and am looking for a property, and the nearby school is preferable.",
        "Cheap studio close to metro",
        "Pet-friendly house with balcony",
        "Luxury villa with pool"
    ]
    
    for q in queries:
        test_query(q)
