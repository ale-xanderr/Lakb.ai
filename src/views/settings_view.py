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
    """Reusable modern settings row."""

    # Logout row is always highlighted red
    effective_text_color = "#FF4B4B" if is_logout else (text_color or "onSurface")
    effective_tile_bg = tile_bg or "surface"

    return ft.Container(
        bgcolor=effective_tile_bg,
        border_radius=16,
        padding=ft.padding.symmetric(horizontal=20, vertical=16),
        margin=ft.margin.only(bottom=12),
        on_click=on_click,
        ink=True,
        content=ft.Row(
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
            controls=[
                ft.Row(
                    vertical_alignment=ft.CrossAxisAlignment.CENTER,
                    spacing=16,
                    controls=[
                        ft.Container(
                            width=40,
                            height=40,
                            border_radius=20,
                            bgcolor=icon_bg,
                            alignment=ft.alignment.center,
                            content=ft.Icon(icon, size=20, color="#FFFFFF"),
                        ),
                        ft.Text(
                            title,
                            size=16,
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
                            spacing=8,
                            vertical_alignment=ft.CrossAxisAlignment.CENTER,
                            controls=[
                                ft.Text(
                                    trailing_text or "",
                                    size=14,
                                    color="#9AA4AF",
                                )
                                if trailing_text
                                else ft.Container(),
                                ft.Icon(
                                    ft.Icons.CHEVRON_RIGHT,
                                    size=20,
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
    
    is_authenticated = auth_state_controller.is_authenticated
    user_name = "Guest User"
    user_email = "guest@example.com"
    user_initial = "G"
    avatar_url = None
    user_id = None
    
    if is_authenticated:
        user = auth_state_controller.user
        email = ""
        meta = {}
        
        if hasattr(user, 'user') and user.user:
             user_obj = user.user
             email = getattr(user_obj, 'email', "")
             user_id = getattr(user_obj, 'id', None)
             meta = getattr(user_obj, 'user_metadata', {}) or {}
        elif isinstance(user, dict):
             email = user.get("email", "")
             user_id = user.get("id")
             meta = user.get("user_metadata", {}) or {}
        else:
             email = getattr(user, 'email', "")
             user_id = getattr(user, 'id', None)
             meta = getattr(user, 'user_metadata', {}) or {}
             
        user_name = meta.get("first_name") or meta.get("full_name") or (email.split("@")[0] if email else "User")
        user_email = email
        avatar_url = meta.get("avatar_url")
        
        if user_id:
            cached = page.session.get(f"profile_{user_id}")
            if cached:
                if cached.get("first_name"):
                    user_name = cached.get("first_name")
                if cached.get("avatar_url"):
                    avatar_url = cached.get("avatar_url")
                    
        user_initial = user_name[0].upper() if user_name else "U"

    # We set values explicitly straight from cached Auth data
    user_name_text = ft.Text(user_name, size=18, weight=ft.FontWeight.BOLD, color="onBackground")
    user_email_text = ft.Text(user_email, size=14, color="#9AA4AF")
    avatar_text = ft.Text(user_initial, color="#FFFFFF", weight=ft.FontWeight.BOLD, size=32)
    avatar_control = ft.CircleAvatar(
        radius=40,
        bgcolor="#46bd8d",
        content=None if avatar_url else avatar_text,
        foreground_image_src=avatar_url,
    )
    
    # We will fetch latest profile data asynchronously to avoid blocking UI on connection failures
    def fetch_latest_profile(u_id, current_name, current_avatar):
        if not u_id: return
        try:
            profile_data = profile_service.get_user_profile(u_id)
            if profile_data:
                page.session.set(f"profile_{u_id}", profile_data)
                new_name = profile_data.get("first_name")
                new_avatar = profile_data.get("avatar_url")
                
                changed = False
                if new_name and new_name != current_name:
                    user_name_text.value = new_name
                    avatar_text.value = new_name[0].upper()
                    changed = True
                
                if new_avatar and new_avatar != current_avatar:
                    avatar_control.foreground_image_src = new_avatar
                    avatar_control.content = None
                    changed = True
                    
                if changed and user_name_text.page:
                    try:
                        user_name_text.update()
                        avatar_control.update()
                    except Exception:
                        pass
        except Exception:
            pass

    # Start a background thread to fetch data if authenticated
    if user_id:
        import threading
        threading.Thread(target=fetch_latest_profile, args=(user_id, user_name, avatar_url), daemon=True).start()

    def go_back(e):
        page.go("/")

    def perform_logout(e):
        """Actual logout logic: sign out and show the login screen."""
        # 1. Orchestrate clearing disk session, db tokens, and sweeping all app singletons
        service_manager.logout_service.logout(page)

        # 2. CRITICAL: Tear down ALL routing/navigation handlers from the current
        #    home_view session. If we leave page.on_route_change pointing at the old
        #    home_view router closure, any subsequent tap/interaction will fire that
        #    dead closure (whose controls no longer exist), causing total UI freeze.
        try:
            page.on_route_change = None
        except Exception:
            pass
        try:
            page.on_view_pop = None
        except Exception:
            pass
        try:
            page._view_route_change_handler = None
        except Exception:
            pass

        # 3. Also clear the auth controller state so any lingering callbacks
        #    that check is_authenticated see a clean slate.
        try:
            auth_ctrl = getattr(page, '_auth_state_controller', None)
            if auth_ctrl:
                auth_ctrl.reset()
        except Exception:
            pass

        # 4. Clear page.session so stale profile data (avatar, name) from the
        #    previous user's session is never shown to the next logged-in user.
        try:
            page.session.clear()
        except Exception:
            pass

        # 5. Remove any DatePicker overlays left behind by /plan_trip visits.
        #    Each visit appends controls to page.overlay without removing them,
        #    causing them to accumulate over multiple cycles.
        try:
            plan_trip_overlays = getattr(page, "_plan_trip_overlays", None)
            if plan_trip_overlays:
                for o in plan_trip_overlays:
                    try:
                        if o in page.overlay:
                            page.overlay.remove(o)
                    except Exception:
                        pass
                page._plan_trip_overlays = None
        except Exception:
            pass

        # 6. Wipe Flet's view stack and all page controls.
        try:
            page.views.clear()
        except Exception:
            pass
        try:
            page.controls.clear()
        except Exception:
            pass
        try:
            page.clean()
        except Exception:
            pass

        # 7. Navigate to the login screen.
        from .login_view import main as login_main
        print("Logout: invoking login_main")
        try:
            login_main(page)
            print("Logout: login_main completed")
        except Exception as e:
            import traceback
            print(f"Error launching login view after logout: {e}")
            traceback.print_exc()

        try:
            page.update()
        except Exception:
            pass


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
            
            # CRITICAL: Clear ALL route/nav handlers from the home_view session
            # before launching the login view (same fix as in perform_logout).
            try:
                page.on_route_change = None
            except Exception:
                pass
            try:
                page.on_view_pop = None
            except Exception:
                pass
            try:
                page._view_route_change_handler = None
            except Exception:
                pass

            # Wipe Flet view stack and controls.
            try:
                page.views.clear()
            except Exception:
                pass
            try:
                page.controls.clear()
            except Exception:
                pass
            try:
                page.clean()
            except Exception:
                pass

            # Import and launch login view
            from views.login_view import main as login_main
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
        padding=ft.padding.only(left=24, right=24, top=8, bottom=8),
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
        if not is_authenticated:
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
                            avatar_control,
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
                        user_name_text,
                        user_email_text,
                    ],
                ),
            ],
        ),
    )

    # About label
    about_label = ft.Container(
        padding=ft.padding.only(left=24, right=24, top=8, bottom=8),
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

    if is_authenticated:
        # Authenticated user (online or offline) - show Logout
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
            gradient=ft.LinearGradient(
                begin=ft.alignment.top_center,
                end=ft.alignment.bottom_center,
                colors=[
                    ft.Colors.with_opacity(0.15, ft.Colors.GREEN),
                    ft.Colors.with_opacity(0.0, ft.Colors.GREEN),
                ],
            ),
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
