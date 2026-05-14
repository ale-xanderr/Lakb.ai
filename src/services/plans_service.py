"""
Plans Service - Manages trip plans with local caching for offline support.

Provides methods to fetch plans from Supabase and cache them locally
for offline viewing. Caches are synchronized when connectivity returns.
"""

import json
import flet as ft
from typing import List, Dict, Optional
from core.supabase_client import get_supabase_client
from core.connectivity import get_connectivity_state, mark_offline, mark_online


class PlansService:
    """
    Service for managing trip plans with offline caching support.
    
    Fetches plans from Supabase when online and caches them locally
    using Flet's client_storage for offline access.
    """
    
    CACHE_KEY = "user_plans_cache"
    
    def __init__(self):
        self.client = get_supabase_client()
        self._cached_plans: List[Dict] = []
        self._page: Optional[ft.Page] = None
    
    def initialize(self, page: ft.Page):
        """
        Initialize the service with a page reference for storage access.
        
        Args:
            page: The Flet page instance with client_storage
        """
        self._page = page
        # Load cached plans on initialization
        self._load_from_cache()
    
    def _get_current_user_id(self) -> Optional[str]:
        """Get the current authenticated user's ID."""
        if not self.client:
            return None
        
        try:
            response = self.client.auth.get_user()
            if response and hasattr(response, 'user') and response.user:
                return response.user.id
        except Exception as e:
            print(f"Error getting user ID for plans: {e}")
            # Mark as offline if this looks like a network error
            if "network" in str(e).lower() or "connection" in str(e).lower():
                mark_offline()
        
        return None
    
    def _load_from_cache(self):
        """Load plans from local cache (client_storage)."""
        if not self._page or not hasattr(self._page, 'client_storage'):
            return
        
        try:
            cached_data = self._page.client_storage.get(self.CACHE_KEY)
            if cached_data:
                self._cached_plans = json.loads(cached_data)
                print(f"Loaded {len(self._cached_plans)} plans from cache")
        except Exception as e:
            print(f"Error loading plans from cache: {e}")
            self._cached_plans = []
    
    def _save_to_cache(self, plans: List[Dict]):
        """
        Save plans to local cache (client_storage).
        
        Args:
            plans: List of plan dictionaries to cache
        """
        if not self._page or not hasattr(self._page, 'client_storage'):
            return
        
        try:
            self._page.client_storage.set(self.CACHE_KEY, json.dumps(plans))
            self._cached_plans = plans
            print(f"Saved {len(plans)} plans to cache")
        except Exception as e:
            print(f"Error saving plans to cache: {e}")
    
    def get_plans(self, force_refresh: bool = False) -> tuple[List[Dict], bool]:
        """
        Get user's trip plans, using cache when offline.
        
        Args:
            force_refresh: If True, always try to fetch from Supabase first
            
        Returns:
            Tuple of (list of plans, is_from_cache: bool)
        """
        if not self.client:
            print("Supabase client not available, using cached plans")
            return self._cached_plans, True
        
        # Try to fetch from Supabase
        try:
            user_id = self._get_current_user_id()
            if not user_id:
                # No user - might be offline or not authenticated
                connectivity = get_connectivity_state()
                if not connectivity.is_online or self._cached_plans:
                    return self._cached_plans, True
                return [], False
            
            # Fetch from Supabase
            response = self.client.table("plans").select("*").eq(
                "user_id", user_id
            ).order("created_at", desc=True).execute()
            
            # Mark as online since request succeeded
            mark_online()
            
            plans = []
            if response.data:
                for plan_data in response.data:
                    data = plan_data.get("data", {})
                    status = data.get("status", "completed")
                    itinerary = data.get("itinerary", [])
                    is_generating = status == "generating" or (not itinerary or len(itinerary) == 0)
                    
                    plan = {
                        "id": plan_data.get("id"),
                        "title": plan_data.get("title", "Untitled Plan"),
                        "description": plan_data.get("description", ""),
                        "image_url": plan_data.get("image_url"),
                        "is_generating": is_generating,
                        "data": data
                    }
                    plans.append(plan)
            
            # Update cache with fresh data
            self._save_to_cache(plans)
            return plans, False
            
        except Exception as e:
            print(f"Error fetching plans from Supabase: {e}")
            
            # Check if this is a network error
            error_str = str(e).lower()
            if "network" in error_str or "connection" in error_str or "timeout" in error_str:
                mark_offline()
            
            # Return cached plans on error
            if self._cached_plans:
                print(f"Returning {len(self._cached_plans)} cached plans due to error")
                return self._cached_plans, True
            
            return [], True
    
    def get_cached_plans(self) -> List[Dict]:
        """
        Get plans from local cache only (no network request).
        
        Returns:
            List of cached plan dictionaries
        """
        return self._cached_plans
    
    def clear_cache(self):
        """Clear the local plans cache."""
        self._cached_plans = []
        if self._page and hasattr(self._page, 'client_storage'):
            try:
                self._page.client_storage.remove(self.CACHE_KEY)
                print("Plans cache cleared")
            except Exception as e:
                print(f"Error clearing plans cache: {e}")
    
    def update_cache_with_plan(self, plan: Dict):
        """
        Add or update a single plan in the cache.
        
        Args:
            plan: Plan dictionary to add/update
        """
        plan_id = plan.get("id")
        if not plan_id:
            return
        
        # Remove existing plan with same ID
        self._cached_plans = [p for p in self._cached_plans if p.get("id") != plan_id]
        
        # Add new plan at the beginning (most recent)
        self._cached_plans.insert(0, plan)
        
        # Save updated cache
        self._save_to_cache(self._cached_plans)
    
    def remove_from_cache(self, plan_id: str):
        """
        Remove a plan from the cache.
        
        Args:
            plan_id: ID of the plan to remove
        """
        self._cached_plans = [p for p in self._cached_plans if p.get("id") != plan_id]
        self._save_to_cache(self._cached_plans)
