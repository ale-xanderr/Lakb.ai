import flet as ft
from .login_view import main as login_main
from core.config import configure_page

def reload_splash_view(page: ft.Page):
    """
    Helper function to robustly reload the splash view.
    """
    try:
        page.views.clear()
        page.controls.clear()
        page.on_route_change = None
        page.on_view_pop = None
        page.clean()
        page.route = "/splash"
        # Ensure update happens before rebuilding to clear old UI
        page.update()
        main(page)
    except Exception as e:
        print(f"Error reloading splash view: {e}")
        main(page)

def main(page: ft.Page):
    """
    Main entry point for the Splash Screen.
    Displays the welcome screen and handles navigation to the login view.
    
    Args:
        page: The Flet page instance.
    """
    configure_page(page, title="Lakb.ai - Welcome")
    page.bgcolor = "#FFFFFF" # Initial background

    def on_get_started(e):
        # Navigate to login view using routing to support browser back button
        page.go("/login")

    # Main content
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
                        color="#091a13", # Text color from login_view
                        text_align=ft.TextAlign.CENTER,
                    ),
                    ft.Container(height=20),
                    ft.Text(
                        "Plan your perfect trip with AI",
                        size=16,
                        color="#95cbd9", # Secondary color
                        text_align=ft.TextAlign.CENTER,
                    ),
                ]
            ),
            ft.Container(height=48),
            ft.ElevatedButton(
                "Get Started",
                style=ft.ButtonStyle(
                    color="#FFFFFF",
                    bgcolor="#091a13", # Dark text color as bg for contrast
                    padding=ft.padding.symmetric(horizontal=40, vertical=20),
                    text_style=ft.TextStyle(size=18, weight=ft.FontWeight.BOLD),
                    shape=ft.RoundedRectangleBorder(radius=32),
                ),
                on_click=on_get_started,
            ),
        ]
    )

    # Background gradient for the splash page itself
    background = ft.Container(
        expand=True,
        gradient=ft.LinearGradient(
            begin=ft.alignment.top_center,
            end=ft.alignment.bottom_center,
            colors=[
                ft.Colors.with_opacity(0.15, ft.Colors.GREEN),
                ft.Colors.with_opacity(0.0, ft.Colors.GREEN),
            ],
        ),
        alignment=ft.alignment.center,
        content=content,
        # Animation properties
        opacity=0,
        offset=ft.Offset(0, 0.05),
        animate_opacity=ft.Animation(800, ft.AnimationCurve.EASE_OUT),
        animate_offset=ft.Animation(800, ft.AnimationCurve.EASE_OUT),
    )

    page.add(background)
    
    # Trigger animation
    background.opacity = 1
    background.offset = ft.Offset(0, 0)
    page.update()

if __name__ == "__main__":
    ft.app(target=main)
