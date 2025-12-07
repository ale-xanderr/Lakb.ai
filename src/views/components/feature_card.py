import flet as ft
from services.favorites_service import FavoritesService
from services.api_service import APIService


def build_feature_card(
    data: dict,
    page: ft.Page,
    on_card_click=None,
    on_favorite_toggle=None,
    mode: str = "full",
    api_service: APIService = None
):
    """
    Build a reusable feature card component.
    
    Args:
        data: Dictionary containing place information
        page: Flet Page object
        on_card_click: Callback function when card is clicked (optional)
        on_favorite_toggle: Callback function when favorite button is toggled (optional)
        mode: Display mode - "full" (default, shows all info) or "compact" (only image, name, heart)
        api_service: APIService instance for fetching photo URLs
    
    Returns:
        ft.Container: The feature card container
    """
    # Initialize services if not provided
    if api_service is None:
        api_service = APIService()
    
    favorites_service = FavoritesService()
    
    # Map API data to UI fields
    title = data.get("name") or data.get("title") or "Unknown"
    address = data.get("formatted_address") or data.get("address") or ""
    place_id = data.get("place_id") or data.get("id")
    
    # Get image URL
    image_url = data.get("image_url")
    if not image_url and "photos" in data and len(data["photos"]) > 0:
        photo_ref = data["photos"][0].get("photo_reference")
        if photo_ref:
            image_url = api_service.get_photo_url(photo_ref)
    
    # Image content
    image_content = None
    if image_url:
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
                ft.Icon(ft.Icons.IMAGE_NOT_SUPPORTED_OUTLINED, color="#B0B0B0", size=40),
                ft.Text("No Image", color="#B0B0B0", size=12)
            ]
        )
    
    def handle_card_click(e):
        """Handle card click - call provided callback or default behavior"""
        if on_card_click:
            on_card_click(e, data)
        else:
            # Default behavior if no callback provided
            pass
    
    def toggle_favorite(e, item):
        """Toggle favorite status"""
        try:
            # Get current state before toggle
            place_id = item.get("place_id") or item.get("id")
            was_favorite = favorites_service.is_favorite(place_id)
            
            # Toggle the favorite
            is_fav = favorites_service.toggle_favorite(item)
            
            # Update item state
            item["is_favorite"] = is_fav
            
            # Verify the state was actually changed
            if is_fav == was_favorite:
                print(f"WARNING: Favorite state didn't change for {place_id}. Current: {is_fav}, Was: {was_favorite}")
                # Force refresh from service
                is_fav = favorites_service.is_favorite(place_id)
                item["is_favorite"] = is_fav
            
            # Update the icon immediately
            e.control.icon = ft.Icons.FAVORITE if is_fav else ft.Icons.FAVORITE_BORDER
            e.control.icon_color = "red" if is_fav else "primary"
            e.control.update()
            
            # Show feedback to user
            place_name = item.get("name") or item.get("title", "place")
            action = "added to" if is_fav else "removed from"
            print(f"DEBUG Card: {place_name} {action} favorites (ID: {place_id})")
            print(f"DEBUG Card: is_favorite check: {favorites_service.is_favorite(place_id)}")
            
            # Update page to ensure other UI elements reflect change
            if page:
                page.update()
            
            # Call the provided callback if available
            if on_favorite_toggle:
                on_favorite_toggle(e, item, is_fav)
        except Exception as ex:
            print(f"ERROR: Failed to toggle favorite: {ex}")
            import traceback
            traceback.print_exc()
            # Show error to user
            if page:
                try:
                    page.snack_bar = ft.SnackBar(
                        ft.Text(f"Failed to update favorite: {str(ex)}"),
                        bgcolor=ft.colors.ERROR,
                        duration=3000
                    )
                    page.snack_bar.open = True
                    page.update()
                except:
                    pass
    
    # Determine sizes based on mode
    if mode == "compact":
        # Compact mode for favorites grid view
        image_height = 120
        card_padding = 12
        title_size = 16
        address_size = 10
        icon_size = 20
        icon_padding = 8
        spacing = 6
        inner_spacing = 4
    else:
        # Full mode for home view
        image_height = 180
        card_padding = 16
        title_size = 18
        address_size = 11
        icon_size = 24
        icon_padding = 10
        spacing = 8
        inner_spacing = 8
    
    # Card background
    card_bg = "surface"
    
    # Build controls list based on mode
    controls = []
    
    # Image container (always shown)
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
    
    # Title and heart button row
    text_controls = [
        ft.Text(
            title,
            color="onSurface",
            size=title_size,
            weight=ft.FontWeight.BOLD,
            no_wrap=True,
            overflow=ft.TextOverflow.ELLIPSIS,
        )
    ]
    
    # Add address only in full mode
    if mode == "full":
        text_controls.append(
            ft.Text(
                address,
                color="onSurfaceVariant",
                size=address_size,
                max_lines=1,
                overflow=ft.TextOverflow.ELLIPSIS,
            )
        )
    
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
                    icon=ft.Icons.FAVORITE if data.get("is_favorite") else ft.Icons.FAVORITE_BORDER,
                    icon_color="red" if data.get("is_favorite") else "primary",
                    bgcolor="background",
                    icon_size=icon_size,
                    style=ft.ButtonStyle(
                        shape={
                            ft.ControlState.DEFAULT: ft.RoundedRectangleBorder(
                                radius=9999
                            )
                        },
                        padding=icon_padding,
                    ),
                    on_click=lambda e: toggle_favorite(e, data),
                ),
            ],
        )
    )
    
    return ft.Container(
        bgcolor=card_bg,
        border_radius=24,
        border=ft.border.all(1, ft.Colors.with_opacity(0.08, "onSurface")),
        padding=card_padding,
        margin=ft.margin.only(bottom=16) if mode == "full" else None,
        on_click=handle_card_click,
        content=ft.Column(
            spacing=spacing,
            controls=controls
        )
    )
