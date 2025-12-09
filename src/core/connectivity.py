"""
Connectivity utility module for network status checking.

Provides functions to detect internet connectivity and manage connectivity 
state throughout the application. Used for offline support.
"""

import httpx
from typing import Optional, Callable, List


class ConnectivityState:
    """
    Singleton class to track current network connectivity status.
    
    Provides methods to check and update connectivity status,
    with callback support for state change notifications.
    """
    
    _instance: Optional['ConnectivityState'] = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._is_online = True  # Assume online initially
            cls._instance._listeners: List[Callable[[bool], None]] = []
        return cls._instance
    
    @property
    def is_online(self) -> bool:
        """Get current connectivity status."""
        return self._is_online
    
    def set_online(self, value: bool):
        """
        Update connectivity status and notify listeners if changed.
        
        Args:
            value: True if online, False if offline
        """
        if self._is_online != value:
            self._is_online = value
            self._notify_listeners()
    
    def add_listener(self, callback: Callable[[bool], None]):
        """
        Add a listener to be notified when connectivity changes.
        
        Args:
            callback: Function that takes a bool (is_online) parameter
        """
        if callback not in self._listeners:
            self._listeners.append(callback)
    
    def remove_listener(self, callback: Callable[[bool], None]):
        """Remove a previously added listener."""
        if callback in self._listeners:
            self._listeners.remove(callback)
    
    def _notify_listeners(self):
        """Notify all registered listeners of connectivity change."""
        for listener in self._listeners:
            try:
                listener(self._is_online)
            except Exception as e:
                print(f"Error notifying connectivity listener: {e}")
    
    def reset(self):
        """Reset to default state (for testing)."""
        self._is_online = True
        self._listeners = []


def is_online() -> bool:
    """
    Check if the device has internet connectivity.
    
    Attempts a lightweight HTTP HEAD request to a reliable endpoint.
    Updates the ConnectivityState singleton.
    
    Returns:
        True if network is available, False otherwise.
    """
    state = ConnectivityState()
    
    try:
        # Use a lightweight endpoint to check connectivity
        # Google's connectivity check endpoint is commonly used
        with httpx.Client(timeout=5.0) as client:
            response = client.head("https://www.google.com/generate_204")
            online = response.status_code == 204 or response.status_code == 200
            state.set_online(online)
            return online
    except Exception:
        state.set_online(False)
        return False


async def check_connectivity_async() -> bool:
    """
    Async version of connectivity check.
    
    Returns:
        True if network is available, False otherwise.
    """
    state = ConnectivityState()
    
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.head("https://www.google.com/generate_204")
            online = response.status_code == 204 or response.status_code == 200
            state.set_online(online)
            return online
    except Exception:
        state.set_online(False)
        return False


def get_connectivity_state() -> ConnectivityState:
    """
    Get the ConnectivityState singleton instance.
    
    Returns:
        The global ConnectivityState instance.
    """
    return ConnectivityState()


def mark_offline():
    """
    Mark the app as offline without performing a network check.
    Useful when an API call fails due to network error.
    """
    ConnectivityState().set_online(False)


def mark_online():
    """
    Mark the app as online without performing a network check.
    Useful when an API call succeeds.
    """
    ConnectivityState().set_online(True)
