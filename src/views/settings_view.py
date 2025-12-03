import flet as ft


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

    def go_back(e):
        page.go("/")

    # Keep track of the bottom sheet instance
    logout_bottom_sheet = None

    def perform_logout(e):
        """Actual logout logic: send user back to login screen."""
        nonlocal logout_bottom_sheet
        from .login_view import main as login_main

        # Close bottom sheet if open
        if logout_bottom_sheet:
            page.close(logout_bottom_sheet)
            logout_bottom_sheet = None

        # Reset routing / nav controlled by home_view
        page.on_route_change = None
        page.views.clear()
        page.navigation_bar = None
        page.clean()
        login_main(page)

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

    def toggle_dark_mode(e: ft.ControlEvent):
        """Toggle app-wide dark mode using page.theme_mode."""
        enabled = e.control.value
        page.theme_mode = ft.ThemeMode.DARK if enabled else ft.ThemeMode.LIGHT

        # Optional: persist preference if storage is available
        try:
            if getattr(page, "client_storage", None) is not None:
                page.client_storage.set("dark_mode", "1" if enabled else "0")
        except Exception:
            pass

        # Just update the page to apply the new theme
        page.update()

    # Header with back arrow and title
    header = ft.Container(
        padding=ft.padding.only(left=16, right=16, top=20, bottom=12),
        content=ft.Row(
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
            controls=[
                ft.IconButton(
                    icon=ft.Icons.ARROW_BACK_IOS_NEW,
                    icon_size=18,
                    icon_color="onBackground",
                    style=ft.ButtonStyle(
                        shape={
                            ft.ControlState.DEFAULT: ft.RoundedRectangleBorder(radius=9999)
                        },
                        padding=8,
                    ),
                    on_click=go_back,
                ),
                ft.Text(
                    "Settings",
                    size=20,
                    weight=ft.FontWeight.BOLD,
                    color="onBackground",
                ),
            ],
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
                                content=ft.Text(
                                    "J",
                                    color="#FFFFFF",
                                    weight=ft.FontWeight.BOLD,
                                    size=32,
                                ),
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
                            "Juan Dela Cruz",
                            size=18,
                            weight=ft.FontWeight.BOLD,
                            color="onBackground",
                        ),
                        ft.Text(
                            "juandelacruz@gmail.com",
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

    # Dark mode switch control for "Dark Mode" row
    # Initialize value based on current page.theme_mode
    is_dark_now = (page.theme_mode == ft.ThemeMode.DARK)
    dark_mode_switch = ft.Switch(
        value=is_dark_now,
        active_color="#42b889",
        on_change=toggle_dark_mode,
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
            "Dark Mode",
            icon=ft.Icons.WB_SUNNY_OUTLINED,
            icon_bg="#ffb74d",
            trailing_control=dark_mode_switch,
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
