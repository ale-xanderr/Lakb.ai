"""
Places State Controller - Manages places/search state.

Handles places data, search queries, filters, location, and pagination.
"""

from typing import Optional, List, Dict, Callable
import flet as ft


class PlacesStateController:
    """
    Controller for managing places and search state.
    Handles search results, pagination tokens, search queries, filters (type, location), and recent search history.
    """
    
    def __init__(self, page: ft.Page):
        self.page = page
        
        # Load recent searches from storage
        stored_history = []
        if hasattr(page, 'client_storage'):
            try:
                stored_history = page.client_storage.get("recent_searches") or []
            except Exception:
                pass
        
        # State
        self._data: List[Dict] = []
        self._next_page_token: Optional[str] = None
        self._query: Optional[str] = None
        self._place_type: Optional[str] = None
        self._location: Optional[str] = None  # "lat,lng" format
        self._city_name: Optional[str] = None
        self._device_location: Optional[str] = None
        self._device_city: Optional[str] = None
        self._recent_searches: List[str] = stored_history
        
        # UI References (optional, for direct UI updates)
        self._places_column_ref: Optional[ft.Ref[ft.Column]] = None
        self._load_more_btn_ref: Optional[ft.Ref[ft.Container]] = None
        self._section_title_ref: Optional[ft.Ref[ft.Text]] = None
        self._search_bar_ref: Optional[ft.Ref[ft.SearchBar]] = None
        self._error_dialog_ref: Optional[ft.Ref[ft.Container]] = None
        
        # Callbacks
        self._on_state_change: Optional[Callable] = None
    
    def set_ui_refs(self, places_column_ref=None, load_more_btn_ref=None, 
                     section_title_ref=None, search_bar_ref=None, error_dialog_ref=None):
        """Set UI references for direct updates."""
        if places_column_ref:
            self._places_column_ref = places_column_ref
        if load_more_btn_ref:
            self._load_more_btn_ref = load_more_btn_ref
        if section_title_ref:
            self._section_title_ref = section_title_ref
        if search_bar_ref:
            self._search_bar_ref = search_bar_ref
        if error_dialog_ref:
            self._error_dialog_ref = error_dialog_ref
    
    def set_on_state_change(self, callback: Callable):
        """Set callback to be called when state changes."""
        self._on_state_change = callback
    
    def _notify_state_change(self):
        """Notify listeners of state change."""
        if self._on_state_change:
            try:
                self._on_state_change()
            except Exception as e:
                print(f"Error in state change callback: {e}")
    
    # Data properties
    @property
    def data(self) -> List[Dict]:
        """Get current places data."""
        return self._data
    
    @data.setter
    def data(self, value: List[Dict]):
        """Set places data."""
        self._data = value
        self._notify_state_change()
    
    @property
    def next_page_token(self) -> Optional[str]:
        """Get next page token for pagination."""
        return self._next_page_token
    
    @next_page_token.setter
    def next_page_token(self, value: Optional[str]):
        """Set next page token."""
        self._next_page_token = value
        self._notify_state_change()
    
    @property
    def query(self) -> Optional[str]:
        """Get current search query."""
        return self._query
    
    @query.setter
    def query(self, value: Optional[str]):
        """Set search query."""
        self._query = value
        self._notify_state_change()
    
    @property
    def place_type(self) -> Optional[str]:
        """Get current place type filter."""
        return self._place_type
    
    @place_type.setter
    def place_type(self, value: Optional[str]):
        """Set place type filter."""
        self._place_type = value
        self._notify_state_change()
    
    @property
    def location(self) -> Optional[str]:
        """Get current location (lat,lng format)."""
        return self._location
    
    @location.setter
    def location(self, value: Optional[str]):
        """Set location."""
        self._location = value
        self._notify_state_change()
    
    @property
    def city_name(self) -> Optional[str]:
        """Get current city name."""
        return self._city_name
    
    @city_name.setter
    def city_name(self, value: Optional[str]):
        """Set city name."""
        self._city_name = value
        self._notify_state_change()
    
    @property
    def device_location(self) -> Optional[str]:
        """Get device location."""
        return self._device_location
    
    @device_location.setter
    def device_location(self, value: Optional[str]):
        """Set device location."""
        self._device_location = value
    
    @property
    def device_city(self) -> Optional[str]:
        """Get device city."""
        return self._device_city
    
    @device_city.setter
    def device_city(self, value: Optional[str]):
        """Set device city."""
        self._device_city = value
    
    @property
    def recent_searches(self) -> List[str]:
        """Get recent searches history."""
        return self._recent_searches
    
    def add_recent_search(self, query: str):
        """Add a query to recent searches."""
        if not query or not query.strip():
            return
        
        query = query.strip()
        
        # Remove if exists to move to top
        if query in self._recent_searches:
            self._recent_searches.remove(query)
        
        self._recent_searches.append(query)
        
        # Keep only last 5
        if len(self._recent_searches) > 5:
            self._recent_searches.pop(0)
        
        # Persist to storage
        if hasattr(self.page, 'client_storage'):
            try:
                self.page.client_storage.set("recent_searches", self._recent_searches)
            except Exception:
                pass
        
        self._notify_state_change()
    
    def clear_recent_searches(self):
        """Clear recent searches history."""
        self._recent_searches = []
        if hasattr(self.page, 'client_storage'):
            try:
                self.page.client_storage.remove("recent_searches")
            except Exception:
                pass
        self._notify_state_change()
    
    def reset_to_device_location(self):
        """Reset state to device location."""
        self._location = self._device_location
        self._city_name = self._device_city
        self._query = ""
        self._place_type = None
        
        # Clear search bar if ref is set
        if self._search_bar_ref and self._search_bar_ref.current:
            self._search_bar_ref.current.value = ""
            if self._search_bar_ref.current.page:
                try:
                    self._search_bar_ref.current.close_view()
                    self._search_bar_ref.current.update()
                except Exception:
                    pass
        
        self._notify_state_change()
    
    def reset(self):
        """Reset all state (except device location and recent searches)."""
        self._data = []
        self._next_page_token = None
        self._query = None
        self._place_type = None
        self._location = None
        self._city_name = None
        self._notify_state_change()
    
    def get_section_title(self) -> str:
        """Get formatted section title based on current state."""
        q = self._query
        t = self._place_type
        city = self._city_name
        
        title_text = "Popular Places"
        
        if q:
            if " in " in q.lower():
                if q.lower().startswith("popular"):
                    title_text = q
                else:
                    title_text = f"Popular {q}"
            else:
                title_text = f"Results for {q}"
        elif t and city:
            title_text = f"Popular {t}s in {city}"
        elif city:
            title_text = f"Popular in {city}"
        elif t:
            title_text = f"Popular {t}s"
        
        import string
        return string.capwords(title_text)
    
    def get_state_dict(self) -> Dict:
        """Get current state as a dictionary (for compatibility with existing code)."""
        return {
            "data": self._data,
            "next_page_token": self._next_page_token,
            "query": self._query,
            "type": self._place_type,
            "location": self._location,
            "city_name": self._city_name,
            "device_location": self._device_location,
            "device_city": self._device_city,
            "recent_searches": self._recent_searches
        }
