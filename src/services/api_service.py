import httpx
from core.config import Config

class APIService:
    """Service for handling external API interactions."""

    def __init__(self):
        self.config = Config
        # Initialize clients or headers if needed
        self.headers = {
            "User-Agent": "Lakb.ai/0.5"
        }

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
            "X-Goog-FieldMask": "places.id,places.displayName,places.formattedAddress,places.photos,places.rating,nextPageToken"
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

    async def get_place_details(self, place_id: str):
        """
        Get details for a specific place using Google Places API (New) v1.
        """
        if not self.config.GOOGLE_PLACES_API_KEY:
            return {"error": "Google Places API Key not configured"}

        # Use the New Places API (v1)
        url = f"https://places.googleapis.com/v1/places/{place_id}"
        
        headers = {
            "Content-Type": "application/json",
            "X-Goog-Api-Key": self.config.GOOGLE_PLACES_API_KEY,
            # Request specific fields: id, name, photos, rating, reviews, editorialSummary, location, address, googleMapsUri
            "X-Goog-FieldMask": "id,displayName,formattedAddress,location,rating,userRatingCount,reviews,photos,editorialSummary,currentOpeningHours,googleMapsUri"
        }

        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(url, headers=headers)
                response.raise_for_status()
                data = response.json()
                
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

                return result

            except httpx.HTTPError as e:
                return {"error": f"Google Places API Error: {str(e)}"}

    async def generate_place_description(self, place_name: str, location: str):
        """
        Generate a description for a place using OpenAI if API details are missing.
        """
        prompt = f"Write a short, engaging travel description (approx 3-4 sentences) for {place_name} located in {location}. Focus on what makes it a good tourist destination."
        
        return await self.get_ai_recommendation(prompt)

    async def get_tripadvisor_content(self, location_id: str):
        """
        Get location details from TripAdvisor API.
        """
        if not self.config.TRIPADVISOR_API_KEY:
            return {"error": "TripAdvisor API Key not configured"}

        url = f"{self.config.TRIPADVISOR_BASE_URL}/{location_id}/details"
        params = {
            "key": self.config.TRIPADVISOR_API_KEY,
            "language": "en"
        }

        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(url, params=params, headers=self.headers)
                response.raise_for_status()
                return response.json()
            except httpx.HTTPError as e:
                return {"error": f"TripAdvisor API Error: {str(e)}"}

    async def get_ai_recommendation(self, prompt: str):
        """
        Get travel recommendations using OpenAI API.
        """
        if not self.config.OPENAI_API_KEY:
            return {"error": "OpenAI API Key not configured"}

        url = f"{self.config.OPENAI_BASE_URL}/chat/completions"
        headers = {
            "Authorization": f"Bearer {self.config.OPENAI_API_KEY}",
            "Content-Type": "application/json"
        }
        data = {
            "model": "gpt-3.5-turbo",
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.7
        }

        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(url, headers=headers, json=data)
                response.raise_for_status()
                return response.json()
            except httpx.HTTPError as e:
                return {"error": f"OpenAI API Error: {str(e)}"}

    async def get_weather(self, location: str):
        """
        Get current weather for a location using OpenWeatherMap API.
        
        Args:
            location: City name (e.g., "Manila")
        """
        if not self.config.OPENWEATHER_API_KEY:
            return {"error": "OpenWeatherMap API Key not configured"}

        url = f"{self.config.OPENWEATHER_BASE_URL}/weather"
        params = {
            "q": location,
            "appid": self.config.OPENWEATHER_API_KEY,
            "units": "metric"
        }

        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(url, params=params)
                response.raise_for_status()
                return response.json()
            except httpx.HTTPError as e:
                return {"error": f"OpenWeatherMap API Error: {str(e)}"}
