import os
from dotenv import load_dotenv
import flet as ft

# Load environment variables from .env file
# Note: .env files are not bundled in Android APK builds
# For production builds, you should either:
#   1. Use the build script to inject values (recommended)
#   2. Hardcode production values in the Config class below
if os.path.exists('.env'):
    load_dotenv()
    print("INFO: Loading environment variables from .env file (development mode)")
else:
    print("INFO: No .env file found - using environment variables or defaults (production mode)")

# Centralized app window configuration
APP_WIDTH: int = 412
APP_HEIGHT: int = 917
APP_TITLE: str = "Lakb.ai"
APP_RESIZABLE: bool = False
APP_PADDING: int | float = 0


def configure_page(page: ft.Page, *, title: str | None = None) -> None:
    """Apply common window configuration to the given Flet page.

    Parameters
    ----------
    page:
        The Flet `Page` instance to configure.
    title:
        Optional custom window title; falls back to `APP_TITLE`.
    """

    # Basic properties
    page.title = title or APP_TITLE
    page.padding = APP_PADDING

    # Handle both older top-level window_* properties and the newer
    # `page.window` object, so the config works across runtimes.
    # Desktop/web runtimes
    if getattr(page, "window", None) is not None:
        page.window.width = APP_WIDTH
        page.window.height = APP_HEIGHT
        page.window.resizable = APP_RESIZABLE
        page.window.maximizable = APP_RESIZABLE

    # Backwards/alternative attributes (no-op if not present)
    if hasattr(page, "window_width"):
        page.window.width = APP_WIDTH
    if hasattr(page, "window_height"):
        page.window.height = APP_HEIGHT
    if hasattr(page, "window_resizable"):
        page.window.resizable = APP_RESIZABLE


class Config:
    """Application configuration.
    
    For Android APK builds:
    - Environment variables can be set using the build_apk.py script
    - Alternatively, replace os.getenv() calls with hardcoded values for production
    - Example: GOOGLE_PLACES_API_KEY = os.getenv("GOOGLE_PLACES_API_KEY") or "your-production-key"
    """
    
    # API Keys
    # For production builds, you can add fallback values using: os.getenv("KEY") or "fallback-value"
    GOOGLE_PLACES_API_KEY = os.getenv("GOOGLE_PLACES_API_KEY")
    MAPS_STATIC_API_KEY = os.getenv("MAPS_STATIC_API_KEY")
    OPENWEATHER_API_KEY = os.getenv("OPENWEATHER_API_KEY")
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
    CALENDARIFIC_API_KEY = os.getenv("CALENDARIFIC_API_KEY")
    OPENAQ_API_KEY = os.getenv("OPENAQ_API_KEY")

    # Base URLs (Optional, can be hardcoded in services or here)
    GOOGLE_PLACES_BASE_URL = "https://maps.googleapis.com/maps/api/place"
    OPENWEATHER_BASE_URL = os.getenv("OPENWEATHER_BASE_URL", "https://api.openweathermap.org/data/2.5")
    GEMINI_BASE_URL = os.getenv("GEMINI_BASE_URL", "https://generativelanguage.googleapis.com/v1beta")
    CALENDARIFIC_BASE_URL = os.getenv("CALENDARIFIC_BASE_URL", "https://calendarific.com/api/v2")
    OPENAQ_BASE_URL = os.getenv("OPENAQ_BASE_URL", "https://api.openaq.org/v3")

    # Supabase
    SUPABASE_URL = os.getenv("SUPABASE_URL")
    SUPABASE_KEY = os.getenv("SUPABASE_KEY")
    
    # OAuth Redirect URL (for Google Sign-In callback)
    REDIRECT_URL = os.getenv("REDIRECT_URL")

    @classmethod
    def validate(cls):
        """Validate that essential configuration is present."""
        missing = []
        if not cls.GOOGLE_PLACES_API_KEY:
            missing.append("GOOGLE_PLACES_API_KEY")
        
        # Warn about optional but recommended services
        warnings = []
        if not cls.SUPABASE_URL or not cls.SUPABASE_KEY:
            warnings.append("Supabase credentials not configured - authentication and data persistence will not work")
        
        if missing:
            print(f"Warning: Missing configuration keys: {', '.join(missing)}")
        
        if warnings:
            for warning in warnings:
                print(f"Warning: {warning}")