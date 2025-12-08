import flet as ft
from views.home_view import main as home_main
from views.login_view import main as login_main
from views.splash import main as splash_main
from state import ServiceManager, AppStateManager, AuthStateController
from urllib.parse import urlparse, parse_qs

def main(page: ft.Page):
    """
    Central app entry for Lakb.ai.
    """
    page.title = "Lakb.ai"

    # Initialize state managers
    service_manager = ServiceManager()
    service_manager.initialize(page)
    
    app_state_manager = AppStateManager(page)
    app_state_manager.initialize()
    
    auth_state_controller = AuthStateController(page)
    # Store auth state controller on page for access from other views
    page._auth_state_controller = auth_state_controller
    
    # Get auth service from service manager
    auth = service_manager.auth_service
    
    # First, try to restore session from client storage
    if hasattr(page, 'client_storage'):
        try:
            session_restored = auth.restore_session_from_storage(page)
            if session_restored:
                user = auth.get_user()
                if user:
                    print(f"Session restored - User logged in: {user.user.email}")
                    auth_state_controller.set_authenticated(user)
                    home_main(page)
                    return
        except Exception as e:
            print(f"Error restoring session: {e}")
    
    # Check if we're being redirected from OAuth (callback route)
    def handle_route_change(e):
        """Handle OAuth callback and other routes"""
        route = page.route
        print(f"Route changed to: {route}")
        
        # General Navigation Routing (Splash <-> Login)
        if route == "/login":
            page.clean()
            login_main(page)
            return
        elif route == "/splash":
            page.clean()
            splash_main(page)
            return

        # Check if this is an OAuth callback - handle /oauth_callback, /auth/callback, root with code, or any route with code
        # Note: Supabase may redirect to Site URL (localhost:3000) instead of redirectTo, so we check for ?code= in any route
        if route and ("/oauth_callback" in route or "/auth/callback" in route or "?code=" in route or "#code=" in route or (route.startswith("/") and "code=" in route)):
            try:
                # PKCE Flow: Check for authorization code in query parameters first
                # Format: /oauth_callback?code=...&state=... or /oauth_callback#code=...
                code = None
                
                # Check query parameters first
                if "?code=" in route or "&code=" in route:
                    if "?" in route:
                        query_part = route.split("?", 1)[1]
                        # Handle case where there might be a hash after query
                        if "#" in query_part:
                            query_part = query_part.split("#", 1)[0]
                        params = parse_qs(query_part)
                        code = params.get("code", [None])[0]
                
                # Check hash fragment as fallback
                if not code and "#code=" in route:
                    hash_part = route.split("#", 1)[1]
                    params = {}
                    for param in hash_part.split("&"):
                        if "=" in param:
                            key, value = param.split("=", 1)
                            params[key] = value
                    code = params.get("code")
                
                if code:
                    print(f"Found authorization code: {code[:20]}..., exchanging for session...")
                    try:
                        # Exchange the code for session tokens
                        # Pass page to help with any storage operations
                        response = auth.exchange_code_for_session(code, page)
                        
                        if response:
                            print(f"Code exchange response received: {type(response)}")
                            
                            # Small delay to ensure session is set in Supabase client
                            import time
                            time.sleep(0.5)
                            
                            # Save to storage for persistence
                            try:
                                auth.save_session_to_storage(page)
                                print("Session saved to storage")
                            except Exception as save_error:
                                print(f"Warning: Could not save session to storage: {save_error}")
                            
                            # Verify user is authenticated
                            user = auth.get_user()
                            print(f"User check result: {user is not None}")
                            
                            if user and hasattr(user, 'user') and user.user:
                                # Sync user profile
                                try:
                                    auth.update_profile_from_user(user)
                                except Exception as profile_error:
                                    print(f"Warning: Could not update profile: {profile_error}")
                                
                                print(f"User authenticated successfully: {user.user.email}")
                                
                                # Update auth state
                                auth_state_controller.set_authenticated(user)
                                
                                # Refresh favorites service to load user's favorites from Supabase
                                try:
                                    favorites_service = service_manager.favorites_service
                                    favorites_service.get_favorites(force_refresh=True)
                                    print("DEBUG: Refreshed favorites after login")
                                except Exception as fav_error:
                                    print(f"Warning: Could not refresh favorites: {fav_error}")
                                
                                # Clear the route to remove the callback parameters
                                try:
                                    page.route = "/"
                                    page.update()
                                except:
                                    pass
                                
                                # Navigate to home
                                page.clean()
                                home_main(page)
                                return
                            else:
                                print(f"Error: User not found after code exchange. User object: {user}")
                                # Try one more time after a brief delay
                                time.sleep(0.5)
                                user = auth.get_user()
                                if user and hasattr(user, 'user') and user.user:
                                    print(f"User found on retry: {user.user.email}")
                                    page.clean()
                                    home_main(page)
                                    return
                                else:
                                    raise Exception("User authentication failed - user not found after code exchange")
                        else:
                            print("Failed to exchange code for session - no response")
                            raise Exception("Failed to exchange code for session - empty response")
                    except Exception as exchange_error:
                        print(f"Error during code exchange: {exchange_error}")
                        import traceback
                        traceback.print_exc()
                        # Show error to user
                        try:
                            page.snack_bar = ft.SnackBar(
                                ft.Text(f"Authentication failed: {str(exchange_error)}"),
                                bgcolor=ft.colors.ERROR,
                                duration=5000
                            )
                            page.snack_bar.open = True
                            page.update()
                        except:
                            pass
                        page.clean()
                        login_main(page)
                        return
                else:
                    print("Authorization code missing in callback URL")
                
                # Implicit Flow (fallback): Parse URL hash fragments
                # Format: /auth/callback#access_token=...&refresh_token=...&type=...
                if "#" in route:
                    hash_part = route.split("#", 1)[1]
                    # Parse the hash fragment
                    params = {}
                    for param in hash_part.split("&"):
                        if "=" in param:
                            key, value = param.split("=", 1)
                            params[key] = value
                    
                    access_token = params.get("access_token")
                    refresh_token = params.get("refresh_token")
                    
                    if access_token and refresh_token:
                        # Set the session with the tokens
                        auth.set_session(access_token, refresh_token)
                        # Save to storage for persistence
                        auth.save_session_to_storage(page)
                        
                        print("OAuth authentication successful via implicit flow!")
                        
                        # Sync user profile
                        user = auth.get_user()
                        if user:
                            auth.update_profile_from_user(user)
                            auth_state_controller.set_authenticated(user)
                        
                        # Navigate to home
                        page.clean()
                        home_main(page)
                        return
                    else:
                        print("Missing tokens in OAuth callback")
                
                # If we get here, the callback didn't have valid tokens or code
                print("OAuth callback received but no valid credentials found")
                print(f"Route was: {route}")
                page.clean()
                login_main(page)
                
            except Exception as ex:
                print(f"Error handling OAuth callback: {ex}")
                import traceback
                traceback.print_exc()
                # Show error to user if possible
                try:
                    page.snack_bar = ft.SnackBar(
                        ft.Text(f"Authentication error: {str(ex)}"),
                        bgcolor=ft.colors.ERROR,
                        duration=5000
                    )
                    page.snack_bar.open = True
                except:
                    pass
                page.clean()
                login_main(page)
    
    # Set up route change handler (only if not already set by home_main)
    # home_main will set its own route handler, so we only set this for initial OAuth handling
    if page.on_route_change is None:
        page.on_route_change = handle_route_change
    
    # Check initial route for OAuth callback (when app starts with callback URL)
    # Also check for code parameter in root or any route
    initial_route = page.route
    if initial_route and ("/oauth_callback" in initial_route or "/auth/callback" in initial_route or "?code=" in initial_route or (initial_route.startswith("/") and "code=" in initial_route)):
        handle_route_change(None)
        return
    
    # Check if already logged in
    user = auth.get_user()
    if user:
        print(f"User already logged in: {user.user.email}")
        auth_state_controller.set_authenticated(user)
        home_main(page)
        return
    
    # Check explicit routes for reload/restart
    if page.route == "/login":
        login_main(page)
        return
    elif page.route == "/splash":
        splash_main(page)
        return
    
    # Default flow - show splash screen
    if page.route == "/" or not page.route:
         page.route = "/splash"
    splash_main(page)

if __name__ == "__main__":
    # For Android APK builds, Flet automatically handles the app view and port
    # The assets_dir should be relative to the project root without parent navigation
    # 
    # Note: OAuth redirects on Android require deep linking configuration
    # For development with web browser testing, you can temporarily use:
    #   ft.app(target=main, assets_dir="assets", port=8550, view=ft.AppView.WEB_BROWSER)
    # 
    # For production Android builds, use the simple form:
    ft.app(target=main, assets_dir="assets")