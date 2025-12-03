import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Config:
    """Application configuration."""
    
    # API Keys
    GOOGLE_PLACES_API_KEY = os.getenv("GOOGLE_PLACES_API_KEY")
    TRIPADVISOR_API_KEY = os.getenv("TRIPADVISOR_API_KEY")
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    OPENWEATHER_API_KEY = os.getenv("OPENWEATHER_API_KEY")

    # Base URLs (Optional, can be hardcoded in services or here)
    GOOGLE_PLACES_BASE_URL = "https://maps.googleapis.com/maps/api/place"
    TRIPADVISOR_BASE_URL = "https://api.content.tripadvisor.com/api/v1/location"
    OPENAI_BASE_URL = "https://api.openai.com/v1"
    OPENWEATHER_BASE_URL = "https://api.openweathermap.org/data/2.5"

    @classmethod
    def validate(cls):
        """Validate that essential configuration is present."""
        missing = []
        if not cls.GOOGLE_PLACES_API_KEY:
            missing.append("GOOGLE_PLACES_API_KEY")
        # Add other critical keys here if strictly required for startup
        
        if missing:
            print(f"Warning: Missing configuration keys: {', '.join(missing)}")
