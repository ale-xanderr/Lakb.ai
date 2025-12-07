import flet as ft
from .login_view import main as login_main
from core.config import configure_page

def main(page: ft.Page):
    configure_page(page, title="Lakb.ai - Welcome")
    page.bgcolor = "#FFFFFF" # Initial background

    def on_get_started(e):
        # Navigate directly to login view without animation
        page.clean()
        login_main(page)

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
            ft.Container(height=50),
            ft.ElevatedButton(
                "Get Started",
                style=ft.ButtonStyle(
                    color="#FFFFFF",
                    bgcolor="#091a13", # Dark text color as bg for contrast
                    padding=ft.padding.symmetric(horizontal=40, vertical=20),
                    text_style=ft.TextStyle(size=18, weight=ft.FontWeight.BOLD),
                    shape=ft.RoundedRectangleBorder(radius=30),
                ),
                on_click=on_get_started,
            ),
        ]
    )

    # Background gradient for the splash page itself
    background = ft.Container(
        expand=True,
        gradient=ft.LinearGradient(
            begin=ft.alignment.top_left,
            end=ft.alignment.bottom_right,
            colors=["#fafdfc", "#e4f6ef"], # Light background colors
        ),
        alignment=ft.alignment.center,
        content=content,
    )

    page.add(background)

if __name__ == "__main__":
    ft.app(target=main)
