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
    """
    Apply common window configuration to the given Flet page.

    Args:
        page: The Flet `Page` instance to configure.
        title: Optional custom window title; falls back to `APP_TITLE`.
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
    - .env files are NOT included in the APK
    - You MUST provide production values as fallbacks using the 'or' operator
    - Example: SUPABASE_URL = os.getenv("SUPABASE_URL") or "https://ncfnpuuritydbdkrnpmd.supabase.co"
    
    IMPORTANT: Replace the placeholder values below with your actual API keys before building APK!
    """
    
    # API Keys - replace apiKey with your actual keys for production builds
    # Development: Loads from .env
    # Production: Uses fallback value (the part after 'or')
    
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

    # Supabase - CRITICAL: These MUST be set for the app to work!
    SUPABASE_URL = os.getenv("SUPABASE_URL")
    SUPABASE_KEY = os.getenv("SUPABASE_KEY")
    
    # OAuth Redirect URL (for Google Sign-In callback)
    # Platform-specific configuration:
    # - Android: Uses custom URL scheme for deep linking (lakbai://oauth_callback)
    # - Desktop/Web: Uses localhost for development (http://localhost:8550/oauth_callback)
    
    # Android deep link redirect URL
    ANDROID_REDIRECT_URL = os.getenv("ANDROID_REDIRECT_URL") or "lakbai://oauth_callback"
    
    # Desktop/Web redirect URL (for development)
    DESKTOP_REDIRECT_URL = os.getenv("REDIRECT_URL") or "http://localhost:8550/oauth_callback"
    
    # Legacy support
    REDIRECT_URL = os.getenv("REDIRECT_URL")
    
    @classmethod
    def is_android(cls) -> bool:
        """Detect if the app is running on Android platform."""
        try:
            import platform
            system = platform.system().lower()
            
            # Check if running on Android
            # Flet on Android typically reports 'linux' but we can check environment
            if system == 'linux':
                # Check for Android-specific environment indicators
                if os.path.exists('/system/build.prop'):
                    return True
                # Check environment variables that might indicate Android
                if 'ANDROID_ROOT' in os.environ or 'ANDROID_DATA' in os.environ:
                    return True
            
            # Also check for Flet-specific indicators
            try:
                import flet as ft
                # Flet might set specific attributes on Android
                # This is a fallback check
                return False
            except:
                pass
                
            return False
        except Exception as e:
            print(f"Error detecting platform: {e}")
            return False
    
    @classmethod
    def get_redirect_url(cls, is_android: bool = None) -> str:
        """
        Get the appropriate redirect URL based on the platform.
        
        Args:
            is_android: Optional explicit platform override. If None, auto-detects.
        
        Returns:
            Platform-appropriate redirect URL
        """
        # Allow explicit override for testing
        if is_android is None:
            is_android = cls.is_android()
        
        # Check if explicitly set in environment (takes precedence)
        if cls.REDIRECT_URL:
            return cls.REDIRECT_URL
        
        # Return platform-specific URL
        if is_android:
            print(f"INFO: Using Android redirect URL: {cls.ANDROID_REDIRECT_URL}")
            return cls.ANDROID_REDIRECT_URL
        else:
            print(f"INFO: Using Desktop/Web redirect URL: {cls.DESKTOP_REDIRECT_URL}")
            return cls.DESKTOP_REDIRECT_URL

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