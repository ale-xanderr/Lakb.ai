from supabase import create_client, Client
from core.config import Config

_supabase_client: Client = None

def get_supabase_client() -> Client:
    """
    Get or create the Supabase client singleton.
    The client is configured to use PKCE flow for OAuth by default.
    """
    global _supabase_client
    if _supabase_client is None:
        if not Config.SUPABASE_URL or not Config.SUPABASE_KEY:
            # We might want to handle this more gracefully depending on how soft the requirement is
            # For now, print a warning and return None or raise error
            print("Warning: Supabase credentials not found. Authentication and persistence will not work.")
            return None
        
        try:
            # Create Supabase client - it automatically uses PKCE flow for OAuth
            _supabase_client = create_client(Config.SUPABASE_URL, Config.SUPABASE_KEY)
            
            # Validate redirect URL is configured
            if not Config.REDIRECT_URL:
                print("Warning: REDIRECT_URL not configured. Google OAuth will not work properly.")
            else:
                print(f"Supabase client initialized. OAuth redirect URL: {Config.REDIRECT_URL}")
                
        except Exception as e:
            print(f"Error creating Supabase client: {e}")
            return None
    
    return _supabase_client
