from typing import Optional, Dict
from supabase import Client
from core.supabase_client import get_supabase_client
from core.config import Config
import flet as ft
import json
from flet.auth.providers.google_oauth_provider import GoogleOAuthProvider

class AuthService:
    def __init__(self):
        # Always use the singleton client to ensure code_verifier persistence
        self.client: Client = get_supabase_client()
        # Store a reference to ensure we're using the same instance
        self._client_id = id(self.client) if self.client else None

    def get_user(self):
        """
        Get the current authenticated user.
        """
        if not self.client:
            return None
        try:
            return self.client.auth.get_user()
        except Exception as e:
            print(f"Error getting user: {e}")
            return None

    def sign_in_with_google(self) -> Optional[str]:
        """
        Initiates Google Sign-In using OAuth with PKCE flow.
        Returns the authorization URL to be opened in the browser.
        """
        if not self.client:
            print("Error: Supabase client not initialized")
            return None
        
        # Use the configured redirect URL from config
        # Should be: http://localhost:8550/oauth_callback
        redirect_url = Config.REDIRECT_URL
        
        if not redirect_url:
            print("Error: REDIRECT_URL not configured in environment variables")
            return None
        
        # Ensure redirect URL is properly formatted
        if not redirect_url.startswith("http://") and not redirect_url.startswith("https://"):
            print(f"Warning: Redirect URL should start with http:// or https://, got: {redirect_url}")
        
        try:
            # Supabase Python client uses PKCE flow by default
            # The redirectTo must match one of the redirect URLs configured in Supabase dashboard
            # IMPORTANT: Supabase Site URL should be set to http://localhost:8550 (not 3000)
            # to match your app's port. Otherwise it will redirect to Site URL instead of redirectTo.
            
            # Try camelCase first (matches Supabase REST API)
            try:
                data = self.client.auth.sign_in_with_oauth({
                    "provider": "google",
                    "options": {
                        "redirectTo": redirect_url  # camelCase format
                    }
                })
            except Exception as e1:
                print(f"camelCase format failed, trying snake_case: {e1}")
                # Fallback to snake_case (Python client format)
                data = self.client.auth.sign_in_with_oauth({
                    "provider": "google",
                    "options": {
                        "redirect_to": redirect_url  # snake_case format
                    }
                })
            
            if data and hasattr(data, 'url'):
                print(f"Google OAuth URL generated successfully, redirecting to: {redirect_url}")
                return data.url
            else:
                print("Error: No URL returned from OAuth sign-in")
                return None
                
        except Exception as e:
            print(f"Error initiating Google Sign-In: {e}")
            import traceback
            traceback.print_exc()
            return None

    def sign_in_with_password(self, email, password):
        """
        Sign in with email and password.
        """
        if not self.client:
             raise Exception("Supabase client not initialized")
        
        response = self.client.auth.sign_in_with_password({
            "email": email,
            "password": password
        })
        
        return response

    def sign_up(self, email, password, data=None):
        """
        Sign up a new user with email confirmation.
        After the user clicks the verification link in their email,
        they will be redirected to the app and automatically logged in.
        """
        if not self.client:
             raise Exception("Supabase client not initialized")
        
        credentials = {
            "email": email,
            "password": password,
        }
        
        # Configure options including email redirect and user metadata
        options = {
            "emailRedirectTo": Config.REDIRECT_URL  # Redirect after email confirmation
        }
        
        # Add user metadata if provided
        if data:
            options["data"] = data
        
        credentials["options"] = options

        return self.client.auth.sign_up(credentials)

    def set_session(self, access_token: str, refresh_token: str):
        """
        Set the session using access and refresh tokens from OAuth callback.
        """
        if not self.client:
            raise Exception("Supabase client not initialized")
        
        try:
            response = self.client.auth.set_session(access_token, refresh_token)
            return response
        except Exception as e:
            print(f"Error setting session: {e}")
            raise

    def exchange_code_for_session(self, code: str, page: ft.Page = None):
        """
        Exchange an authorization code for a session (PKCE flow).
        This is used when Supabase redirects with ?code= parameter.
        
        The code_verifier should be stored by the client during OAuth initiation.
        If it's missing, it means the client instance or storage was lost.
        
        Returns the response object which should contain session information.
        """
        if not self.client:
            raise Exception("Supabase client not initialized")
        
        try:
            # CRITICAL: The code_verifier must be stored by the client during OAuth initiation.
            # If it's missing, check if we can access it from the client's storage
            # The Supabase Python client stores it internally, but it might be lost if:
            # 1. The client instance changed
            # 2. The storage was cleared
            # 3. The app restarted between OAuth initiation and callback
            
            # Try to access the client's internal storage to check for code_verifier
            code_verifier = None
            if hasattr(self.client.auth, '_storage'):
                try:
                    # Try to get code_verifier from storage
                    storage = self.client.auth._storage
                    if hasattr(storage, 'get_item'):
                        code_verifier = storage.get_item('supabase.auth.code_verifier')
                        if code_verifier:
                            print("Found code_verifier in storage")
                        else:
                            print("Warning: code_verifier not found in storage")
                except Exception as storage_error:
                    print(f"Could not access storage: {storage_error}")
            
            # Supabase Python client expects a dictionary with 'auth_code' key for PKCE flow
            # Also need to include redirect_to to match the original OAuth request
            redirect_url = Config.REDIRECT_URL or "http://localhost:8550/oauth_callback"
            
            # Try with auth_code and redirect_to
            try:
                response = self.client.auth.exchange_code_for_session({
                    "auth_code": code,
                    "redirect_to": redirect_url
                })
            except Exception as e1:
                print(f"First attempt failed: {e1}")
                # Try without redirect_to
                try:
                    response = self.client.auth.exchange_code_for_session({
                        "auth_code": code
                    })
                except Exception as e2:
                    print(f"Second attempt failed: {e2}")
                    # Try with 'code' key instead of 'auth_code'
                    try:
                        response = self.client.auth.exchange_code_for_session({
                            "code": code,
                            "redirect_to": redirect_url
                        })
                    except Exception as e3:
                        print(f"Third attempt failed: {e3}")
                        # Last resort: try with just 'code'
                        try:
                            response = self.client.auth.exchange_code_for_session({
                                "code": code
                            })
                        except Exception as e4:
                            # All attempts failed - code_verifier is likely missing
                            error_msg = (
                                f"Code exchange failed. The code_verifier from OAuth initiation was lost. "
                                f"This usually happens when:\n"
                                f"1. The Supabase client instance changed between OAuth initiation and callback\n"
                                f"2. The storage was cleared\n"
                                f"3. The app was restarted between OAuth initiation and callback\n\n"
                                f"Error: {e4}"
                            )
                            print(error_msg)
                            raise Exception(error_msg)
            
            # The response should contain session data
            # Verify we have a valid response
            if response:
                print(f"Code exchange successful - response type: {type(response)}")
                # Check if response has session attribute
                if hasattr(response, 'session') and response.session:
                    print(f"Session found in response")
                elif hasattr(response, 'access_token'):
                    print(f"Access token found in response")
                return response
            else:
                raise Exception("Empty response from code exchange")
        except Exception as e:
            print(f"Error exchanging code for session: {e}")
            import traceback
            traceback.print_exc()
            raise

    def get_session(self) -> Optional[Dict]:
        """
        Get the current session.
        """
        if not self.client:
            return None
        
        try:
            session = self.client.auth.get_session()
            return session
        except Exception as e:
            print(f"Error getting session: {e}")
            return None

    def save_session_to_storage(self, page: ft.Page):
        """
        Save the current session to Flet's client storage for persistence.
        """
        if not self.client or not hasattr(page, 'client_storage'):
            return
        
        try:
            session = self.get_session()
            if session:
                # Handle different session object structures
                access_token = None
                refresh_token = None
                
                if hasattr(session, 'access_token'):
                    access_token = session.access_token
                    refresh_token = session.refresh_token
                elif hasattr(session, 'session') and session.session:
                    # Session might be wrapped
                    access_token = session.session.access_token
                    refresh_token = session.session.refresh_token
                elif isinstance(session, dict):
                    access_token = session.get('access_token')
                    refresh_token = session.get('refresh_token')
                
                if access_token and refresh_token:
                    page.client_storage.set("supabase_access_token", access_token)
                    page.client_storage.set("supabase_refresh_token", refresh_token)
                    print("Session saved to storage")
                else:
                    print("Warning: Could not extract tokens from session")
        except Exception as e:
            print(f"Error saving session to storage: {e}")
            import traceback
            traceback.print_exc()

    def restore_session_from_storage(self, page: ft.Page) -> bool:
        """
        Restore session from Flet's client storage.
        Returns True if session was successfully restored, False otherwise.
        """
        if not self.client or not hasattr(page, 'client_storage'):
            return False
        
        try:
            access_token = page.client_storage.get("supabase_access_token")
            refresh_token = page.client_storage.get("supabase_refresh_token")
            
            if access_token and refresh_token:
                self.set_session(access_token, refresh_token)
                print("Session restored from storage")
                return True
        except Exception as e:
            print(f"Error restoring session from storage: {e}")
        
        return False

    def sign_out(self, page: ft.Page = None):
        """
        Sign out the current user and clear session from storage.
        """
        if self.client:
            try:
                self.client.auth.sign_out()
            except Exception as e:
                print(f"Error signing out from Supabase: {e}")
        
        # Clear session from client storage
        if page and hasattr(page, 'client_storage'):
            try:
                page.client_storage.remove("supabase_access_token")
                page.client_storage.remove("supabase_refresh_token")
                # Clear recent searches and other user-specific data
                page.client_storage.remove("recent_searches")
                print("Session cleared from storage")
            except Exception as e:
                print(f"Error clearing storage: {e}")

    def update_profile_from_user(self, user):
        """
        Updates the 'profiles' table with data from the authenticated user.
        Useful for syncing Google account data (avatar, name) to our app's profile.
        """
        if not self.client or not user:
            return

        try:
            user_id = user.user.id
            email = user.user.email
            
            # Extract metadata
            meta = user.user.user_metadata or {}
            full_name = meta.get("full_name", "")
            avatar_url = meta.get("avatar_url", "")
            
            # Split name if possible
            first_name = ""
            last_name = ""
            if full_name:
                parts = full_name.split(" ", 1)
                first_name = parts[0]
                if len(parts) > 1:
                    last_name = parts[1]
            else:
                # Fallback to metadata first/last name if available
                first_name = meta.get("first_name", "") # Google doesn't always send this directly in top level
                last_name = meta.get("last_name", "")

            # Prepare update data
            profile_data = {
                "id": user_id,
                "email": email,
                "avatar_url": avatar_url,
                "updated_at": "now()", # Let Supabase handle timestamp if using default, or pass string
            }
            
            # Only update names if they are not empty (avoid overwriting if user manually changed them later, 
            # strictly speaking we might want to overwrite on login, but let's be safe. 
            # Actually, for initial google login, we want to set them.)
            if first_name:
                profile_data["first_name"] = first_name
            if last_name:
                profile_data["last_name"] = last_name
                
            # Upsert into profiles table
            # upsert=True is default for .upsert(), effectively INSERT ON CONFLICT UPDATE
            data = self.client.table("profiles").upsert(profile_data).execute()
            print(f"Profile updated for {email}: {data}")

        except Exception as e:
            print(f"Error updating profile: {e}")

    def reset_password_for_email(self, email: str):
        """
        Request a password reset email for the given email address.
        Supabase will send an email with a reset token.
        """
        if not self.client:
            raise Exception("Supabase client not initialized")
        
        try:
            # Use the configured redirect URL from config
            redirect_url = Config.REDIRECT_URL or "http://localhost:8550"
            
            # Request password reset - Supabase will send email with reset link
            response = self.client.auth.reset_password_for_email(
                email,
                {
                    "redirect_to": redirect_url
                }
            )
            return response
        except Exception as e:
            print(f"Error requesting password reset: {e}")
            raise

    def verify_reset_token_and_update_password(self, email: str, token: str, new_password: str):
        """
        Verify the reset token and update the password.
        For Supabase, we use verify_otp with type='recovery' to verify the token,
        then update the password.
        """
        if not self.client:
            raise Exception("Supabase client not initialized")
        
        try:
            # Verify the recovery token using verify_otp
            # Supabase recovery tokens can be verified using verify_otp with type='recovery'
            verify_response = self.client.auth.verify_otp({
                "email": email,
                "token": token,
                "type": "recovery"
            })
            
            # After verification, the session should be set automatically
            # Now we can update the password
            if verify_response:
                # Update the password
                update_response = self.client.auth.update_user({
                    "password": new_password
                })
                return update_response
            else:
                raise Exception("Token verification failed")
        except Exception as e:
            print(f"Error verifying token and updating password: {e}")
            raise
