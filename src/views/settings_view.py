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

    def perform_logout(e):
        """Actual logout logic: send user back to splash screen."""
        # Sign out and clear session from storage
        auth_service.sign_out(page)
        
        # Navigate to splash screen (same pattern as password_reset_view.py)
        from .splash import main as splash_main
        page.clean()
        splash_main(page)

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
