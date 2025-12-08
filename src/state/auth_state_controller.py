"""
Auth State Controller - Manages authentication state.

Handles user session, authentication status, and auth-related operations.
"""

from typing import Optional, Callable
import flet as ft


class AuthStateController:
    """
    Controller for managing authentication state.
    Handles user session, authentication status (authenticated, guest, loading), and notifies listeners of changes.
    """
    
    def __init__(self, page: ft.Page):
        self.page = page
        self._user = None
        self._is_authenticated = False
        self._is_guest = False
        self._is_loading = False
        
        # Callbacks
        self._on_auth_state_change: Optional[Callable] = None
    
    def set_on_auth_state_change(self, callback: Callable):
        """Set callback to be called when auth state changes."""
        self._on_auth_state_change = callback
    
    def _notify_auth_state_change(self):
        """Notify listeners of auth state change."""
        if self._on_auth_state_change:
            try:
                self._on_auth_state_change()
            except Exception as e:
                print(f"Error in auth state change callback: {e}")
    
    @property
    def user(self):
        """Get current user."""
        return self._user
    
    @user.setter
    def user(self, value):
        """Set current user."""
        self._user = value
        self._is_authenticated = value is not None
        self._notify_auth_state_change()
    
    @property
    def is_authenticated(self) -> bool:
        """Check if user is authenticated."""
        return self._is_authenticated
    
    @property
    def is_guest(self) -> bool:
        """Check if user is a guest."""
        return self._is_guest
    
    @is_guest.setter
    def is_guest(self, value: bool):
        """Set guest status."""
        self._is_guest = value
    
    @property
    def is_loading(self) -> bool:
        """Check if auth operation is in progress."""
        return self._is_loading
    
    @is_loading.setter
    def is_loading(self, value: bool):
        """Set loading state."""
        self._is_loading = value
    
    def set_authenticated(self, user):
        """Set user as authenticated."""
        self._user = user
        self._is_authenticated = True
        self._is_guest = False
        self._is_loading = False
        self._notify_auth_state_change()
    
    def set_guest(self):
        """Set user as guest (unauthenticated but can use app)."""
        self._user = None
        self._is_authenticated = False
        self._is_guest = True
        self._is_loading = False
        self._notify_auth_state_change()
    
    def set_unauthenticated(self):
        """Set user as unauthenticated."""
        self._user = None
        self._is_authenticated = False
        self._is_guest = False
        self._is_loading = False
        self._notify_auth_state_change()
    
    def reset(self):
        """Reset auth state."""
        self.set_unauthenticated()
