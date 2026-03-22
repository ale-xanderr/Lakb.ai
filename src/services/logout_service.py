"""
Logout Service - Centralized orchestrator for logging a user out and wiping caches.

Ensures that when a user logs out, we not only remove disk tokens but 
also clear any in-memory singletons containing the previous user's data.
"""

import flet as ft
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from state.service_manager import ServiceManager

class LogoutService:
    """
    Service responsible for orchestrating a complete logout.
    Clears Supabase session, local storage tokens, and all in-memory singleton caches.
    """
    
    def __init__(self, service_manager: 'ServiceManager'):
        """
        Initialize with a reference to the centralized service manager
        so we can access and clear other services.
        """
        self._sm = service_manager
        
    def logout(self, page: ft.Page = None):
        """
        Perform a complete application logout sequence.
        
        Args:
            page: the Flet Page instance (required to wipe client_storage)
        """
        # 1. Sign out of Supabase and clear disk tokens via AuthService
        if self._sm._auth_service:
            print("LogoutService: Signing out of Supabase Auth...")
            self._sm.auth_service.sign_out(page)
            
        # 2. Wipe in-memory active singletons to prevent "ghost" data
        if self._sm._favorites_service:
            print("LogoutService: Clearing Favorites Cache...")
            self._sm.favorites_service.clear_cache()
            
        if self._sm._plans_service:
            print("LogoutService: Clearing Plans Cache...")
            self._sm.plans_service.clear_cache()
            
        # 3. Reset manager services that don't auto-handle state
        print("LogoutService: Resetting ServiceManager tracked states...")
        self._sm.reset()
        
        print("LogoutService: Complete logout sequence finished successfully.")
