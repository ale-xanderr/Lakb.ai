# src/services/api_service.py
import httpx
import datetime
from core.config import Config

class APIService:
    """Service for handling external API interactions."""

    def __init__(self):
        self.config = Config
        self.headers = {
            "User-Agent": "Lakb.ai/0.5"
        }

    # --- 1. SEARCH PLACES (List View) ---
    def search_places(self, query: str = None, location: str = None, place_type: str = None, page_token: str = None, limit: int = 20):
        if not getattr(self.config, "GOOGLE_PLACES_API_KEY", None):
            print("DEBUG: Google Places API Key is MISSING")
            return {"error": "Google Places API Key not configured"}

        url = "https://places.googleapis.com/v1/places:searchText"
        headers = {
            "Content-Type": "application/json",
            "X-Goog-Api-Key": self.config.GOOGLE_PLACES_API_KEY,
            "X-Goog-FieldMask": "places.id,places.displayName,places.formattedAddress,places.photos,places.rating,places.location,nextPageToken"
        }

        body = {}
        base_query = query or place_type or "tourist attractions"
        
        # Append location to query for better relevance
        if location:
            body["textQuery"] = f"{base_query} in {location}"
        else:
            body["textQuery"] = base_query

        if page_token:
            body["pageToken"] = page_token

        with httpx.Client() as client:
            try:
                response = client.post(url, headers=headers, json=body)
                response.raise_for_status()
                data = response.json()

                results = []
                for place in data.get("places", []):
                    # Normalize Location Data (Lat/Lng)
                    loc_data = place.get("location", {})
                    lat = loc_data.get("latitude")
                    lng = loc_data.get("longitude")

                    mapped_place = {
                        "place_id": place.get("id"),
                        "name": (place.get("displayName") or {}).get("text"),
                        "formatted_address": place.get("formattedAddress"),
                        "rating": place.get("rating"),
                        "geometry": {
                            "location": {
                                "lat": lat,
                                "lng": lng
                            }
                        },
                        "photos": []
                    }
                    if "photos" in place:
                        for photo in place["photos"]:
                            mapped_place["photos"].append({
                                "photo_reference": photo.get("name"),
                                "width": photo.get("widthPx"),
                                "height": photo.get("heightPx")
                            })
                    results.append(mapped_place)

                return {"results": results[:limit], "next_page_token": data.get("nextPageToken")}
            except Exception as e:
                print(f"DEBUG: Places API Error: {e}")
                return {"error": str(e)}

    # --- 2. GET PLACE DETAILS (Fixes your Crash) ---
    async def get_place_details(self, place_id: str):
        """
        Fetches detailed info (reviews, opening hours) for a specific place.
        CRITICAL for destination_card.py
        """
        if not getattr(self.config, "GOOGLE_PLACES_API_KEY", None):
            return {"error": "Google Places API Key not configured"}

        url = f"https://places.googleapis.com/v1/places/{place_id}"
        headers = {
            "Content-Type": "application/json",
            "X-Goog-Api-Key": self.config.GOOGLE_PLACES_API_KEY,
            "X-Goog-FieldMask": "id,displayName,formattedAddress,location,rating,userRatingCount,reviews,photos,editorialSummary,currentOpeningHours,googleMapsUri"
        }

        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(url, headers=headers)
                response.raise_for_status()
                data = response.json()

                result = {
                    "place_id": data.get("id"),
                    "name": (data.get("displayName") or {}).get("text"),
                    "address": data.get("formattedAddress"),
                    "rating": data.get("rating"),
                    "user_rating_count": data.get("userRatingCount"),
                    "description": (data.get("editorialSummary") or {}).get("text"),
                    "location": data.get("location"),
                    "reviews": [],
                    "photos": [],
                    "open_now": (data.get("currentOpeningHours") or {}).get("openNow", False),
                    "google_maps_url": data.get("googleMapsUri")
                }

                if "reviews" in data:
                    for review in data["reviews"]:
                        result["reviews"].append({
                            "author_name": (review.get("authorAttribution") or {}).get("displayName"),
                            "rating": review.get("rating"),
                            "text": (review.get("text") or {}).get("text") if review.get("text") else None,
                            "relative_time": review.get("relativePublishTimeDescription"),
                            "author_photo": (review.get("authorAttribution") or {}).get("photoUri")
                        })

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

    # --- 3. REVERSE GEOCODE (Fixes 'Not Near User') ---
    def reverse_geocode(self, lat: float, lng: float):
        """
        Converts GPS (13.4, 123.3) -> Name ("Ocampo").
        """
        if not getattr(self.config, "GOOGLE_PLACES_API_KEY", None):
            return None

        url = "https://maps.googleapis.com/maps/api/geocode/json"
        params = {
            "latlng": f"{lat},{lng}",
            "key": self.config.GOOGLE_PLACES_API_KEY,
            "result_type": "locality|administrative_area_level_1"
        }

        with httpx.Client() as client:
            try:
                response = client.get(url, params=params, timeout=5.0)
                if response.status_code == 200:
                    data = response.json()
                    if data.get("status") == "OK" and data.get("results"):
                        for result in data["results"]:
                            for comp in result["address_components"]:
                                if "locality" in comp["types"]:
                                    return comp["long_name"]
                        return data["results"][0]["formatted_address"]
            except Exception as e:
                print(f"DEBUG: Reverse Geocode Error: {e}")
        return None

    def get_photo_url(self, photo_reference: str, max_width: int = 400) -> str:
        if not getattr(self.config, "GOOGLE_PLACES_API_KEY", None):
            return ""
        base_url = "https://places.googleapis.com/v1"
        return f"{base_url}/{photo_reference}/media?key={self.config.GOOGLE_PLACES_API_KEY}&maxWidthPx={max_width}"

    # --- 4. GOOGLE GEMINI ---
    def get_ai_recommendation(self, prompt: str) -> str:
        api_key = getattr(self.config, "GEMINI_API_KEY", "")
        if not api_key: api_key = self.config.GOOGLE_PLACES_API_KEY
        if not api_key: return "Plan ahead and stay safe!"

        url = f"{self.config.GEMINI_BASE_URL}/models/gemini-1.5-flash:generateContent?key={api_key}"
        headers = {"Content-Type": "application/json"}
        payload = {"contents": [{"parts": [{"text": prompt}]}]}

        try:
            with httpx.Client() as client:
                resp = client.post(url, headers=headers, json=payload, timeout=15.0)
                if resp.status_code == 200:
                    data = resp.json()
                    return data["candidates"][0]["content"]["parts"][0]["text"]
                else:
                    print(f"Gemini Error: {resp.text}")
                    return ""
        except Exception as e:
            print(f"AI Conn Error: {e}")
            return ""

    # --- 5. CONTEXT APIS ---
    def get_weather_forecast(self, location: str):
        if not self.config.OPENWEATHER_API_KEY: return None
        url = f"{self.config.OPENWEATHER_BASE_URL}/weather"
        try:
            with httpx.Client() as client:
                resp = client.get(url, params={"q": location, "appid": self.config.OPENWEATHER_API_KEY, "units": "metric"}, timeout=5.0)
                if resp.status_code == 200:
                    data = resp.json()
                    return f"{data['weather'][0]['description']}, {data['main']['temp']}°C"
        except Exception: return None

    def get_holidays(self, country_code="PH", year=None):
        if not self.config.CALENDARIFIC_API_KEY: return None
        import datetime
        if not year: year = datetime.datetime.now().year
        url = f"{self.config.CALENDARIFIC_BASE_URL}/holidays"
        try:
            with httpx.Client() as client:
                resp = client.get(url, params={"api_key": self.config.CALENDARIFIC_API_KEY, "country": country_code, "year": year}, timeout=5.0)
                if resp.status_code == 200: return resp.json().get("response", {}).get("holidays", [])
        except Exception: return None

    def get_air_quality(self, lat: float, lng: float):
        url = f"{self.config.OPENAQ_BASE_URL}/latest"
        headers = {"X-API-Key": self.config.OPENAQ_API_KEY} if self.config.OPENAQ_API_KEY else {}
        try:
            with httpx.Client() as client:
                resp = client.get(url, params={"coordinates": f"{lat},{lng}", "radius": 5000, "limit": 1}, headers=headers, timeout=5.0)
                if resp.status_code == 200:
                    data = resp.json()
                    if data.get("results"):
                        m = data["results"][0].get("measurements", [])[0]
                        return f"{m['parameter'].upper()}: {m['value']} {m['unit']}"
        except Exception: return None