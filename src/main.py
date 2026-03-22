import flet as ft
from views.home_view import main as home_main
from views.login_view import main as login_main
from views.splash import main as splash_main
from core.config import configure_page
from state import ServiceManager, AppStateManager, AuthStateController

def main(page: ft.Page):
    """
    Central app entry for Lakb.ai.
    """
    # Enforce window size and configuration globally
    configure_page(page)
    
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
    
    # 1. Try to restore session from client storage
    user = auth.resolve_initial_auth_state(page)
    if user:
        if hasattr(user, 'user') and user.user: # Authenticated online
             auth_state_controller.set_authenticated(user)
        else: # Authenticated offline (cached dict)
             auth_state_controller.set_authenticated_offline(user)
        
        # We don't return here yet, we might have a deep link or specific route to handle

    # 2. Define Route Handler
    def handle_route_change(e):
        """
        Handle route changes, including OAuth callbacks and general navigation.
        """
        route = page.route
        print(f"Route changed to: {route}")
        
        # Enforce window size on every route change to ensure consistency
        configure_page(page)
        
        # Check if this is an OAuth callback
        if route and ("/api/oauth/redirect" in route or "/oauth_callback" in route or "/auth/callback" in route or "lakbai://" in route or "?code=" in route or "#code=" in route or (route.startswith("/") and "code=" in route)):
            
            # Delegate complex parsing to AuthService
            result = auth.handle_auth_callback(route, page)
            
            if result["success"]:
                user = result["user"]
                auth_state_controller.set_authenticated(user)
                
                # Refresh favorites service to load user's favorites from Supabase in background
                try:
                    favorites_service = service_manager.favorites_service
                    import threading
                    def refresh_favs():
                        try:
                            favorites_service.get_favorites(force_refresh=True)
                            print("DEBUG: Refreshed favorites after login in background")
                        except Exception as fav_error:
                            print(f"Warning: Could not refresh favorites: {fav_error}")
                    threading.Thread(target=refresh_favs, daemon=True).start()
                except Exception as eval_err:
                    print(f"Warning: Could not start favorites refresh thread: {eval_err}")
                
                # Navigate to home (clearing history)
                page.clean()
                # CRITICAL: Clear our OAuth on_route_change so home_view can
                # install its own routing handler without being blocked.
                page.on_route_change = None
                page.route = "/"  # Reset the route, otherwise home_view won't know what to render
                home_main(page)
                return
            
            elif result["error"]:
                 # Show error and go to login
                 try:
                    page.snack_bar = ft.SnackBar(
                        ft.Text(f"Authentication failed: {result['error']}"),
                        bgcolor=ft.colors.ERROR,
                        duration=5000
                    )
                    page.snack_bar.open = True
                    page.update()
                 except:
                    pass
                 
                 # Redirect if specified
                 if result.get("redirect_to"):
                     page.clean()
                     if result["redirect_to"] == "/login":
                         page.route = "/login"
                         login_main(page)
                     else:
                         page.go(result["redirect_to"])
                 return

        # General Navigation Routing (Splash <-> Login)
        if route == "/login":
            page.clean()
            login_main(page)
            return
        elif route == "/splash":
            page.clean()
            splash_main(page)
            return

    # Set up our OAuth/redirect route change handler.
    # NOTE: home_view will ALWAYS override this with its own handler — this
    # is intentional. This handler is only needed between app start and the
    # moment home_view takes over (i.e. during the OAuth redirect flow).
    page.on_route_change = handle_route_change
    
    # Check initial route for OAuth callback (when app starts with callback URL)
    initial_route = page.route
    if initial_route and ("/api/oauth/redirect" in initial_route or "/oauth_callback" in initial_route or "/auth/callback" in initial_route or "?code=" in initial_route or (initial_route.startswith("/") and "code=" in initial_route)):
        handle_route_change(None)
        return
    
    # If we already have a user from resolve_initial_auth_state, go to home.
    # Clear our OAuth handler first so home_view can register its own cleanly.
    if auth_state_controller.is_authenticated or auth_state_controller.is_offline:
        print(f"User already logged in, navigating to home.")
        page.on_route_change = None
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