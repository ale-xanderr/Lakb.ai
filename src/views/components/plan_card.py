import flet as ft
from .loading_indicator import create_loading_indicator

def build_plan_card(
    data: dict,
    on_card_click=None,
):
    """
    Build a plan card component.

    Args:
        data: Dictionary containing plan information
        on_card_click: Callback function when card is clicked (optional, disabled if plan is generating)

    Returns:
        ft.Container: The plan card container
    """
    
    # Configuration from specs
    image_height = 120
    card_padding = 12
    title_size = 16
    address_size = 10
    icon_size = 20
    icon_padding = 8
    spacing = 6
    inner_spacing = 4

    # Check if plan is generating
    is_generating = data.get("is_generating", False)

    # Map data to UI fields
    title = data.get("name") or data.get("title") or "Untitled Plan"
    description = data.get("description") or data.get("summary") or ""
    if is_generating:
        description = "Generating your personalized itinerary..."
    image_url = data.get("image_url")
    
    # Image content - show loading indicator if generating
    image_content = None
    if is_generating:
        # Show loading indicator overlay
        image_content = ft.Stack(
            controls=[
                ft.Container(
                    bgcolor="#2A2A2A",
                    width=float("inf"),
                    height=float("inf"),
                ),
                ft.Container(
                    content=create_loading_indicator("Generating..."),
                    alignment=ft.alignment.center,
                    width=float("inf"),
                    height=float("inf"),
                )
            ]
        )
    elif image_url:
        image_content = ft.Image(
            src=image_url,
            fit=ft.ImageFit.COVER,
            width=float("inf"),
            height=float("inf"),
        )
    else:
        # Placeholder for missing image
        image_content = ft.Column(
            alignment=ft.MainAxisAlignment.CENTER,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            controls=[
                ft.Icon(ft.Icons.MAP_OUTLINED, color="#B0B0B0", size=30),
            ]
        )
    
    def handle_card_click(e):
        # Don't allow clicks if generating
        if is_generating:
            return
        if on_card_click:
            on_card_click(e, data)

    # Card background
    card_bg = "surface"
    
    # Build controls
    controls = []
    
    # Image container
    controls.append(
        ft.Container(
            height=image_height,
            border_radius=18,
            bgcolor="#2A2A2A",
            clip_behavior=ft.ClipBehavior.HARD_EDGE,
            content=image_content,
        )
    )
    
    controls.append(ft.Container(height=inner_spacing))
    
    # Title
    text_controls = [
        ft.Text(
            title,
            color="onSurface",
            size=title_size,
            weight=ft.FontWeight.BOLD,
            no_wrap=True,
            overflow=ft.TextOverflow.ELLIPSIS,
        ),
        ft.Text(
            description,
            color="onSurfaceVariant",
            size=address_size,
            max_lines=2,
            overflow=ft.TextOverflow.ELLIPSIS,
        )
    ]
    
    controls.append(
        ft.Row(
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
            controls=[
                ft.Column(
                    spacing=2,
                    alignment=ft.MainAxisAlignment.CENTER,
                    expand=True,
                    controls=text_controls,
                ),
                ft.IconButton(
                    icon=ft.Icons.ARROW_FORWARD if not is_generating else ft.Icons.HOURGLASS_EMPTY,
                    icon_color="primary" if not is_generating else "onSurfaceVariant",
                    bgcolor="background",
                    icon_size=icon_size,
                    disabled=is_generating,
                    style=ft.ButtonStyle(
                        shape={
                            ft.ControlState.DEFAULT: ft.RoundedRectangleBorder(
                                radius=9999
                            )
                        },
                        padding=icon_padding,
                    ),
                    on_click=handle_card_click,
                ),
            ],
        )
    )
    
    # Make card non-clickable if generating
    card_opacity = 0.6 if is_generating else 1.0
    
    return ft.Container(
        bgcolor=card_bg,
        border_radius=24,
        border=ft.border.all(1, ft.Colors.with_opacity(0.08, "onSurface")),
        padding=card_padding,
        on_click=handle_card_click if not is_generating else None,
        opacity=card_opacity,
        content=ft.Column(
            spacing=spacing,
            controls=controls
        )
    )
