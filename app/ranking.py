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
            # 0. Strict Filters
            # If max_price is set and property price > max_price, skip
            if query.max_price and prop.price > query.max_price:
                continue
            
            # If bedrooms set and property bedrooms < query.bedrooms, skip (Assuming '2 bedroom' means at least 2?)
            # Prompt says "2BHK", usually implies exact or min. Let's assume min or exact.
            # "2 bedroom flat... with parking". Usually means at least 2.
            # But the prompt says "Strict filters (max_price, min_bedrooms if detected)".
            # So let's interpret 'bedrooms' in query as MINIMUM bedrooms.
            if query.bedrooms and prop.bedrooms < query.bedrooms:
                continue
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
            
            # 3. Price Match (Bonus for being significantly under budget?)
            price_boost = 0.0
            # We already strictly filtered max_price. 
            # We can give a small boost if it's well under budget (e.g. 10% under), but simplicity is key.
            # Let's just grant W_PRICE if it satisfies constraints (which they all do now if filtered).
            # So effectively this adds 0.05 to everything. We can remove it or keep it as a baseline "valid" score.
            # Let's keep it 0.0 for now to depend more on semantic/location.
            
            # 4. Bedroom Match
            bed_boost = 0.0
            # If we filtered for min_bedrooms, we can boost EXACT match?
            if query.bedrooms and prop.bedrooms == query.bedrooms:
                bed_boost = self.W_BEDROOM
            
            # 5. Nearby Preferences
            nearby_bonus = 0.0
            if query.prefer_nearby_school:
                for place in prop.nearby_places:
                    if place.type == 'school' and place.distance_m <= 300:
                        nearby_bonus += 0.05 
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
