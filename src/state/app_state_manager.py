"""
App State Manager - Manages application-level state.

Handles theme, app initialization, and global settings.
"""

from typing import Optional, Callable
import flet as ft


class AppStateManager:
    """
    Manages application-level state including theme, initialization status, and global settings.
    Persists theme preferences to client storage.
    """
    
    def __init__(self, page: ft.Page):
        self.page = page
        self._theme_mode: ft.ThemeMode = ft.ThemeMode.SYSTEM
        self._initialized = False
        
        # Load theme preference from storage if available
        self._load_theme_preference()
    
    def _load_theme_preference(self):
        """Load theme preference from client storage."""
        if hasattr(self.page, 'client_storage'):
            try:
                dark_mode = self.page.client_storage.get("dark_mode")
                if dark_mode == "1":
                    self._theme_mode = ft.ThemeMode.DARK
                elif dark_mode == "0":
                    self._theme_mode = ft.ThemeMode.LIGHT
                else:
                    self._theme_mode = ft.ThemeMode.SYSTEM
            except Exception:
                pass
    
    def initialize(self):
        """Initialize the app state manager."""
        if self._initialized:
            return
        
        # Apply theme
        self.page.theme_mode = self._theme_mode
        self._initialized = True
    
    @property
    def theme_mode(self) -> ft.ThemeMode:
        """Get current theme mode."""
        return self._theme_mode
    
    def set_theme_mode(self, mode: ft.ThemeMode):
        """Set theme mode and persist to storage."""
        self._theme_mode = mode
        self.page.theme_mode = mode
        
        # Persist to storage
        if hasattr(self.page, 'client_storage'):
            try:
                if mode == ft.ThemeMode.DARK:
                    self.page.client_storage.set("dark_mode", "1")
                elif mode == ft.ThemeMode.LIGHT:
                    self.page.client_storage.set("dark_mode", "0")
                else:
                    self.page.client_storage.set("dark_mode", "system")
            except Exception:
                pass
        
        self.page.update()
    
    def toggle_theme(self):
        """Toggle between light and dark themes."""
        if self._theme_mode == ft.ThemeMode.DARK:
            self.set_theme_mode(ft.ThemeMode.LIGHT)
        else:
            self.set_theme_mode(ft.ThemeMode.DARK)
    
    def is_initialized(self) -> bool:
        """Check if the app state manager is initialized."""
        return self._initialized
