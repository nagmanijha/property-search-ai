from typing import List
from app.models import Property, ParsedQuery, SearchResult, Explanation

class Ranker:
    def __init__(self):
        # Weights
        self.W_SEMANTIC = 0.75
        self.W_LOCATION = 0.10
        self.W_AMENITY = 0.05
        self.W_PRICE = 0.05
        self.W_BEDROOM = 0.05
        pass

    def rank(self, properties: List[Property], semantic_scores: List[float], query: ParsedQuery) -> List[SearchResult]:
        results = []
        
        for prop, sem_score in zip(properties, semantic_scores):
            # 1. Location Boost
            loc_boost = 0.0
            if query.location:
                if query.location.lower() in prop.neighborhood.lower() or \
                   query.location.lower() in prop.address.lower() or \
                   query.location.lower() in prop.title.lower():
                    loc_boost = self.W_LOCATION
            
            # 2. Amenity Boost
            amenity_boost = 0.0
            if query.amenities:
                matching = [a for a in query.amenities if a in prop.amenities]
                if matching:
                    ratio = len(matching) / len(query.amenities)
                    amenity_boost = ratio * self.W_AMENITY
            
            # 3. Price Match
            price_boost = 0.0
            if query.max_price:
                if prop.price <= query.max_price:
                    price_boost = self.W_PRICE
            elif query.min_price:
                 if prop.price >= query.min_price:
                    price_boost = self.W_PRICE
            
            # 4. Bedroom Match
            bed_boost = 0.0
            if query.bedrooms:
                if prop.bedrooms == query.bedrooms:
                    bed_boost = self.W_BEDROOM
            
            # 5. Nearby Preferences
            nearby_bonus = 0.0
            if query.prefer_nearby_school:
                for place in prop.nearby_places:
                    if place.type == 'school' and place.distance_m < 1000:
                        nearby_bonus += 0.02 
                        break
            
            if query.prefer_nearby_hospital:
                 for place in prop.nearby_places:
                    if place.type == 'hospital' and place.distance_m < 2000:
                        nearby_bonus += 0.02
                        break
                        
            if query.prefer_nearby_transit:
                 for place in prop.nearby_places:
                    if place.type in ['transit', 'station', 'metro'] and place.distance_m < 1000:
                        nearby_bonus += 0.02
                        break

            final_score = (self.W_SEMANTIC * sem_score) + \
                          loc_boost + \
                          amenity_boost + \
                          price_boost + \
                          bed_boost + \
                          nearby_bonus
            
            explanation = Explanation(
                semantic_similarity=round(sem_score, 4),
                location_boost=round(loc_boost, 4),
                amenity_match=round(amenity_boost, 4),
                price_match=round(price_boost, 4),
                bedroom_match=round(bed_boost, 4),
                total_boost=round(loc_boost + amenity_boost + price_boost + bed_boost + nearby_bonus, 4)
            )
            
            results.append(SearchResult(
                id=prop.id,
                title=prop.title,
                score=round(final_score, 4),
                explanation=explanation,
                metadata=prop.model_dump()
            ))
            
        results.sort(key=lambda x: x.score, reverse=True)
        return results
