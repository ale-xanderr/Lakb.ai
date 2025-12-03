import httpx
from src.core.config import Config

class APIService:
    """Service for handling external API interactions."""

    def __init__(self):
        self.config = Config
        # Initialize clients or headers if needed
        self.headers = {
            "User-Agent": "Lakb.ai/0.5"
        }

    async def search_places(self, query: str, location: str = None):
        """
        Search for places using Google Places API.
        
        Args:
            query: Text query for the place.
            location: Optional 'lat,lng' string to bias results.
        """
        if not self.config.GOOGLE_PLACES_API_KEY:
            return {"error": "Google Places API Key not configured"}

        url = f"{self.config.GOOGLE_PLACES_BASE_URL}/textsearch/json"
        params = {
            "query": query,
            "key": self.config.GOOGLE_PLACES_API_KEY
        }
        if location:
            params["location"] = location

        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(url, params=params)
                response.raise_for_status()
                return response.json()
            except httpx.HTTPError as e:
                return {"error": f"Google Places API Error: {str(e)}"}

    async def get_place_details(self, place_id: str):
        """
        Get details for a specific place using Google Places API.
        """
        if not self.config.GOOGLE_PLACES_API_KEY:
            return {"error": "Google Places API Key not configured"}

        url = f"{self.config.GOOGLE_PLACES_BASE_URL}/details/json"
        params = {
            "place_id": place_id,
            "key": self.config.GOOGLE_PLACES_API_KEY
        }

        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(url, params=params)
                response.raise_for_status()
                return response.json()
            except httpx.HTTPError as e:
                return {"error": f"Google Places API Error: {str(e)}"}

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
