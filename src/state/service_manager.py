"""
Service Manager - Centralized service instance management.

This module provides a singleton pattern for service instances to avoid
creating multiple instances across the application.
"""

from typing import Optional
from services.api_service import APIService
from services.auth_service import AuthService
from services.favorites_service import FavoritesService
from services.profile_service import ProfileService
from services.geolocation_service import GeolocationService
import flet as ft


class ServiceManager:
    """
    Centralized manager for all service instances.
    Ensures services are created once and reused across the application.
    """
    
    _instance: Optional['ServiceManager'] = None
    _initialized = False
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        if not self._initialized:
            self._api_service: Optional[APIService] = None
            self._auth_service: Optional[AuthService] = None
            self._favorites_service: Optional[FavoritesService] = None
            self._profile_service: Optional[ProfileService] = None
            self._geolocation_service: Optional[GeolocationService] = None
            self._page: Optional[ft.Page] = None
            ServiceManager._initialized = True
    
    def initialize(self, page: ft.Page):
        """Initialize the service manager with a Flet page instance."""
        self._page = page
    
    @property
    def api_service(self) -> APIService:
        """Get or create APIService instance."""
        if self._api_service is None:
            self._api_service = APIService()
        return self._api_service
    
    @property
    def auth_service(self) -> AuthService:
        """Get or create AuthService instance."""
        if self._auth_service is None:
            self._auth_service = AuthService()
        return self._auth_service
    
    @property
    def favorites_service(self) -> FavoritesService:
        """Get or create FavoritesService instance."""
        if self._favorites_service is None:
            self._favorites_service = FavoritesService()
        return self._favorites_service
    
    @property
    def profile_service(self) -> ProfileService:
        """Get or create ProfileService instance."""
        if self._profile_service is None:
            self._profile_service = ProfileService()
        return self._profile_service
    
    @property
    def geolocation_service(self) -> Optional[GeolocationService]:
        """Get GeolocationService instance (may be None if not initialized)."""
        return self._geolocation_service
    
    def create_geolocation_service(self, on_location_update=None) -> GeolocationService:
        """
        Create and return a GeolocationService instance.
        Note: GeolocationService requires cleanup, so we manage it carefully.
        """
        if self._page is None:
            raise ValueError("ServiceManager must be initialized with a page before creating GeolocationService")
        
        # Clean up existing service if any
        if self._geolocation_service is not None:
            self._geolocation_service.cleanup()
        
        self._geolocation_service = GeolocationService(
            self._page,
            on_location_update=on_location_update
        )
        return self._geolocation_service
    
    def cleanup_geolocation_service(self):
        """Clean up the GeolocationService if it exists."""
        if self._geolocation_service is not None:
            self._geolocation_service.cleanup()
            self._geolocation_service = None
    
    def reset(self):
        """Reset all services (useful for logout or app reset)."""
        self.cleanup_geolocation_service()
        # Note: We don't reset other services as they may be needed
        # Auth and favorites services handle their own state
