import json
import os
from typing import List, Dict, Optional

class FavoritesService:
    """
    Service to manage favorite places.
    Persists data to a local JSON file.
    """
    FILE_PATH = "favorites.json"

    def __init__(self):
        self._favorites: List[Dict] = []
        self._load_favorites()

    def _load_favorites(self):
        """Load favorites from the JSON file."""
        if os.path.exists(self.FILE_PATH):
            try:
                with open(self.FILE_PATH, "r", encoding="utf-8") as f:
                    self._favorites = json.load(f)
            except (json.JSONDecodeError, IOError) as e:
                print(f"Error loading favorites: {e}")
                self._favorites = []
        else:
            self._favorites = []

    def _save_favorites(self):
        """Save favorites to the JSON file."""
        try:
            with open(self.FILE_PATH, "w", encoding="utf-8") as f:
                json.dump(self._favorites, f, indent=4)
        except IOError as e:
            print(f"Error saving favorites: {e}")

    def get_favorites(self) -> List[Dict]:
        """Return the list of favorite places."""
        return self._favorites

    def is_favorite(self, place_id: str) -> bool:
        """Check if a place is in favorites."""
        return any(f.get("place_id") == place_id or f.get("id") == place_id for f in self._favorites)

    def add_favorite(self, place: Dict):
        """Add a place to favorites if not already present."""
        place_id = place.get("place_id") or place.get("id")
        if not place_id:
            print("Cannot favorite a place without an ID")
            return

        if not self.is_favorite(place_id):
            # Store a minimal version or the full object. 
            # Storing essential fields for the list view is good practice.
            # Ensure we have consistent keys.
            fav_item = {
                "place_id": place_id,
                "name": place.get("name"),
                "formatted_address": place.get("formatted_address") or place.get("address"),
                "rating": place.get("rating"),
                "photos": place.get("photos", []),
                "image_url": place.get("image_url"), # If available directly
                "is_favorite": True
            }
            self._favorites.append(fav_item)
            self._save_favorites()

    def remove_favorite(self, place_id: str):
        """Remove a place from favorites."""
        self._favorites = [f for f in self._favorites if f.get("place_id") != place_id and f.get("id") != place_id]
        self._save_favorites()

    def toggle_favorite(self, place: Dict) -> bool:
        """
        Toggle the favorite status of a place.
        Returns the new status (True for favorite, False for not).
        """
        place_id = place.get("place_id") or place.get("id")
        if self.is_favorite(place_id):
            self.remove_favorite(place_id)
            return False
        else:
            self.add_favorite(place)
            return True
