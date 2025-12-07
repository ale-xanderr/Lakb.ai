"""
Favorites State Controller - Manages favorites state.

Handles favorites data, filtering, and search within favorites.
"""

from typing import Optional, List, Dict, Callable
import flet as ft


class FavoritesStateController:
    """
    Controller for managing favorites state.
    """
    
    def __init__(self, page: ft.Page):
        self.page = page
        
        # State
        self._favorites_data: List[Dict] = []
        self._filter_query: str = ""
        self._filter_category: Optional[str] = None
        
        # UI References
        self._grid_ref: Optional[ft.Ref[ft.GridView]] = None
        self._search_bar_ref: Optional[ft.Ref[ft.SearchBar]] = None
        self._error_dialog_ref: Optional[ft.Ref[ft.Container]] = None
        
        # Callbacks
        self._on_state_change: Optional[Callable] = None
    
    def set_ui_refs(self, grid_ref=None, search_bar_ref=None, error_dialog_ref=None):
        """Set UI references for direct updates."""
        if grid_ref:
            self._grid_ref = grid_ref
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
                print(f"Error in favorites state change callback: {e}")
    
    # Data properties
    @property
    def favorites_data(self) -> List[Dict]:
        """Get current favorites data."""
        return self._favorites_data
    
    @favorites_data.setter
    def favorites_data(self, value: List[Dict]):
        """Set favorites data."""
        self._favorites_data = value
        self._notify_state_change()
    
    @property
    def filter_query(self) -> str:
        """Get current filter query."""
        return self._filter_query
    
    @filter_query.setter
    def filter_query(self, value: str):
        """Set filter query."""
        self._filter_query = value
        self._notify_state_change()
    
    @property
    def filter_category(self) -> Optional[str]:
        """Get current filter category."""
        return self._filter_category
    
    @filter_category.setter
    def filter_category(self, value: Optional[str]):
        """Set filter category."""
        self._filter_category = value
        self._notify_state_change()
    
    def get_filtered_favorites(self) -> List[Dict]:
        """Get filtered favorites based on current query and category."""
        filtered = []
        q = self._filter_query.lower().strip()
        cat = self._filter_category
        
        for item in self._favorites_data:
            # Text search
            name = (item.get("name") or item.get("title") or "").lower()
            addr = (item.get("formatted_address") or item.get("address") or "").lower()
            match_query = (not q) or (q in name) or (q in addr)
            
            # Category filter
            match_category = True
            if cat:
                types = item.get("types", [])
                cat_normalized = cat.lower().replace(" ", "")
                
                if types:
                    match_category = any(
                        cat_normalized in t.lower().replace("_", "") or
                        cat_normalized == t.lower().replace("_", "")
                        for t in types
                    )
                else:
                    match_category = (cat.lower() in name) or (cat.lower() in addr)
            
            if match_query and match_category:
                filtered.append(item)
        
        return filtered
    
    def reset_filters(self):
        """Reset all filters."""
        self._filter_query = ""
        self._filter_category = None
        self._notify_state_change()
    
    def reset(self):
        """Reset all state."""
        self._favorites_data = []
        self.reset_filters()
        self._notify_state_change()
