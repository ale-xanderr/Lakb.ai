import flet as ft
from state import ServiceManager, AppStateManager, ProfileStateController, AuthStateController, NavigationController


def _build_settings_tile(
    title: str,
    *,
    icon: str,
    icon_bg: str,
    trailing_text: str | None = None,
    is_logout: bool = False,
    on_click=None,
    trailing_control: ft.Control | None = None,
    text_color: str | None = None,
    tile_bg: str | None = None,
) -> ft.Control:
    """Reusable pill-shaped settings row."""

    # Logout row is always highlighted red
    effective_text_color = "#FF4B4B" if is_logout else (text_color or "onSurface")
    effective_tile_bg = tile_bg or "surface"

    return ft.Container(
        bgcolor=effective_tile_bg,
        border_radius=30,
        padding=ft.padding.symmetric(horizontal=18, vertical=10),
        margin=ft.margin.only(bottom=10),
        on_click=on_click,
        content=ft.Row(
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
            controls=[
                ft.Row(
                    vertical_alignment=ft.CrossAxisAlignment.CENTER,
                    spacing=14,
                    controls=[
                        ft.Container(
                            width=32,
                            height=32,
                            border_radius=16,
                            bgcolor=icon_bg,
                            alignment=ft.alignment.center,
                            content=ft.Icon(icon, size=18, color="#FFFFFF"),
                        ),
                        ft.Text(
                            title,
                            size=14,
                            weight=ft.FontWeight.W_600,
                            color=effective_text_color,
                        ),
                    ],
                ),
                (
                    trailing_control
                    if trailing_control is not None
                    else (
                        ft.Row(
                            spacing=10,
                            vertical_alignment=ft.CrossAxisAlignment.CENTER,
                            controls=[
                                ft.Text(
                                    trailing_text or "",
                                    size=12,
                                    color="#9AA4AF",
                                )
                                if trailing_text
                                else ft.Container(),
                                ft.Icon(
                                    ft.Icons.CHEVRON_RIGHT,
                                    size=18,
                                    color="#CED4DA" if not is_logout else "#FF4B4B",
                                ),
                            ],
                        )
                        if not is_logout
                        else ft.Container()
                    )
                ),
            ],
        ),
    )


