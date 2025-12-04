import flet as ft
import flet_geolocator as fg
from services.api_service import APIService

class GeolocationService:
    """
    Service to handle device geolocation and reverse geocoding.
    """
    def __init__(self, page: ft.Page, on_location_update=None):
        self.page = page
        self.api_service = APIService()
        self.on_location_update = on_location_update
        self.last_location = None # (lat, lng)
        
        # Initialize Geolocator
        self.geolocator = fg.Geolocator(
            on_position_change=self._handle_position,
            on_error=self._handle_error
        )
        self.page.overlay.append(self.geolocator)
        self.page.update()

    def request_location(self):
        """
        Request the current device location.
        """
        print("DEBUG: Requesting location permission...")
        # Check permission first
        try:
            self.geolocator.request_permission()
            
            self.geolocator.get_current_position(
                accuracy=fg.GeolocatorPositionAccuracy.HIGH,
                location_settings=fg.GeolocatorSettings(
                    accuracy=fg.GeolocatorPositionAccuracy.HIGH
                )
            )
        except Exception as e:
            print(f"DEBUG: Error requesting location: {e}")

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
