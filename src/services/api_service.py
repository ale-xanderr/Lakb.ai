import httpx
import math
from core.config import Config

class APIService:
    """Service for handling external API interactions."""

    def __init__(self):
        self.config = Config
        # Initialize clients or headers if needed
        self.headers = {
            "User-Agent": "Lakb.ai/0.5"
        }
        # Use a shared async client for better connection pooling
        self._async_client = None

    def search_places(self, query: str = None, location: str = None, place_type: str = None, page_token: str = None):
        """
        Search for places using Google Places API.
        
        Args:
            query: Text query for the place.
            location: Optional 'lat,lng' string to bias results.
            place_type: Optional type of place to filter by (e.g., 'lodging', 'restaurant').
            page_token: Token for fetching the next page of results.
        """
    def search_places(self, query: str = None, location: str = None, place_type: str = None, page_token: str = None):
        """
        Search for places using Google Places API (New) v1.
        """
        if not self.config.GOOGLE_PLACES_API_KEY:
            print("DEBUG: Google Places API Key is MISSING")
            return {"error": "Google Places API Key not configured"}

        # Use the New Places API (v1)
        url = "https://places.googleapis.com/v1/places:searchText"
        
        headers = {
            "Content-Type": "application/json",
            "X-Goog-Api-Key": self.config.GOOGLE_PLACES_API_KEY,
            # Request specific fields to save costs and latency
            "X-Goog-FieldMask": "places.id,places.displayName,places.formattedAddress,places.photos,places.rating,places.types,nextPageToken"
        }

        # Construct the request body
        body = {}
        
        # Text query is required for searchText
        if query:
            body["textQuery"] = query
        elif place_type:
             # If no query but type is provided, search for the type
             body["textQuery"] = place_type
        else:
            # Fallback if neither is provided
            body["textQuery"] = "tourist attractions"

        # Add location bias if provided
        if location:
            # location format expected: "lat,lng"
            try:
                lat, lng = map(float, location.split(","))
                body["locationBias"] = {
                    "circle": {
                        "center": {
                            "latitude": lat,
                            "longitude": lng
                        },
                        "radius": 5000.0 # 5km radius bias
                    }
                }
            except ValueError:
                print(f"DEBUG: Invalid location format: {location}")

        if place_type:
             # v1 uses 'includedType' but textQuery is often enough. 
             # Let's use textQuery for broader matching or includedType if strict.
             # For now, appending to textQuery is often safer for v1 unless we know exact type strings.
             # But let's try strict typing if we can.
             # body["includedType"] = place_type.lower() # Note: v1 types are specific (e.g. "restaurant" not "Restaurant")
             pass 

        if page_token:
            body["pageToken"] = page_token

        print(f"DEBUG: Searching places (v1) with body: {body}")

        with httpx.Client() as client:
            try:
                response = client.post(url, headers=headers, json=body)
                print(f"DEBUG: API Response Status: {response.status_code}")
                # print(f"DEBUG: API Response Body: {response.text}") # Uncomment for deep debug
                response.raise_for_status()
                data = response.json()
                
                # Map v1 response to legacy structure for compatibility with home_view
                results = []
                for place in data.get("places", []):
                    mapped_place = {
                        "place_id": place.get("id"),
                        "name": place.get("displayName", {}).get("text"),
                        "formatted_address": place.get("formattedAddress"),
                        "rating": place.get("rating"),
                        "types": place.get("types", []),
                        "photos": []
                    }
                    
                    # Map photos
                    if "photos" in place:
                        for photo in place["photos"]:
                            mapped_place["photos"].append({
                                "photo_reference": photo.get("name"), # In v1, 'name' is the resource name used for fetching
                                "width": photo.get("widthPx"),
                                "height": photo.get("heightPx")
                            })
                    
                    results.append(mapped_place)
                
                print(f"DEBUG: Mapped {len(results)} results")
                return {
                    "results": results,
                    "next_page_token": data.get("nextPageToken")
                }

            except httpx.HTTPError as e:
                print(f"DEBUG: HTTP Error: {e}")
                return {"error": f"Google Places API Error: {str(e)}"}

    def reverse_geocode(self, lat: float, lng: float):
        """
        Get the city/locality name from coordinates using Google Geocoding API.
        """
        if not self.config.GOOGLE_PLACES_API_KEY:
             return None
             
        url = "https://maps.googleapis.com/maps/api/geocode/json"
        params = {
            "latlng": f"{lat},{lng}",
            "key": self.config.GOOGLE_PLACES_API_KEY,
            "result_type": "locality|administrative_area_level_1" # Prefer city/region
        }
        
        with httpx.Client() as client:
            try:
                response = client.get(url, params=params)
                response.raise_for_status()
                data = response.json()
                
                if data.get("status") == "OK" and data.get("results"):
                    # Return the first formatted address or specific component
                    # Ideally we want just the city name, e.g. "Legazpi City"
                    # Let's try to extract the locality component
                    for result in data["results"]:
                         for component in result["address_components"]:
                             if "locality" in component["types"]:
                                 return component["long_name"]
                    
                    # Fallback to formatted address of first result
                    return data["results"][0]["formatted_address"]
                    
                return None
            except Exception as e:
                print(f"DEBUG: Geocoding Error: {e}")
                return None

    def geocode(self, address: str):
        """
        Get coordinates and city name from an address string.
        Returns dict with lat, lng, city, or None.
        """
        if not self.config.GOOGLE_PLACES_API_KEY:
             return None
             
        url = "https://maps.googleapis.com/maps/api/geocode/json"
        params = {
            "address": address,
            "key": self.config.GOOGLE_PLACES_API_KEY
        }
        
        with httpx.Client() as client:
            try:
                response = client.get(url, params=params)
                response.raise_for_status()
                data = response.json()
                
                if data.get("status") == "OK" and data.get("results"):
                    result = data["results"][0]
                    loc = result["geometry"]["location"]
                    lat = loc["lat"]
                    lng = loc["lng"]
                    
                    # Extract city name
                    city = None
                    for component in result["address_components"]:
                         if "locality" in component["types"]:
                             city = component["long_name"]
                             break
                    
                    if not city:
                         # Fallback to administrative area or just formatted address
                         for component in result["address_components"]:
                             if "administrative_area_level_1" in component["types"]:
                                 city = component["long_name"]
                                 break
                    
                    if not city:
                        city = result["formatted_address"]

                    return {
                        "lat": lat,
                        "lng": lng,
                        "city": city,
                        "formatted_address": result["formatted_address"]
                    }
                    
                return None
            except Exception as e:
                print(f"DEBUG: Geocoding Error: {e}")
                return None

    def get_photo_url(self, photo_reference: str, max_width: int = 400) -> str:
        """
        Generate the URL for a place photo using Places API (New) v1.
        Args:
            photo_reference: The resource name (e.g. "places/ID/photos/ID")
        """
        if not self.config.GOOGLE_PLACES_API_KEY:
            return ""
            
        # v1 photo URL format:
        # https://places.googleapis.com/v1/{name}/media?key=API_KEY&maxWidthPx=400
        base_url = "https://places.googleapis.com/v1"
        return f"{base_url}/{photo_reference}/media?key={self.config.GOOGLE_PLACES_API_KEY}&maxWidthPx={max_width}"

    def get_static_map_url(self, lat: float, lng: float, width: int = 600, height: int = 300, zoom: int = 15) -> str:
        """
        Generate a static map image URL using Google Maps Static API.
        
        Args:
            lat: Latitude of the location
            lng: Longitude of the location
            width: Width of the map image in pixels (default: 600)
            height: Height of the map image in pixels (default: 300)
            zoom: Zoom level (1-20, default: 15)
        
        Returns:
            URL string for the static map image, or empty string if API key is missing
        """
        print(f"DEBUG: get_static_map_url called - lat: {lat}, lng: {lng}")
        print(f"DEBUG: MAPS_STATIC_API_KEY exists: {bool(self.config.MAPS_STATIC_API_KEY)}")
        
        if not self.config.MAPS_STATIC_API_KEY:
            print("DEBUG: MAPS_STATIC_API_KEY is missing!")
            return ""
        
        # Google Maps Static API URL format
        base_url = "https://maps.googleapis.com/maps/api/staticmap"
        params = {
            "center": f"{lat},{lng}",
            "zoom": str(zoom),
            "size": f"{width}x{height}",
            "markers": f"color:red|{lat},{lng}",
            "key": self.config.MAPS_STATIC_API_KEY
        }
        
        # Build query string
        query_string = "&".join([f"{k}={v}" for k, v in params.items()])
        return f"{base_url}?{query_string}"

    def _get_async_client(self):
        """Get or create a shared async HTTP client for connection pooling"""
        if self._async_client is None:
            self._async_client = httpx.AsyncClient(timeout=30.0)
        return self._async_client
    
    async def cleanup(self):
        """Clean up resources, close async client"""
        if self._async_client is not None:
            try:
                await self._async_client.aclose()
            except Exception as e:
                print(f"DEBUG: Error closing async client: {e}")
            finally:
                self._async_client = None
    
    async def get_place_details(self, place_id: str):
        """
        Get details for a specific place using Google Places API (New) v1.
        """
        print(f"\n=== DEBUG: get_place_details called ===")
        print(f"DEBUG: place_id = {place_id}")
        
        if not self.config.GOOGLE_PLACES_API_KEY:
            print("DEBUG: Google Places API Key is MISSING")
            return {"error": "Google Places API Key not configured"}

        # Use the New Places API (v1)
        # Ensure we target the resource correctly: places/{place_id}
        url = f"https://places.googleapis.com/v1/places/{place_id}"
        print(f"DEBUG: API URL = {url}")
        
        headers = {
            "Content-Type": "application/json",
            "X-Goog-Api-Key": self.config.GOOGLE_PLACES_API_KEY,
            # Request specific fields: id, name, photos, rating, reviews, editorialSummary, location, address, googleMapsUri
            "X-Goog-FieldMask": "id,displayName,formattedAddress,location,rating,userRatingCount,reviews,photos,editorialSummary,currentOpeningHours,googleMapsUri"
        }

        client = self._get_async_client()
        try:
            print("DEBUG: Sending GET request to Places API...")
            response = await client.get(url, headers=headers)
            print(f"DEBUG: Response status code = {response.status_code}")
            response.raise_for_status()
            data = response.json()
            print(f"DEBUG: Raw API response keys: {data.keys()}")
            print(f"DEBUG: editorialSummary field: {data.get('editorialSummary')}")
            
            # Map to a friendly structure
            result = {
                "place_id": data.get("id"),
                "name": data.get("displayName", {}).get("text"),
                "address": data.get("formattedAddress"),
                "rating": data.get("rating"),
                "user_rating_count": data.get("userRatingCount"),
                "description": data.get("editorialSummary", {}).get("text"),
                "location": data.get("location"), # {latitude, longitude}
                "reviews": [],
                "photos": [],
                "open_now": data.get("currentOpeningHours", {}).get("openNow", False),
                "google_maps_url": data.get("googleMapsUri")
            }
            
            print(f"DEBUG: Extracted description = {result.get('description')}")

            # Map reviews
            if "reviews" in data:
                for review in data["reviews"]:
                    result["reviews"].append({
                        "author_name": review.get("authorAttribution", {}).get("displayName"),
                        "rating": review.get("rating"),
                        "text": review.get("text", {}).get("text"),
                        "relative_time": review.get("relativePublishTimeDescription"),
                        "author_photo": review.get("authorAttribution", {}).get("photoUri")
                    })

            # Map photos
            if "photos" in data:
                for photo in data["photos"]:
                    result["photos"].append({
                        "photo_reference": photo.get("name"),
                        "width": photo.get("widthPx"),
                        "height": photo.get("heightPx")
                    })

            print(f"DEBUG: Mapped result with {len(result['reviews'])} reviews, {len(result['photos'])} photos")
            return result

        except httpx.HTTPError as e:
            print(f"DEBUG: HTTP Error occurred: {str(e)}")
            print(f"DEBUG: Response text (if available): {getattr(e.response, 'text', 'N/A')}")
            return {"error": f"Google Places API Error: {str(e)}"}

    async def get_nearby_places(self, lat: float, lng: float, radius: int = 5000, max_results: int = 5):
        """
        Get nearby places using Google Places API (New) v1 searchText endpoint with location bias.
        This is more reliable than searchNearby which has stricter requirements.
        
        Args:
            lat: Latitude of the center point
            lng: Longitude of the center point
            radius: Search radius in meters (default: 5000m = 5km)
            max_results: Maximum number of results to return (default: 5)
        
        Returns:
            List of nearby places with name, address, distance, photo, etc.
        """
        if not self.config.GOOGLE_PLACES_API_KEY:
            print("DEBUG: Google Places API Key is MISSING")
            return {"error": "Google Places API Key not configured"}

        # Use searchText with location bias - more reliable than searchNearby
        url = "https://places.googleapis.com/v1/places:searchText"
        
        headers = {
            "Content-Type": "application/json",
            "X-Goog-Api-Key": self.config.GOOGLE_PLACES_API_KEY,
            "X-Goog-FieldMask": "places.id,places.displayName,places.formattedAddress,places.photos,places.rating,places.location"
        }

        # Search for tourist attractions and points of interest near the location
        body = {
            "textQuery": "tourist attractions points of interest",
            "maxResultCount": max_results,
            "locationBias": {
                "circle": {
                    "center": {
                        "latitude": lat,
                        "longitude": lng
                    },
                    "radius": float(radius)
                }
            }
        }

        print(f"DEBUG: Searching nearby places with body: {body}")

        client = self._get_async_client()
        try:
            response = await client.post(url, headers=headers, json=body)
            print(f"DEBUG: Nearby places API Response Status: {response.status_code}")
            
            # Log error details if request failed
            if response.status_code != 200:
                error_text = response.text
                print(f"DEBUG: Error response: {error_text}")
            
            response.raise_for_status()
            data = response.json()
            
            # Map v1 response to friendly structure
            results = []
            for place in data.get("places", []):
                place_location = place.get("location", {})
                place_lat = place_location.get("latitude")
                place_lng = place_location.get("longitude")
                
                # Calculate distance (simple haversine formula approximation)
                distance_km = None
                if place_lat and place_lng:
                    # Haversine formula for distance calculation
                    R = 6371  # Earth radius in km
                    dlat = math.radians(place_lat - lat)
                    dlng = math.radians(place_lng - lng)
                    a = math.sin(dlat/2)**2 + math.cos(math.radians(lat)) * math.cos(math.radians(place_lat)) * math.sin(dlng/2)**2
                    c = 2 * math.asin(math.sqrt(a))
                    distance_km = R * c
                
                mapped_place = {
                    "place_id": place.get("id"),
                    "name": place.get("displayName", {}).get("text"),
                    "address": place.get("formattedAddress"),
                    "rating": place.get("rating"),
                    "location": place_location,
                    "distance_km": round(distance_km, 1) if distance_km else None,
                    "photos": []
                }
                
                # Map photos
                if "photos" in place:
                    for photo in place["photos"]:
                        mapped_place["photos"].append({
                            "photo_reference": photo.get("name"),
                            "width": photo.get("widthPx"),
                            "height": photo.get("heightPx")
                        })
                
                results.append(mapped_place)
            
            print(f"DEBUG: Found {len(results)} nearby places")
            return results

        except httpx.HTTPError as e:
            error_msg = str(e)
            if hasattr(e, 'response') and e.response is not None:
                try:
                    error_data = e.response.json()
                    error_msg = f"{error_msg} - {error_data}"
                except:
                    error_msg = f"{error_msg} - {e.response.text}"
            print(f"DEBUG: Nearby places HTTP Error: {error_msg}")
            return {"error": f"Google Places API Error: {error_msg}"}
        except Exception as e:
            print(f"DEBUG: Nearby places Unexpected Error: {e}")
            return {"error": f"Unexpected error: {str(e)}"}


