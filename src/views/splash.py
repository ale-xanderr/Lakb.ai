import flet as ft
import asyncio
from .login_view import main as login_main
from .app_config import configure_page

def main(page: ft.Page):
    configure_page(page, title="Lakb.ai - Welcome")
    page.bgcolor = "#FFFFFF" # Initial background

    # Animation state
    # We will use a stack to layer the button and the expanding container
    
    # Refs for animation
    text_column_ref = ft.Ref[ft.Column]()

    async def on_get_started(e):
        # 1. Fade out the text
        text_column_ref.current.opacity = 0
        text_column_ref.current.update()

        # 2. Animate the expanding container to fill the screen
        # We use a large value to ensure it covers the screen
        expanding_circle.width = 3000 
        expanding_circle.height = 3000
        expanding_circle.border_radius = 0
        expanding_circle.update()
        
        # 3. Wait for animation to finish
        await asyncio.sleep(0.6) # Match animation duration
        
        # 4. Navigate to login view
        page.clean()
        login_main(page)

    # The expanding container (initially hidden/small behind the button)
    # We want it to start from the button's position. 
    # Since we are centering everything, we can center this too.
    expanding_circle = ft.Container(
        width=0,
        height=0,
        border_radius=100,
        gradient=ft.LinearGradient(
            begin=ft.alignment.bottom_left,
            end=ft.alignment.top_right,
            colors=["#46bd8d", "#95cbd9"], # Using primary/secondary colors from login_view
        ),
        animate=ft.Animation(500, ft.AnimationCurve.EASE_IN_OUT),
        alignment=ft.alignment.center,
    )

    # Main content
    content = ft.Column(
        alignment=ft.MainAxisAlignment.CENTER,
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        controls=[
            ft.Column(
                ref=text_column_ref,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                animate_opacity=ft.Animation(300, ft.AnimationCurve.EASE_OUT),
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
            # Wrapper to prevent layout shift when circle expands
            ft.Container(
                width=250, 
                height=80,
                alignment=ft.alignment.center,
                content=ft.Stack(
                    alignment=ft.alignment.center,
                    clip_behavior=ft.ClipBehavior.NONE,
                    controls=[
                        expanding_circle,
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
            )
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