def build_settings_content(page: ft.Page) -> ft.Control:
    """
    Builds the Settings / Profile View content.
    Displays user profile information and application settings (theme, language, etc.).
    
    Args:
        page: The Flet page instance.
        
    Returns:
        ft.Control: The main content control for the view.
    """

    # We rely on page.theme_mode and ft.Colors for styling now.
    # No manual color switching needed here.

    page.bgcolor = "background"
    
    # Initialize state managers
    service_manager = ServiceManager()
    if not service_manager._page:
        service_manager.initialize(page)
    
    app_state_manager = AppStateManager(page)
    profile_state_controller = ProfileStateController(page)
    
    # Get or create auth and navigation controllers
    # Check if they're stored on the page (from home_view), otherwise create them
    auth_state_controller = getattr(page, "_auth_state_controller", None)
    if auth_state_controller is None:
        auth_state_controller = AuthStateController(page)
        page._auth_state_controller = auth_state_controller
    
    navigation_controller = getattr(page, "_navigation_controller", None)
    if navigation_controller is None:
        navigation_controller = NavigationController(page)
        page._navigation_controller = navigation_controller
    
    # Get services
    auth_service = service_manager.auth_service
    profile_service = service_manager.profile_service
    
    # Fetch user and profile data
    user = auth_service.get_user()
    if not user:
        print("DEBUG: User is signed in as guest (User None)")
        # If no user, show placeholder data
        user_name = "Guest User"
        user_email = "guest@example.com"
        user_initial = "G"
        avatar_url = None
    else:
        # Fetch profile from Supabase
        # UserResponse structure: user.user contains the actual User object
        user_data = user.user
        profile = profile_service.ensure_profile_exists(
            user_data.id,
            user_data.email,
            user_data.user_metadata
        )
        
        # Update profile state controller
        profile_state_controller.profile = profile
        
        user_name = profile_state_controller.get_user_name()
        user_email = profile_state_controller.get_user_email()
        user_initial = profile_state_controller.get_user_initial()
        avatar_url = profile_state_controller.get_avatar_url()

    def go_back(e):
        page.go("/")

    def perform_logout(e):
        """Actual logout logic: sign out and show the login screen."""
        # Sign out and clear session from storage
        auth_service.sign_out(page)
        # Clear any view stack or route handlers that may re-render the home view
        try:
            # Clear Flet's view stack if present
            if hasattr(page, 'views') and isinstance(page.views, list):
                page.views.clear()
        except Exception:
            pass

        try:
            # If a route handler is set, unset it so subsequent view setup doesn't override login
            if hasattr(page, 'on_route_change'):
                page.on_route_change = None
        except Exception:
            pass

        # Navigate to the login screen so the user can sign in again
        from .login_view import main as login_main
        try:
            print("Logout: cleaning page and controls before launching login view")
            try:
                # Remove any dialogs
                if hasattr(page, 'dialog') and page.dialog:
                    try:
                        page.close(page.dialog)
                    except Exception:
                        pass
            except Exception:
                pass

            try:
                page.controls.clear()
            except Exception:
                pass

            try:
                page.views.clear()
            except Exception:
                pass

            try:
                page.route = "/"
            except Exception:
                pass

            try:
                page.clean()
            except Exception:
                pass

            print("Logout: invoking login_main")
            try:
                login_main(page)
                print("Logout: login_main completed")
            except Exception as e:
                import traceback
                print(f"Error launching login view after logout: {e}")
                traceback.print_exc()

            # Diagnostic info about page state after invoking login_main
            try:
                controls_len = len(page.controls) if hasattr(page, 'controls') else 'no-controls'
            except Exception:
                controls_len = 'err'
            try:
                views_len = len(page.views) if hasattr(page, 'views') else 'no-views'
            except Exception:
                views_len = 'err'
            try:
                rt = page.route if hasattr(page, 'route') else 'no-route'
            except Exception:
                rt = 'err'
            print(f"Logout diagnostic: controls={controls_len}, views={views_len}, route={rt}")

            try:
                page.update()
            except Exception:
                pass
            # If login_main didn't add any controls (blank screen), provide a visible fallback
            try:
                empty = False
                try:
                    empty = (not hasattr(page, 'controls')) or len(page.controls) == 0
                except Exception:
                    empty = True

                if empty:
                    print("Logout: detected empty page after attempting login_main — adding fallback button")
                    try:
                        def _open_login(e):
                            try:
                                login_main(page)
                                page.update()
                            except Exception as ex:
                                print(f"Fallback login_main error: {ex}")

                        fb = ft.Column(
                            alignment=ft.MainAxisAlignment.CENTER,
                            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                            controls=[
                                ft.Text("Could not render login screen.", color="onSurface"),
                                ft.Container(height=12),
                                ft.ElevatedButton("Open Login", on_click=_open_login)
                            ]
                        )
                        page.add(fb)
                        page.update()
                    except Exception as fb_err:
                        print(f"Failed to add fallback UI: {fb_err}")
            except Exception:
                pass
        except Exception as outer_e:
            print(f"Unexpected error during logout navigation: {outer_e}")

    # Keep track of the logout dialog instance
    logout_dialog = None

    def show_logout_confirmation(e):
        """Show a dialog to confirm logout."""
        nonlocal logout_dialog
        
        def on_cancel(e):
            nonlocal logout_dialog
            if logout_dialog:
                page.close(logout_dialog)
                logout_dialog = None
        
        # Define the dialog content
        logout_dialog = ft.AlertDialog(
            modal=True,
            title=ft.Text(
                "Log Out",
                weight=ft.FontWeight.BOLD,
                color="onSurface",
            ),
            content=ft.Text(
                "Are you sure you want to log out?",
                color="onSurface",
            ),
            actions=[
                ft.TextButton(
                    "Cancel",
                    on_click=on_cancel,
                ),
                ft.TextButton(
                    "Yes, logout",
                    on_click=lambda e: (page.close(logout_dialog), perform_logout(None)),
                    style=ft.ButtonStyle(color="#FF4B4B"),
                ),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )
        page.open(logout_dialog)

    def show_signup_dialog(e):
        """Show a dialog prompting guest user to sign up."""
        def go_to_signup(e):
            """Handle sign up button click - navigate to login view."""
            # Navigate to login view for registration/login flow
            page.close(signup_dialog)
            
            # Clear any view stack or route handlers
            try:
                if hasattr(page, 'views') and isinstance(page.views, list):
                    page.views.clear()
            except Exception:
                pass

            try:
                if hasattr(page, 'on_route_change'):
                    page.on_route_change = None
            except Exception:
                pass
            
            try:
                if hasattr(page, 'on_view_pop'):
                    page.on_view_pop = None
            except Exception:
                pass

            # Import and launch login view
            from views.login_view import main as login_main
            try:
                page.controls.clear()
            except Exception:
                pass
            
            try:
                page.clean()
            except Exception:
                pass
            
            try:
                page.route = "/"
            except Exception:
                pass
            
            try:
                login_main(page)
                page.update()
            except Exception as ex:
                print(f"Error launching login view: {ex}")
        
        # Define the dialog content
        signup_dialog = ft.AlertDialog(
            modal=True,
            title=ft.Text(
                "Create Account for Full Access",
                weight=ft.FontWeight.BOLD,
                color="onSurface",
            ),
            content=ft.Text(
                "To access this feature and create trip plans, please create an account.",
                color="onSurface",
                size=14,
            ),
            actions=[
                ft.TextButton(
                    "Ok",
                    on_click=lambda e: page.close(signup_dialog),
                ),
                ft.ElevatedButton(
                    "Sign up",
                    on_click=go_to_signup,
                    bgcolor="primary",
                    color="white",
                ),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )
        page.open(signup_dialog)

    # Theme toggle icon - updates based on current theme
    # Create theme toggle icon button first
    theme_icon = ft.IconButton(
        icon=ft.Icons.DARK_MODE if app_state_manager.theme_mode == ft.ThemeMode.LIGHT 
             else ft.Icons.WB_SUNNY,
        icon_size=24,
        tooltip="Toggle theme",
    )
    
    def toggle_theme(e):
        """Toggle between light and dark theme."""
        app_state_manager.toggle_theme()
        # Update the icon based on new theme
        # When in light mode, show dark mode icon (to switch to dark)
        # When in dark mode, show light mode icon (to switch to light)
        theme_icon.icon = (
            ft.Icons.DARK_MODE if app_state_manager.theme_mode == ft.ThemeMode.LIGHT 
            else ft.Icons.WB_SUNNY
        )
        theme_icon.update()
    
    # Set the on_click handler after defining the function
    theme_icon.on_click = toggle_theme

    # Header with theme toggle icon at top right
    header = ft.Container(
        padding=ft.padding.only(left=24, right=24, top=10, bottom=10),
        content=ft.Row(
            controls=[
                ft.Text(
                    "Settings",
                    size=28,
                    weight=ft.FontWeight.BOLD,
                    color="onBackground",
                ),
                theme_icon,
            ],
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
        ),
    )

    # Profile section (Redesigned)
    def go_to_edit_profile(e):
        # If user is a guest, show sign up dialog instead
        if not user:
            show_signup_dialog(e)
        else:
            page.go("/profile_edit")

    profile_section = ft.Container(
        padding=ft.padding.symmetric(vertical=20),
        alignment=ft.alignment.center,
        content=ft.Column(
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=12,
            controls=[
                # Avatar with Edit Icon
                ft.Container(
                    on_click=go_to_edit_profile,
                    content=ft.Stack(
                        controls=[
                            ft.CircleAvatar(
                                radius=40,
                                bgcolor="#46bd8d",
                                foreground_image_src=avatar_url if avatar_url else None,
                                content=ft.Text(
                                    user_initial,
                                    color="#FFFFFF",
                                    weight=ft.FontWeight.BOLD,
                                    size=32,
                                ) if not avatar_url else None,
                            ),
                            ft.Container(
                                right=0,
                                bottom=0,
                                width=24,
                                height=24,
                                bgcolor="surface",
                                border_radius=12,
                                alignment=ft.alignment.center,
                                content=ft.Icon(
                                    ft.Icons.EDIT,
                                    size=14,
                                    color="primary",
                                ),
                            ),
                        ],
                        width=80,
                        height=80,
                    ),
                ),
                # Name and Email
                ft.Column(
                    spacing=4,
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    controls=[
                        ft.Text(
                            user_name,
                            size=18,
                            weight=ft.FontWeight.BOLD,
                            color="onBackground",
                        ),
                        ft.Text(
                            user_email,
                            size=14,
                            color="#9AA4AF",
                        ),
                    ],
                ),
            ],
        ),
    )

    # About label
    about_label = ft.Container(
        padding=ft.padding.only(left=24, right=24, top=8, bottom=6),
        content=ft.Text(
            "About",
            size=13,
            weight=ft.FontWeight.W_500,
            color="#9AA4AF",
        ),
    )


    def go_to_login(e):
        """Navigate to login screen."""
        page.clean()
        # Use the route directly which is handled in main.py
        page.go("/login")

    # Settings tiles
    tiles = [
        _build_settings_tile(
            "Terms Of Use",
            icon=ft.Icons.DESCRIPTION_OUTLINED,
            icon_bg="#f5a623",
        ),
        _build_settings_tile(
            "Privacy Policy",
            icon=ft.Icons.SHIELD_OUTLINED,
            icon_bg="#29b6f6",
        ),
        _build_settings_tile(
            "App Language",
            icon=ft.Icons.LANGUAGE,
            icon_bg="#4dd0e1",
            trailing_text="English",
        ),
        _build_settings_tile(
            "Notifications and Sounds",
            icon=ft.Icons.NOTIFICATIONS_NONE,
            icon_bg="#9575cd",
        ),
    ]

    if user:
        # Authenticated user - show Logout
        tiles.append(
            _build_settings_tile(
                "Logout",
                icon=ft.Icons.LOGOUT,
                icon_bg="#ff5252",
                is_logout=True,
                on_click=show_logout_confirmation,
            )
        )
    else:
        # Guest user - show Sign Up
        tiles.append(
            _build_settings_tile(
                "Sign Up",
                icon=ft.Icons.LOGIN,
                icon_bg="#46bd8d", # Match success/primary color
                text_color="#46bd8d",
                on_click=show_signup_dialog,
            )
        )

    content_column = ft.Column(
        spacing=0,
        controls=[
            header,
            profile_section,
            about_label,
            ft.Container(
                padding=ft.padding.symmetric(horizontal=16),
                content=ft.Column(controls=tiles),
            ),
        ],
    )

    return ft.SafeArea(
        expand=True,
        content=ft.Container(
            bgcolor="background",
            expand=True,
            content=ft.Column(
                expand=True,
                controls=[
                    ft.ListView(
                        expand=True,
                        padding=0,
                        controls=[content_column],
                    )
                ],
            ),
        ),
    )


def main(page: ft.Page):
    """Standalone entry to preview the settings screen."""

    page.title = "Lakb.ai - Settings"
    page.padding = 0
    page.add(build_settings_content(page))


if __name__ == "__main__":
    ft.app(target=main)
