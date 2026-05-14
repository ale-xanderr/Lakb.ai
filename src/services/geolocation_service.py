import flet as ft
import flet_geolocator as fg
from services.api_service import APIService

class GeolocationService:
    """
    Service to handle device geolocation and reverse geocoding.
    Manages the Flet Geolocator control and handles location updates.
    """
    def __init__(self, page: ft.Page, on_location_update=None):
        self.page = page
        self.api_service = APIService()
        self.on_location_update = on_location_update
        self.last_location = None # (lat, lng)
        self._is_cleaned_up = False
        
        # Initialize Geolocator
        self.geolocator = fg.Geolocator(
            on_position_change=self._handle_position,
            on_error=self._handle_error
        )
        # Check if geolocator is already in overlay to avoid duplicates
        if self.geolocator not in self.page.overlay:
            self.page.overlay.append(self.geolocator)
            self.page.update()
    
    def cleanup(self):
        """
        Clean up resources by removing geolocator from overlay.
        Should be called when the service is no longer needed.
        """
        if self._is_cleaned_up:
            return
        
        try:
            if self.geolocator in self.page.overlay:
                self.page.overlay.remove(self.geolocator)
                self.page.update()
            self._is_cleaned_up = True
            print("DEBUG: GeolocationService cleaned up")
        except Exception as e:
            print(f"DEBUG: Error cleaning up GeolocationService: {e}")
    
    def __del__(self):
        """Destructor to ensure cleanup on deletion"""
        if not self._is_cleaned_up:
            self.cleanup()

    def request_location(self):
        """
        Request the current device location.
        Non-blocking: doesn't wait for permission, app continues to load.
        """
        if self._is_cleaned_up:
            print("DEBUG: GeolocationService is cleaned up, skipping request")
            return

        print("DEBUG: Requesting location permission (non-blocking)...")
        try:
            # Request permission asynchronously - don't wait for response
            # This prevents the app from hanging if permission is denied or takes time
            import threading
            
            def request_async():
                try:
                    if self._is_cleaned_up:
                        return

                    # Request permission (non-blocking)
                    # Use a try-except block specifically for the geolocator calls
                    try:
                        self.geolocator.request_permission()
                    except Exception as e:
                        if self._is_cleaned_up:
                            # Ignore errors if we are cleaning up
                            return
                        raise e
                    
                    if self._is_cleaned_up:
                        return

                    # Small delay to allow permission dialog to appear
                    import time
                    time.sleep(0.5)
                    
                    if self._is_cleaned_up:
                        return
                    
                    # Try to get position (will work if permission granted)
                    self.geolocator.get_current_position(
                        accuracy=fg.GeolocatorPositionAccuracy.HIGH,
                        location_settings=fg.GeolocatorSettings(
                            accuracy=fg.GeolocatorPositionAccuracy.HIGH
                        )
                    )
                except Exception as e:
                    # Only log errors if we haven't cleaned up
                    # Timeouts are expected if the control was removed during a request
                    if not self._is_cleaned_up:
                        print(f"DEBUG: Error in async location request: {e}")
            
            # Run in background thread so it doesn't block the UI
            thread = threading.Thread(target=request_async, daemon=True)
            thread.start()
            
        except Exception as e:
            print(f"DEBUG: Error starting location request: {e}")
            # Continue execution - don't block the app

    def _handle_position(self, e: fg.GeolocatorPositionChangeEvent):
        """
        Callback when position is received.
        """
        # print(f"DEBUG: Location received: {e.latitude}, {e.longitude}")
        
        lat = e.latitude
        lng = e.longitude
        
        # Throttle: Only update if location changed significantly (e.g. ~100m)
        # 0.001 degrees is roughly 111m
        if self.last_location:
            last_lat, last_lng = self.last_location
            if abs(lat - last_lat) < 0.001 and abs(lng - last_lng) < 0.001:
                # print("DEBUG: Location change too small, skipping update")
                return

        print(f"DEBUG: Processing significant location update: {lat}, {lng}")
        self.last_location = (lat, lng)
        
        # Reverse geocode to get city name
        city = self.api_service.reverse_geocode(lat, lng)
        print(f"DEBUG: Resolved city: {city}")
        
        if self.on_location_update:
            self.on_location_update(lat, lng, city)

    def _handle_error(self, e):
        """
        Callback when location error occurs.
        """
        print(f"DEBUG: Location error: {e}")
        # Fallback or notify user if needed
