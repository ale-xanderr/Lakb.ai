import json
import os
import flet as ft
from typing import List, Dict, Optional
from core.supabase_client import get_supabase_client
from core.connectivity import get_connectivity_state, mark_offline, mark_online

class FavoritesService:
    """
    Service to manage favorite places.
    Persists data to Supabase if logged in, otherwise falls back to a local JSON file.
    For authenticated users, also caches to client_storage for offline access.
    """
    FILE_PATH = "favorites.json"
    CACHE_KEY = "user_favorites_cache"

    def __init__(self):
        self.client = get_supabase_client()
        self._favorites: List[Dict] = []
        self._supabase_fetch_done = False
        self._cached_user_id = None
        self._user_id_cache_valid = False
        self._page: Optional[ft.Page] = None
        self._load_local_favorites()

    def initialize(self, page: ft.Page):
        """
        Initialize the service with page reference for client_storage access.
        
        Args:
            page: The Flet page instance
        """
        self._page = page
        # Try to load from client storage cache
        self._load_from_client_storage()

    def _load_local_favorites(self):
        """Load favorites from the local JSON file (fallback)."""
        if os.path.exists(self.FILE_PATH):
            try:
                with open(self.FILE_PATH, "r", encoding="utf-8") as f:
                    self._favorites = json.load(f)
            except (json.JSONDecodeError, IOError) as e:
                print(f"Error loading local favorites: {e}")
                self._favorites = []
        else:
            self._favorites = []

    def _save_local_favorites(self):
        """Save favorites to the local JSON file (fallback)."""
        try:
            with open(self.FILE_PATH, "w", encoding="utf-8") as f:
                json.dump(self._favorites, f, indent=4)
        except IOError as e:
            print(f"Error saving local favorites: {e}")

    def _load_from_client_storage(self):
        """Load favorites from client_storage cache (for authenticated users offline)."""
        if not self._page or not hasattr(self._page, 'client_storage'):
            return
        
        try:
            cached_data = self._page.client_storage.get(self.CACHE_KEY)
            if cached_data:
                self._favorites = json.loads(cached_data)
                print(f"Loaded {len(self._favorites)} favorites from client storage cache")
        except Exception as e:
            print(f"Error loading favorites from client storage: {e}")

    def _save_to_client_storage(self):
        """Save favorites to client_storage cache (for authenticated users offline access)."""
        if not self._page or not hasattr(self._page, 'client_storage'):
            return
        
        try:
            self._page.client_storage.set(self.CACHE_KEY, json.dumps(self._favorites))
            print(f"Saved {len(self._favorites)} favorites to client storage cache")
        except Exception as e:
            print(f"Error saving favorites to client storage: {e}")

    def clear_cache(self):
        """Clear the client storage cache (called on logout)."""
        if self._page and hasattr(self._page, 'client_storage'):
            try:
                self._page.client_storage.remove(self.CACHE_KEY)
                print("Favorites cache cleared")
            except Exception as e:
                print(f"Error clearing favorites cache: {e}")
        self._favorites = []
        self._supabase_fetch_done = False

    def _get_current_user_id(self, force_refresh=False) -> Optional[str]:
        """Get current user ID, using cache when possible to avoid redundant API calls."""
        if not self.client:
            self._cached_user_id = None
            self._user_id_cache_valid = False
            return None
        
        # Return cached value if available and not forcing refresh
        if self._user_id_cache_valid and not force_refresh and self._cached_user_id is not None:
            return self._cached_user_id
        
        try:
            # get_user() returns an object where .user contains the details
            response = self.client.auth.get_user()
            if response and hasattr(response, 'user') and response.user:
                user_id = response.user.id
                self._cached_user_id = user_id
                self._user_id_cache_valid = True
                print(f"DEBUG Favorites: Current user ID: {user_id}")
                return user_id
            else:
                print("DEBUG Favorites: No user found in response")
                self._cached_user_id = None
                self._user_id_cache_valid = True
                return None
        except Exception as e:
            print(f"DEBUG Favorites: Error getting user: {e}")
            # Invalidate cache on error
            self._user_id_cache_valid = False
            return None

    def get_favorites(self, force_refresh=False) -> List[Dict]:
        """Return the list of favorite places."""
        # Store old user ID before fetching new one to detect changes
        old_user_id = self._cached_user_id
        
        # Force refresh user ID if forcing refresh or if we need to check for user changes
        user_id = self._get_current_user_id(force_refresh=force_refresh)
        
        # Check for user session change
        if user_id != old_user_id:
            print(f"Debug: User changed from {old_user_id} to {user_id}. Refreshing favorites.")
            self._supabase_fetch_done = False
            # If logged out, reset to local favorites immediately
            if not user_id:
                 self._load_local_favorites()
        
        if user_id:
            # If we haven't fetched from Supabase yet, or forced, do it now
            if not self._supabase_fetch_done or force_refresh:
                try:
                    print(f"DEBUG Favorites: Fetching from Supabase (force_refresh={force_refresh}, fetch_done={self._supabase_fetch_done})")
                    response = self.client.table("favorites").select("*").eq("user_id", user_id).execute()
                    # Assume 'data' column holds the place dict
                    self._favorites = [item["data"] for item in response.data]
                    self._supabase_fetch_done = True
                    # Mark as online since fetch succeeded
                    mark_online()
                    # Save to client storage for offline access
                    self._save_to_client_storage()
                    print(f"DEBUG Favorites: Fetched {len(self._favorites)} favorites from Supabase")
                except Exception as e:
                    print(f"ERROR Favorites: Error fetching favorites from Supabase: {e}")
                    import traceback
                    traceback.print_exc()
                    # Check if this is a network error
                    error_str = str(e).lower()
                    if "network" in error_str or "connection" in error_str or "timeout" in error_str:
                        mark_offline()
                    # Try to load from client storage cache if we have nothing
                    if not self._favorites:
                        self._load_from_client_storage()
            else:
                print(f"DEBUG Favorites: Using cached favorites ({len(self._favorites)} items)")
            return self._favorites
        
        return self._favorites

    def is_favorite(self, place_id: str) -> bool:
        """Check if a place is in favorites."""
        # Ensure we have loaded favorites at least once if logged in
        # Use cached user ID to avoid unnecessary API call
        user_id = self._get_current_user_id(force_refresh=False)
        if not self._supabase_fetch_done and user_id:
            self.get_favorites()
        
        # Check both place_id and id fields
        for f in self._favorites:
            fav_place_id = f.get("place_id") or f.get("id")
            if fav_place_id == place_id:
                return True
        return False

    def add_favorite(self, place: Dict):
        """Add a place to favorites if not already present."""
        place_id = place.get("place_id") or place.get("id")
        if not place_id:
            print("Cannot favorite a place without an ID")
            return False

        if self.is_favorite(place_id):
            print(f"DEBUG Favorites: Place {place_id} is already a favorite")
            return True

        # Prepare the item
        types = place.get("types", [])
        fav_item = {
            "place_id": place_id,
            "name": place.get("name"),
            "formatted_address": place.get("formatted_address") or place.get("address"),
            "rating": place.get("rating"),
            "types": types,
            "photos": place.get("photos", []),
            "image_url": place.get("image_url"),
            "is_favorite": True
        }
        
        user_id = self._get_current_user_id(force_refresh=False)
        if user_id:
            try:
                # Insert into Supabase first
                data_payload = {
                    "user_id": user_id,
                    "place_id": place_id,
                    "data": fav_item
                }
                result = self.client.table("favorites").insert(data_payload).execute()
                print(f"DEBUG Favorites: Successfully added to Supabase: {place.get('name')} (ID: {place_id})")
                
                # Only update local cache after successful Supabase insert
                self._favorites.append(fav_item)
                # Mark that we need to refresh from Supabase to ensure consistency
                # But keep the local cache updated for immediate UI response
                return True
            except Exception as e:
                print(f"ERROR Favorites: Failed to add to Supabase: {e}")
                import traceback
                traceback.print_exc()
                # Don't add to local cache if Supabase insert failed
                return False
        else:
            # Local fallback persistence (user not logged in)
            print(f"DEBUG Favorites: User not logged in, saving locally: {place.get('name')}")
            self._favorites.append(fav_item)
            self._save_local_favorites()
            return True

    def remove_favorite(self, place_id: str):
        """Remove a place from favorites."""
        user_id = self._get_current_user_id(force_refresh=False)
        if user_id:
            try:
                # Remove from Supabase first
                result = self.client.table("favorites").delete().eq("user_id", user_id).eq("place_id", place_id).execute()
                print(f"DEBUG Favorites: Successfully removed from Supabase: {place_id}")
                
                # Update local cache after successful removal
                self._favorites = [f for f in self._favorites if (f.get("place_id") != place_id and f.get("id") != place_id)]
            except Exception as e:
                print(f"ERROR Favorites: Failed to remove from Supabase: {e}")
                import traceback
                traceback.print_exc()
                # Don't update local cache if Supabase removal failed
        else:
            print(f"DEBUG Favorites: User not logged in, removing locally: {place_id}")
            self._favorites = [f for f in self._favorites if (f.get("place_id") != place_id and f.get("id") != place_id)]
            self._save_local_favorites()

    def toggle_favorite(self, place: Dict) -> bool:
        """
        Toggle the favorite status of a place.
        Returns the new status (True for favorite, False for not).
        """
        place_id = place.get("place_id") or place.get("id")
        if not place_id:
            print("ERROR: Cannot toggle favorite - no place_id")
            return False
        
        current_status = self.is_favorite(place_id)
        print(f"DEBUG Toggle: Place {place_id} current status: {current_status}")
        
        if current_status:
            self.remove_favorite(place_id)
            new_status = False
        else:
            success = self.add_favorite(place)
            new_status = success  # Returns True if successfully added
            
        # Verify the change
        verified_status = self.is_favorite(place_id)
        if verified_status != new_status:
            print(f"WARNING: Status mismatch after toggle. Expected: {new_status}, Got: {verified_status}")
            # Force a refresh from Supabase if logged in
            user_id = self._get_current_user_id()
            if user_id:
                try:
                    self.get_favorites(force_refresh=True)
                    verified_status = self.is_favorite(place_id)
                    print(f"DEBUG Toggle: After refresh, status is: {verified_status}")
                except Exception as e:
                    print(f"ERROR: Failed to refresh favorites: {e}")
        
        return verified_status
