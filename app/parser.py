import re
from typing import List, Dict, Any
from app.models import ParsedQuery

# Keywords for amenities
AMENITY_KEYWORDS = {
    "parking": ["parking", "garage", "car", "park"],
    "balcony": ["balcony", "terrace", "patio"],
    "gym": ["gym", "fitness", "workout"],
    "pool": ["pool", "swimming"],
    "garden": ["garden", "lawn", "park"],
    "pet_friendly": ["pet", "dog", "cat", "animal"],
    "public_transit": ["metro", "bus", "transit", "train", "station"]
}

# Keywords for preferences
PREFERENCE_KEYWORDS = {
    "prefer_nearby_school": ["school", "education", "college"],
    "prefer_nearby_hospital": ["hospital", "clinic", "medical", "doctor"],
    "prefer_nearby_transit": ["metro", "bus", "station", "transit"]
}

def parse_query(query: str) -> ParsedQuery:
    query_lower = query.lower()
    parsed = ParsedQuery()

    # 1. Extract Price (max/min)
    normalized_query = re.sub(r'(\d+)k', r'\1000', query_lower)
    
    # Max Price
    max_price_match = re.search(r'(?:under|less than|max|budget|below)\s+?(\d+)', normalized_query)
    if max_price_match:
        parsed.max_price = int(max_price_match.group(1))
    
    # Min Price
    min_price_match = re.search(r'(?:above|more than|min|at least)\s+?(\d+)', normalized_query)
    if min_price_match:
        parsed.min_price = int(min_price_match.group(1))

    # 2. Extract Bedrooms
    bed_match = re.search(r'(\d+)\s*(?:bhk|bed|bedroom)', query_lower)
    if bed_match:
        parsed.bedrooms = int(bed_match.group(1))
    
    # 3. Extract Amenities
    found_amenities = []
    for key, synonyms in AMENITY_KEYWORDS.items():
        if any(syn in query_lower for syn in synonyms):
            found_amenities.append(key)
    parsed.amenities = found_amenities

    # 4. Extract Preferences
    if any(kw in query_lower for kw in PREFERENCE_KEYWORDS["prefer_nearby_school"]):
        parsed.prefer_nearby_school = True
    if any(kw in query_lower for kw in PREFERENCE_KEYWORDS["prefer_nearby_hospital"]):
        parsed.prefer_nearby_hospital = True
    if any(kw in query_lower for kw in PREFERENCE_KEYWORDS["prefer_nearby_transit"]):
        parsed.prefer_nearby_transit = True

    # 5. Extract Location
    loc_match = re.search(r'(?:near|in|at|to)\s+([a-zA-Z\s]+?)(?:\s+(?:and|with|for|under|below|max|min|budget)|\.|,|$)', query_lower)
    if loc_match:
        candidate = loc_match.group(1).strip()
        if candidate not in ["the", "a", "an"]:
            parsed.location = candidate.title()
    
    return parsed

if __name__ == "__main__":
    q = "2BHK under 40k near Pine Street with parking"
    print(parse_query(q))
