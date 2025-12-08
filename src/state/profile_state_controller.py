"""
Profile State Controller - Manages user profile state.

Handles profile data, updates, and profile-related operations.
"""

from typing import Optional, Dict, Callable
import flet as ft


class ProfileStateController:
    """
    Controller for managing user profile state.
    Handles profile data (name, email, avatar), loading/saving states, and notifies listeners of changes.
    """
    
    def __init__(self, page: ft.Page):
        self.page = page
        self._profile: Optional[Dict] = None
        self._is_loading = False
        self._is_saving = False
        
        # Callbacks
        self._on_profile_change: Optional[Callable] = None
    
    def set_on_profile_change(self, callback: Callable):
        """Set callback to be called when profile changes."""
        self._on_profile_change = callback
    
    def _notify_profile_change(self):
        """Notify listeners of profile change."""
        if self._on_profile_change:
            try:
                self._on_profile_change()
            except Exception as e:
                print(f"Error in profile change callback: {e}")
    
    @property
    def profile(self) -> Optional[Dict]:
        """Get current profile data."""
        return self._profile
    
    @profile.setter
    def profile(self, value: Optional[Dict]):
        """Set profile data."""
        self._profile = value
        self._notify_profile_change()
    
    @property
    def is_loading(self) -> bool:
        """Check if profile is being loaded."""
        return self._is_loading
    
    @is_loading.setter
    def is_loading(self, value: bool):
        """Set loading state."""
        self._is_loading = value
    
    @property
    def is_saving(self) -> bool:
        """Check if profile is being saved."""
        return self._is_saving
    
    @is_saving.setter
    def is_saving(self, value: bool):
        """Set saving state."""
        self._is_saving = value
    
    def get_user_name(self) -> str:
        """Get formatted user name from profile."""
        if not self._profile:
            return "User"
        
        first_name = self._profile.get('first_name', '')
        last_name = self._profile.get('last_name', '')
        
        if first_name and last_name:
            return f"{first_name} {last_name}"
        elif first_name:
            return first_name
        else:
            return "User"
    
    def get_user_email(self) -> str:
        """Get user email from profile."""
        if not self._profile:
            return ""
        return self._profile.get('email', '')
    
    def get_user_initial(self) -> str:
        """Get user initial for avatar."""
        if not self._profile:
            return "U"
        
        first_name = self._profile.get('first_name', '')
        email = self._profile.get('email', '')
        
        if first_name:
            return first_name[0].upper()
        elif email:
            return email[0].upper()
        else:
            return "U"
    
    def get_avatar_url(self) -> Optional[str]:
        """Get avatar URL from profile."""
        if not self._profile:
            return None
        return self._profile.get('avatar_url')
    
    def reset(self):
        """Reset profile state."""
        self._profile = None
        self._is_loading = False
        self._is_saving = False
        self._notify_profile_change()
