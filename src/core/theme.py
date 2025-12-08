"""
Centralized theme configuration for the application.
This module provides a single source of truth for the app's light and dark themes.
"""
import flet as ft


def configure_theme(page: ft.Page):
    """
    Configure the page with custom light and dark themes.
    Sets up color schemes, fonts, and page transitions.
    
    Args:
        page: The Flet page to configure.
    """
    # Light Theme
    page.theme = ft.Theme(
        color_scheme=ft.ColorScheme(
            background="#fafdfc",
            on_background="#091a13",
            primary="#46bd8d",
            secondary="#95cbd9",
            tertiary="#76a2ce",
            surface="#FFFFFF",
            on_surface="#091a13",
            on_surface_variant="#5f6368",
        ),
        font_family="Poppins",
        page_transitions=ft.PageTransitionsTheme(
            android=ft.PageTransitionTheme.NONE,
            ios=ft.PageTransitionTheme.NONE,
            macos=ft.PageTransitionTheme.NONE,
            linux=ft.PageTransitionTheme.NONE,
            windows=ft.PageTransitionTheme.NONE,
        ),
    )

    # Dark Theme
    page.dark_theme = ft.Theme(
        color_scheme=ft.ColorScheme(
            background="#010403",
            on_background="#e4f6ef",
            primary="#42b889",
            secondary="#265c69",
            tertiary="#315c87",
            surface="#12161C",
            on_surface="#e4f6ef",
            on_surface_variant="#a0b3af",
        ),
        font_family="Poppins",
        page_transitions=ft.PageTransitionsTheme(
            android=ft.PageTransitionTheme.NONE,
            ios=ft.PageTransitionTheme.NONE,
            macos=ft.PageTransitionTheme.NONE,
            linux=ft.PageTransitionTheme.NONE,
            windows=ft.PageTransitionTheme.NONE,
        ),
    )

    # Set initial background color to follow theme
    page.bgcolor = "background"

    # Fonts Setup
    page.fonts = {
        "Courgette": "/fonts/Courgette-Regular.ttf",
        "Poppins": "/fonts/Poppins-Regular.ttf",
        "PoppinsBold": "/fonts/Poppins-Bold.ttf",
    }
