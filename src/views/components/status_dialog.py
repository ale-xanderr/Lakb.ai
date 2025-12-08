import flet as ft


def create_status_dialog(
    message: str,
    message_type: str = "error",  # "error", "warning", "info", "success"
    dismissible: bool = True
) -> ft.Container:
    """
    Creates a status/error dialog component that can be displayed inline.
    
    Args:
        message: The message to display
        message_type: Type of message - "error", "warning", "info", or "success"
        dismissible: Whether the dialog can be dismissed by the user
    
    Returns:
        A Container with the styled status dialog
    """
    
    # Map message types to colors and icons
    type_config = {
        "error": {
            "icon": ft.Icons.ERROR_OUTLINE_ROUNDED,
            "icon_color": "#E74C3C",
            "bg_color_light": "#FFEBEE",
            "bg_color_dark": "#4A1F1F",
            "text_color_light": "#C62828",
            "text_color_dark": "#FFCDD2",
        },
        "warning": {
            "icon": ft.Icons.WARNING_AMBER_ROUNDED,
            "icon_color": "#F39C12",
            "bg_color_light": "#FFF3E0",
            "bg_color_dark": "#4A3A1F",
            "text_color_light": "#E65100",
            "text_color_dark": "#FFE0B2",
        },
        "info": {
            "icon": ft.Icons.INFO_OUTLINE_ROUNDED,
            "icon_color": "#3498DB",
            "bg_color_light": "#E3F2FD",
            "bg_color_dark": "#1F2F4A",
            "text_color_light": "#1565C0",
            "text_color_dark": "#BBDEFB",
        },
        "success": {
            "icon": ft.Icons.CHECK_CIRCLE_OUTLINE_ROUNDED,
            "icon_color": "#27AE60",
            "bg_color_light": "#E8F5E9",
            "bg_color_dark": "#1F4A2F",
            "text_color_light": "#2E7D32",
            "text_color_dark": "#C8E6C9",
        }
    }
    
    config = type_config.get(message_type, type_config["info"])
    
    # Convert technical error messages to user-friendly ones
    user_message = format_error_message(message)
    
    # Create dismissible dialog with Ref for visibility control
    dialog_ref = ft.Ref[ft.Container]()
    
    def dismiss_dialog(e):
        if dialog_ref.current:
            dialog_ref.current.visible = False
            dialog_ref.current.update()
    
    # Build the content
    content_row = ft.Row(
        spacing=12,
        controls=[
            ft.Icon(
                name=config["icon"],
                color=config["icon_color"],
                size=24,
            ),
            ft.Container(
                expand=True,
                content=ft.Text(
                    user_message,
                    size=14,
                    weight=ft.FontWeight.W_500,
                    color=config["text_color_light"],  # Will be overridden by theme
                ),
            ),
        ]
    )
    
    # Add dismiss button if dismissible
    if dismissible:
        content_row.controls.append(
            ft.IconButton(
                icon=ft.Icons.CLOSE_ROUNDED,
                icon_size=20,
                icon_color=config["text_color_light"],
                on_click=dismiss_dialog,
                tooltip="Dismiss",
            )
        )
    
    # Create the dialog container
    dialog = ft.Container(
        ref=dialog_ref,
        padding=ft.padding.all(16),
        margin=ft.margin.only(bottom=16),
        border_radius=12,
        bgcolor=config["bg_color_light"],
        shadow=ft.BoxShadow(
            spread_radius=0,
            blur_radius=8,
            color=ft.Colors.with_opacity(0.1, "#000000"),
            offset=ft.Offset(0, 2),
        ),
        animate=ft.Animation(300, ft.AnimationCurve.EASE_OUT),
        content=content_row,
    )
    
    return dialog


def format_error_message(technical_message: str) -> str:
    """
    Convert technical error messages to user-friendly messages.
    
    Args:
        technical_message: The technical error message from the API or system
    
    Returns:
        A user-friendly error message
    """
    message_lower = technical_message.lower()
    
    # Google Places API errors
    if "400 bad request" in message_lower or "invalid request" in message_lower:
        return "Unable to load places. Please check your search query and try again."
    
    if "401" in message_lower or "unauthorized" in message_lower or "api key" in message_lower:
        return "Service authentication failed. Please contact support."
    
    if "403" in message_lower or "forbidden" in message_lower:
        return "Access to this service is currently restricted. Please try again later."
    
    if "404" in message_lower or "not found" in message_lower:
        return "The requested location or place could not be found."
    
    if "429" in message_lower or "rate limit" in message_lower or "quota" in message_lower:
        return "Too many requests. Please wait a moment and try again."
    
    if "500" in message_lower or "503" in message_lower or "server error" in message_lower:
        return "Service is temporarily unavailable. Please try again in a few moments."
    
    if "timeout" in message_lower or "timed out" in message_lower:
        return "Request timed out. Please check your connection and try again."
    
    if "network" in message_lower or "connection" in message_lower:
        return "Network error. Please check your internet connection."
    
    if "no results" in message_lower or "no places found" in message_lower:
        return "No places found matching your search. Try a different search term or location."
    
    # Geolocation errors
    if "location" in message_lower and ("permission" in message_lower or "denied" in message_lower):
        return "Location access was denied. Please enable location services to see nearby places."
    
    if "geolocation" in message_lower:
        return "Unable to determine your location. Please search for a specific place instead."
    
    # Generic fallback - return the original message if no match
    # But clean it up a bit
    if "error:" in message_lower:
        # Extract the part after "error:"
        parts = technical_message.split(":", 1)
        if len(parts) > 1:
            return parts[1].strip()
    
    return technical_message


# Example usage for status messages (not errors)
def create_info_message(message: str) -> ft.Container:
    """Quick helper for info messages"""
    return create_status_dialog(message, message_type="info", dismissible=True)


def create_success_message(message: str) -> ft.Container:
    """Quick helper for success messages"""
    return create_status_dialog(message, message_type="success", dismissible=True)


def create_warning_message(message: str) -> ft.Container:
    """Quick helper for warning messages"""
    return create_status_dialog(message, message_type="warning", dismissible=True)


def create_error_message(message: str) -> ft.Container:
    """Quick helper for error messages"""
    return create_status_dialog(message, message_type="error", dismissible=True)
