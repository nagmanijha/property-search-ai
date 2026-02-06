from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any

class NearbyPlace(BaseModel):
    type: str
    name: str
    distance_m: int

class Property(BaseModel):
    id: str
    title: str
    description: str
    address: str
    neighborhood: str
    latitude: float
    longitude: float
    price: int
    bedrooms: int
    bathrooms: int
    area_sqft: int
    amenities: List[str]
    nearby_places: List[NearbyPlace]

class ParsedQuery(BaseModel):
    location: Optional[str] = None
    max_price: Optional[int] = None
    min_price: Optional[int] = None
    bedrooms: Optional[int] = None
    amenities: List[str] = Field(default_factory=list)
    prefer_nearby_school: bool = False
    prefer_nearby_hospital: bool = False
    prefer_nearby_transit: bool = False

class Explanation(BaseModel):
    semantic_similarity: float
    location_boost: float = 0.0
    amenity_match: float = 0.0
    price_match: float = 0.0
    bedroom_match: float = 0.0
    total_boost: float = 0.0

class SearchResult(BaseModel):
    id: str
    title: str
    score: float
    explanation: Explanation
    metadata: Dict[str, Any]

class SearchResponse(BaseModel):
    results: List[SearchResult]
    parsed_query: ParsedQuery
