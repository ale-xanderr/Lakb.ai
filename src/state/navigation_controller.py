"""
Navigation Controller - Manages navigation and routing state.

Handles route changes, navigation history, and selected place for destination view.
"""

from typing import Optional, Dict, Callable
import flet as ft


class NavigationController:
    """
    Controller for managing navigation and routing state.
    """
    
    def __init__(self, page: ft.Page):
        self.page = page
        self._current_route: str = "/"
        self._current_nav_index: int = 0
        self._selected_place: Optional[Dict] = None
        
        # Callbacks
        self._on_route_change: Optional[Callable] = None
        self._on_nav_change: Optional[Callable] = None
    
    def set_on_route_change(self, callback: Callable):
        """Set callback to be called when route changes."""
        self._on_route_change = callback
    
    def set_on_nav_change(self, callback: Callable):
        """Set callback to be called when navigation index changes."""
        self._on_nav_change = callback
    
    def _notify_route_change(self):
        """Notify listeners of route change."""
        if self._on_route_change:
            try:
                self._on_route_change()
            except Exception as e:
                print(f"Error in route change callback: {e}")
    
    def _notify_nav_change(self):
        """Notify listeners of nav change."""
        if self._on_nav_change:
            try:
                self._on_nav_change()
            except Exception as e:
                print(f"Error in nav change callback: {e}")
    
    @property
    def current_route(self) -> str:
        """Get current route."""
        return self._current_route
    
    @current_route.setter
    def current_route(self, value: str):
        """Set current route."""
        self._current_route = value
        self._notify_route_change()
    
    @property
    def current_nav_index(self) -> int:
        """Get current navigation bar index."""
        return self._current_nav_index
    
    @current_nav_index.setter
    def current_nav_index(self, value: int):
        """Set current navigation bar index."""
        self._current_nav_index = value
        self._notify_nav_change()
    
    @property
    def selected_place(self) -> Optional[Dict]:
        """Get currently selected place for destination view."""
        return self._selected_place
    
    @selected_place.setter
    def selected_place(self, value: Optional[Dict]):
        """Set selected place."""
        self._selected_place = value
    
    def navigate_to(self, route: str):
        """Navigate to a route."""
        self.page.go(route)
        self._current_route = route
    
    def navigate_home(self):
        """Navigate to home."""
        self.navigate_to("/")
        self.current_nav_index = 0
    
    def navigate_favorites(self):
        """Navigate to favorites."""
        self.navigate_to("/favorites")
        self.current_nav_index = 1
    
    def navigate_plans(self):
        """Navigate to plans."""
        self.navigate_to("/plans")
        self.current_nav_index = 2
    
    def navigate_settings(self):
        """Navigate to settings."""
        self.navigate_to("/settings")
        self.current_nav_index = 3
    
    def navigate_destination(self, place: Dict):
        """Navigate to destination view with a place."""
        self.selected_place = place
        self.navigate_to("/destination")
    
    def navigate_back(self):
        """Navigate back based on current navigation index."""
        if self._current_nav_index == 1:
            self.navigate_favorites()
        elif self._current_nav_index == 2:
            self.navigate_plans()
        else:
            self.navigate_home()
    
    def reset(self):
        """Reset navigation state."""
        self._current_route = "/"
        self._current_nav_index = 0
        self._selected_place = None
