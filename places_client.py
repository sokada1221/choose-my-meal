import requests
import json
from typing import List, Dict, Optional

class PlacesClient:
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://places.googleapis.com/v1"

    def find_place(self, query: str) -> Optional[str]:
        """Finds a place ID from a text query using Places API (New)."""
        url = f"{self.base_url}/places:searchText"
        headers = {
            "Content-Type": "application/json",
            "X-Goog-Api-Key": self.api_key,
            "X-Goog-FieldMask": "places.id,places.name"
        }
        payload = {
            "textQuery": query
        }

        try:
            response = requests.post(url, headers=headers, json=payload)
            response.raise_for_status()
            data = response.json()
            
            if data.get('places'):
                return data['places'][0]['id']
            return None
        except Exception as e:
            print(f"Error finding place '{query}': {e}")
            return None

    def get_place_details(self, place_id: str) -> Dict:
        """Fetches details for a specific place ID using Places API (New)."""
        url = f"{self.base_url}/places/{place_id}"
        headers = {
            "Content-Type": "application/json",
            "X-Goog-Api-Key": self.api_key,
            "X-Goog-FieldMask": "id,displayName,rating,userRatingCount,reviews"
        }

        try:
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            data = response.json()
            
            # Normalize data to match expected format in main.py
            return {
                "name": data.get("displayName", {}).get("text", ""),
                "rating": data.get("rating", "N/A"),
                "user_ratings_total": data.get("userRatingCount", 0),
                "reviews": data.get("reviews", [])
            }
        except Exception as e:
            print(f"Error getting details for place_id '{place_id}': {e}")
            return {}
