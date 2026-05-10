"""
Interaction Service - Manages user interactions like swiping and visited places.

Handles database operations for the `swipes` and `visited_places` tables,
allowing the AI engine to learn from user preferences and avoid recommending
places the user has already visited.
"""

from typing import List, Dict, Optional, Any
from core.supabase_client import get_supabase_client

class InteractionService:
    """Service for managing user swipes and visited places."""
    
    def __init__(self):
        self.client = get_supabase_client()
        
    def _get_current_user_id(self) -> Optional[str]:
        if not self.client:
            return None
        try:
            response = self.client.auth.get_user()
            if response and hasattr(response, 'user') and response.user:
                return response.user.id
        except Exception as e:
            print(f"Error getting user ID in InteractionService: {e}")
        return None

    # --- Swipes ---
    def record_swipe(self, place: Dict[str, Any], action: str) -> bool:
        """
        Record a user's swipe action ('like' or 'dislike') on a place.
        """
        if action not in ('like', 'dislike'):
            print(f"Invalid swipe action: {action}")
            return False
            
        user_id = self._get_current_user_id()
        if not user_id or not self.client:
            return False
            
        place_id = place.get("place_id") or place.get("id")
        if not place_id:
            return False
            
        try:
            # Upsert the swipe record
            data = {
                "user_id": user_id,
                "place_id": place_id,
                "place_data": place,
                "action": action
            }
            # The Supabase python client doesn't have a direct upsert method that handles
            # ON CONFLICT perfectly without specifying the column, but since we have a UNIQUE constraint,
            # we can use upsert.
            self.client.table("swipes").upsert(data, on_conflict="user_id, place_id").execute()
            return True
        except Exception as e:
            print(f"Error recording swipe: {e}")
            return False

    def get_swipes(self, action: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Get the user's swiped places, optionally filtered by action.
        """
        user_id = self._get_current_user_id()
        if not user_id or not self.client:
            return []
            
        try:
            query = self.client.table("swipes").select("*").eq("user_id", user_id)
            if action:
                query = query.eq("action", action)
                
            response = query.execute()
            return response.data if response.data else []
        except Exception as e:
            print(f"Error fetching swipes: {e}")
            return []

    def get_liked_places(self) -> List[Dict[str, Any]]:
        """Convenience method to get liked places."""
        return self.get_swipes(action="like")

    # --- Visited Places (Mark as Done) ---
    def mark_visited(self, place: Dict[str, Any], visited: bool = True) -> bool:
        """
        Mark or unmark a place as visited.
        """
        user_id = self._get_current_user_id()
        if not user_id or not self.client:
            return False
            
        place_id = place.get("place_id") or place.get("id")
        if not place_id:
            return False
            
        try:
            if visited:
                data = {
                    "user_id": user_id,
                    "place_id": place_id,
                    "place_data": place
                }
                self.client.table("visited_places").upsert(data, on_conflict="user_id, place_id").execute()
            else:
                self.client.table("visited_places").delete().eq("user_id", user_id).eq("place_id", place_id).execute()
            return True
        except Exception as e:
            print(f"Error marking place as visited: {e}")
            return False

    def get_visited_places(self) -> List[Dict[str, Any]]:
        """
        Get the user's visited places.
        """
        user_id = self._get_current_user_id()
        if not user_id or not self.client:
            return []
            
        try:
            response = self.client.table("visited_places").select("*").eq("user_id", user_id).execute()
            return response.data if response.data else []
        except Exception as e:
            print(f"Error fetching visited places: {e}")
            return []

    def is_visited(self, place_id: str) -> bool:
        """
        Check if a specific place has been marked as visited.
        """
        user_id = self._get_current_user_id()
        if not user_id or not self.client:
            return False
            
        try:
            response = self.client.table("visited_places").select("id").eq("user_id", user_id).eq("place_id", place_id).execute()
            return len(response.data) > 0 if response.data else False
        except Exception as e:
            print(f"Error checking if place is visited: {e}")
            return False
