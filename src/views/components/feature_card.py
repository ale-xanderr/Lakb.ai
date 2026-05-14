import flet as ft
from services.api_service import APIService
from state import AuthStateController, ServiceManager


def build_feature_card(
    data: dict,
    page: ft.Page,
    on_card_click=None,
    on_favorite_toggle=None,
    mode: str = "full",
    api_service: APIService = None
):
    """
    Builds a reusable feature card component for displaying place information.
    Supports 'full' mode for detailed view and 'compact' mode for grids.
    
    Args:
        data: Dictionary containing place information (name, address, photos, etc.).
        page: The Flet page instance.
        on_card_click: Optional callback when the card is clicked.
        on_favorite_toggle: Optional callback when the favorite button is toggled.
        mode: Display mode - "full" (default) or "compact".
        api_service: Optional APIService instance for fetching photo URLs.
    
    Returns:
        ft.Container: The constructed feature card control.
    """
    # Initialize services if not provided
    if api_service is None:
        api_service = ServiceManager().api_service
    
    favorites_service = ServiceManager().favorites_service
    
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
    
    def show_guest_account_dialog():
        """Show dialog prompting guest user to create account for full functionality."""
        def go_to_signup(e):
            """Handle sign up button click - navigate to login view."""
            # Navigate to login view for registration
            page.close(dialog)
            
            # Clear any view stack or route handlers
            try:
                if hasattr(page, 'views') and isinstance(page.views, list):
                    page.views.clear()
            except Exception:
                pass

            try:
                if hasattr(page, 'on_route_change'):
                    page._view_route_change_handler = None
            except Exception:
                pass
            
            try:
                if hasattr(page, 'on_view_pop'):
                    page.on_view_pop = None
            except Exception:
                pass

            # Import and launch login view
            from views.login_view import main as login_main
            try:
                page.controls.clear()
            except Exception:
                pass
            
            try:
                page.clean()
            except Exception:
                pass
            
            try:
                page.route = "/"
            except Exception:
                pass
            
            try:
                login_main(page)
                page.update()
            except Exception as ex:
                print(f"Error launching login view: {ex}")
        
        dialog = ft.AlertDialog(
            modal=True,
            title=ft.Text("Create Account for Full Access"),
            content=ft.Text(
                "To add places to favorites and access all features, please create an account.",
                size=14,
            ),
            actions=[
                ft.TextButton("Ok", on_click=lambda e: page.close(dialog)),
                ft.ElevatedButton(
                    "Sign up",
                    on_click=go_to_signup,
                    bgcolor="primary",
                    color="white"
                ),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )
        page.open(dialog)
    
    def toggle_favorite(e, item):
        """Toggle favorite status"""
        try:
            # Check if user is a guest
            auth_state_controller = getattr(page, "_auth_state_controller", None)
            if auth_state_controller:
                print(f"DEBUG: Auth state - is_guest: {auth_state_controller.is_guest}, is_authenticated: {auth_state_controller.is_authenticated}")
                if auth_state_controller.is_guest:
                    # Guest users cannot add favorites - show dialog
                    print("DEBUG: Guest user detected, showing account creation dialog")
                    show_guest_account_dialog()
                    return
            else:
                print("DEBUG: No auth_state_controller found on page")
            
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
        spacing = 8
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
            width=float("inf"),
            height=image_height,
            border_radius=16,
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
            max_lines=2,
            overflow=ft.TextOverflow.ELLIPSIS,
        )
    ]
    
    # Add address - show in both modes now, but with styling matching plan_card
    text_controls.append(
        ft.Text(
            address,
            color="onSurfaceVariant",
            size=address_size,
            max_lines=2 if mode == "compact" else 1, # Allow 2 lines in compact to match plan card description style
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
                                radius=10000
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
