import flet as ft
from state import ServiceManager, AppStateManager, ProfileStateController


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
    """Build the Settings / Profile screen content.

    This is intended to be embedded inside a `View` from `home_view` routing.
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
    
    # Get services
    auth_service = service_manager.auth_service
    profile_service = service_manager.profile_service
    
    # Fetch user and profile data
    user = auth_service.get_user()
    if not user:
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

    # Keep track of the bottom sheet instance
    logout_bottom_sheet = None

    def perform_logout(e):
        """Actual logout logic: send user back to splash screen."""
        print("DEBUG: perform_logout called!")
        nonlocal logout_bottom_sheet
        
        try:
            from .components.loading_indicator import create_loading_indicator
            from core.config import configure_page

            # Step 1: Close bottom sheet if open
            if logout_bottom_sheet:
                print("DEBUG: Closing bottom sheet")
                try:
                    page.close(logout_bottom_sheet)
                    logout_bottom_sheet = None
                    page.update()
                except Exception as close_error:
                    print(f"DEBUG: Error closing bottom sheet: {close_error}")

            # Step 2: Show first loading indicator - Logging out
            print("DEBUG: Showing first loading indicator - Logging out...")
            page.clean()
            page.add(
                ft.Container(
                    expand=True,
                    bgcolor="background",
                    content=create_loading_indicator("Logging out...")
                )
            )
            page.update()

            # Step 3: Sign out and clear session from storage
            print("DEBUG: Signing out")
            auth_service.sign_out(page)
            print("DEBUG: Sign out completed")
            
            # Step 4: Show second loading indicator - Preparing splash screen
            print("DEBUG: Showing second loading indicator - Preparing splash screen...")
            page.clean()
            page.add(
                ft.Container(
                    expand=True,
                    bgcolor="background",
                    content=create_loading_indicator("Preparing splash screen...")
                )
            )
            page.update()
            
            # Step 5: COMPLETELY reset page state - remove ALL handlers and views
            print("DEBUG: Resetting page state completely")
            
            # Remove all event handlers
            page.on_route_change = None
            page.on_view_pop = None
            if hasattr(page, 'on_keyboard_event'):
                page.on_keyboard_event = None
            if hasattr(page, 'on_resize'):
                page.on_resize = None
            
            # Clear navigation
            page.navigation_bar = None
            page.appbar = None
            
            # Clear ALL views - this is critical to exit views mode
            if hasattr(page, 'views'):
                page.views.clear()
            
            # Clear all controls
            page.clean()
            
            # Reset route
            page.route = "/"
            
            # Reset page properties to default state
            page.padding = 0
            page.spacing = 0
            
            # Force update to apply state changes
            page.update()
            
            # Step 6: Configure page for splash screen (like main.py does)
            print("DEBUG: Configuring page for splash screen")
            configure_page(page, title="Lakb.ai - Welcome")
            page.bgcolor = "#FFFFFF"
            
            # Step 7: Build splash screen content
            print("DEBUG: Building splash screen content")
            
            def on_get_started(e):
                from .login_view import main as login_main
                page.clean()
                login_main(page)
            
            content = ft.Column(
                alignment=ft.MainAxisAlignment.CENTER,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                controls=[
                    ft.Column(
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                        controls=[
                            ft.Text(
                                "Lakb.ai",
                                size=50,
                                weight=ft.FontWeight.BOLD,
                                color="#091a13",
                                text_align=ft.TextAlign.CENTER,
                            ),
                            ft.Container(height=20),
                            ft.Text(
                                "Plan your perfect trip with AI",
                                size=16,
                                color="#95cbd9",
                                text_align=ft.TextAlign.CENTER,
                            ),
                        ]
                    ),
                    ft.Container(height=50),
                    ft.ElevatedButton(
                        "Get Started",
                        style=ft.ButtonStyle(
                            color="#FFFFFF",
                            bgcolor="#091a13",
                            padding=ft.padding.symmetric(horizontal=40, vertical=20),
                            text_style=ft.TextStyle(size=18, weight=ft.FontWeight.BOLD),
                            shape=ft.RoundedRectangleBorder(radius=30),
                        ),
                        on_click=on_get_started,
                    ),
                ]
            )
            
            background = ft.Container(
                expand=True,
                gradient=ft.LinearGradient(
                    begin=ft.alignment.top_left,
                    end=ft.alignment.bottom_right,
                    colors=["#fafdfc", "#e4f6ef"],
                ),
                alignment=ft.alignment.center,
                content=content,
            )
            
            # Step 8: Add splash screen content
            print("DEBUG: Adding splash screen content to page")
            page.clean()  # Final clean before adding splash
            page.add(background)
            print("DEBUG: Splash screen content added")
            page.update()
            print("DEBUG: Page update completed - splash screen should be visible")
            
        except Exception as ex:
            print(f"ERROR in perform_logout: {ex}")
            import traceback
            traceback.print_exc()

    def dismiss_bottom_sheet(e):
        nonlocal logout_bottom_sheet
        if logout_bottom_sheet:
            page.close(logout_bottom_sheet)
            logout_bottom_sheet = None

    def show_logout_confirmation(e):
        """Show a bottom sheet to confirm logout."""
        nonlocal logout_bottom_sheet
        
        # Define the bottom sheet content
        logout_bottom_sheet = ft.BottomSheet(
            content=ft.Container(
                padding=ft.padding.symmetric(vertical=20, horizontal=24),
                bgcolor="surface",
                border_radius=ft.border_radius.only(top_left=20, top_right=20),
                content=ft.Column(
                    tight=True,
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    controls=[
                        ft.Container(
                            width=40,
                            height=4,
                            bgcolor=ft.Colors.GREY_300,
                            border_radius=2,
                            margin=ft.margin.only(bottom=20),
                        ),
                        ft.Text(
                            "Log Out",
                            size=20,
                            weight=ft.FontWeight.BOLD,
                            color="onSurface",
                        ),
                        ft.Text(
                            "Are you sure you want to log out?",
                            size=14,
                            color="#9AA4AF",
                            text_align=ft.TextAlign.CENTER,
                        ),
                        ft.Container(height=20),
                        ft.Row(
                            spacing=16,
                            controls=[
                                ft.ElevatedButton(
                                    text="Cancel",
                                    expand=True,
                                    style=ft.ButtonStyle(
                                        color="onSurface",
                                        bgcolor=ft.Colors.TRANSPARENT,
                                        elevation=0,
                                        side={
                                            ft.ControlState.DEFAULT: ft.BorderSide(1, "#E0E0E0")
                                        },
                                        shape={
                                            ft.ControlState.DEFAULT: ft.RoundedRectangleBorder(radius=12)
                                        },
                                        padding=16,
                                    ),
                                    on_click=dismiss_bottom_sheet,
                                ),
                                ft.ElevatedButton(
                                    text="Yes, Logout",
                                    expand=True,
                                    style=ft.ButtonStyle(
                                        color="white",
                                        bgcolor="#FF4B4B",
                                        elevation=0,
                                        shape={
                                            ft.ControlState.DEFAULT: ft.RoundedRectangleBorder(radius=12)
                                        },
                                        padding=16,
                                    ),
                                    on_click=perform_logout,
                                ),
                            ],
                        ),
                        ft.Container(height=10),
                    ],
                ),
            ),
        )
        page.open(logout_bottom_sheet)

    # Header (redesigned to match Favorites view)
    header = ft.Container(
        padding=ft.padding.only(left=24, right=24, top=10, bottom=10),
        content=ft.Text(
            "Settings",
            size=28,
            weight=ft.FontWeight.BOLD,
            color="onBackground",
        ),
    )

    # Profile section (Redesigned)
    def go_to_edit_profile(e):
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

    # Theme selection logic
    theme_bottom_sheet = None
    
    # Create a text control that we can update dynamically
    theme_text_control = ft.Text(
        "Dark" if app_state_manager.theme_mode == ft.ThemeMode.DARK else "Light",
        size=12,
        color="#9AA4AF",
    )

    def set_theme(e, mode):
        nonlocal theme_bottom_sheet
        app_state_manager.set_theme_mode(mode)
        
        # Update the text control
        theme_text_control.value = "Dark" if mode == ft.ThemeMode.DARK else "Light"
        theme_text_control.update()

        if theme_bottom_sheet:
            page.close(theme_bottom_sheet)
            theme_bottom_sheet = None

    def dismiss_theme_sheet(e):
        nonlocal theme_bottom_sheet
        if theme_bottom_sheet:
            page.close(theme_bottom_sheet)
            theme_bottom_sheet = None

    def show_theme_selector(e):
        nonlocal theme_bottom_sheet
        
        theme_bottom_sheet = ft.BottomSheet(
            content=ft.Container(
                padding=ft.padding.symmetric(vertical=20, horizontal=24),
                bgcolor="surface",
                border_radius=ft.border_radius.only(top_left=20, top_right=20),
                content=ft.Column(
                    tight=True,
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    controls=[
                        ft.Container(
                            width=40,
                            height=4,
                            bgcolor=ft.Colors.GREY_300,
                            border_radius=2,
                            margin=ft.margin.only(bottom=20),
                        ),
                        ft.Text(
                            "App Theme",
                            size=20,
                            weight=ft.FontWeight.BOLD,
                            color="onSurface",
                        ),
                        ft.Container(height=20),
                        ft.Row(
                            spacing=16,
                            controls=[
                                ft.ElevatedButton(
                                    text="Light Mode",
                                    expand=True,
                                    style=ft.ButtonStyle(
                                        color="onSurface",
                                        bgcolor=ft.Colors.TRANSPARENT,
                                        elevation=0,
                                        side={
                                            ft.ControlState.DEFAULT: ft.BorderSide(1, "#E0E0E0")
                                        },
                                        shape={
                                            ft.ControlState.DEFAULT: ft.RoundedRectangleBorder(radius=12)
                                        },
                                        padding=16,
                                    ),
                                    on_click=lambda e: set_theme(e, ft.ThemeMode.LIGHT),
                                ),
                                ft.ElevatedButton(
                                    text="Dark Mode",
                                    expand=True,
                                    style=ft.ButtonStyle(
                                        color="white",
                                        bgcolor="#42b889",
                                        elevation=0,
                                        shape={
                                            ft.ControlState.DEFAULT: ft.RoundedRectangleBorder(radius=12)
                                        },
                                        padding=16,
                                    ),
                                    on_click=lambda e: set_theme(e, ft.ThemeMode.DARK),
                                ),
                            ],
                        ),
                        ft.Container(height=10),
                        ft.TextButton(
                            "Cancel",
                            style=ft.ButtonStyle(color="onSurface"),
                            on_click=dismiss_theme_sheet
                        )
                    ],
                ),
            ),
        )
        page.open(theme_bottom_sheet)

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
            "Dark Mode",
            icon=ft.Icons.WB_SUNNY_OUTLINED,
            icon_bg="#ffb74d",
            trailing_control=ft.Row(
                spacing=10,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
                controls=[
                    theme_text_control,
                    ft.Icon(
                        ft.Icons.CHEVRON_RIGHT,
                        size=18,
                        color="#CED4DA",
                    ),
                ],
            ),
            on_click=show_theme_selector,
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
        _build_settings_tile(
            "Logout",
            icon=ft.Icons.LOGOUT,
            icon_bg="#ff5252",
            is_logout=True,
            on_click=show_logout_confirmation,
        ),
    ]

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
