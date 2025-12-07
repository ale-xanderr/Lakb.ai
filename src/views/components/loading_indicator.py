import flet as ft

def create_loading_indicator(message: str = "Loading...") -> ft.Control:
    """
    Create a reusable loading indicator with a spinner and optional message.
    
    Args:
        message: The loading message to display below the spinner
        
    Returns:
        A Container with centered loading spinner and message
    """
    return ft.Container(
        padding=ft.padding.all(40),
        alignment=ft.alignment.center,
        content=ft.Column(
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=20,
            controls=[
                ft.ProgressRing(
                    width=50,
                    height=50,
                    stroke_width=4,
                    color="primary",
                ),
                ft.Text(
                    message,
                    size=14,
                    color="onSurfaceVariant",
                    text_align=ft.TextAlign.CENTER,
                ),
            ]
        )
    )
