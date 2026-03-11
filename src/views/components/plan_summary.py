import flet as ft
from core.config import APP_WIDTH
from core.supabase_client import get_supabase_client
from datetime import datetime

def build_plan_summary_view(on_back, trip_data=None, page=None, plan_id=None, on_delete_callback=None) -> ft.Control:
    """
    View for displaying the summary of a planned trip.
    
    Args:
        on_back: Callback fired when the back button is clicked.
        trip_data: Dictionary containing trip information from plan_trip view.
                   Expected keys: destination, date_from, date_to, budget_min, budget_max,
                   travel_style, time_preference, activity, dietary.
        page: The Flet page instance.
        plan_id: Optional ID of the plan (for deletion).
        on_delete_callback: Optional callback fired after plan deletion.
    """
    
    # Default values if trip_data is not provided
    if trip_data is None:
        trip_data = {}
    
    # Handler for deleting the plan
    def handle_delete_plan(e, plan_id_to_delete, on_back_callback, page_ref):
        """Handle plan deletion with confirmation dialog."""
        print(f"DEBUG: handle_delete_plan called with plan_id={plan_id_to_delete}, page_ref={page_ref}")
        
        if not plan_id_to_delete:
            print("DEBUG: No plan_id provided")
            if page_ref:
                page_ref.snack_bar = ft.SnackBar(
                    content=ft.Text("Cannot delete: Plan ID not available"),
                    bgcolor="error"
                )
                page_ref.snack_bar.open = True
                page_ref.update()
            return
        
        if not page_ref:
            print("Error: Page reference not available for deletion")
            return
        
        print("DEBUG: Showing confirmation dialog")
        
        # Function to perform the actual deletion
        def perform_delete():
            supabase = get_supabase_client()
            if not supabase:
                page_ref.snack_bar = ft.SnackBar(
                    content=ft.Text("Database connection not available"),
                    bgcolor="error"
                )
                page_ref.snack_bar.open = True
                page_ref.update()
                return
            
            try:
                # Delete the plan from database
                response = supabase.table("plans").delete().eq("id", plan_id_to_delete).execute()
                
                # Show success message
                page_ref.snack_bar = ft.SnackBar(
                    content=ft.Text("Plan deleted successfully"),
                    bgcolor="success"
                )
                page_ref.snack_bar.open = True
                page_ref.update()
                
                # Call refresh callback if provided (to refresh plans view)
                if on_delete_callback:
                    on_delete_callback()
                
                # Navigate back to plans view
                if on_back_callback:
                    on_back_callback(e)
                
            except Exception as error:
                print(f"Error deleting plan: {error}")
                page_ref.snack_bar = ft.SnackBar(
                    content=ft.Text(f"Failed to delete plan: {str(error)}"),
                    bgcolor="error"
                )
                page_ref.snack_bar.open = True
                page_ref.update()
        
        # Create confirmation dialog with Yes/No buttons
        def on_confirm_delete(e):
            page_ref.close(delete_dialog)
            # Perform deletion after dialog closes
            perform_delete()
        
        def on_cancel(e):
            page_ref.close(delete_dialog)
        
        # Create confirmation dialog
        delete_dialog = ft.AlertDialog(
            modal=True,
            title=ft.Text("Delete Plan", weight=ft.FontWeight.BOLD),
            content=ft.Text("Are you sure you want to delete this plan? This action cannot be undone."),
            actions=[
                ft.TextButton("No", on_click=on_cancel),
                ft.TextButton(
                    "Yes",
                    on_click=on_confirm_delete,
                    style=ft.ButtonStyle(color="error")
                ),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )
        
        # Open the dialog
        page_ref.open(delete_dialog)
    
    # Helper function to parse date (handles ISO strings and datetime objects)
    def parse_date(date_value):
        if date_value is None:
            return None
        if isinstance(date_value, datetime):
            return date_value
        if isinstance(date_value, str):
            # Try common date formats
            formats = [
                "%Y-%m-%dT%H:%M:%S",  # ISO with time
                "%Y-%m-%dT%H:%M:%S.%f",  # ISO with microseconds
                "%Y-%m-%dT%H:%M:%S%z",  # ISO with timezone
                "%Y-%m-%d",  # Simple date
            ]
            for fmt in formats:
                try:
                    return datetime.strptime(date_value.split('+')[0].split('Z')[0], fmt)
                except:
                    continue
        return None
    
    # Helper function to format date
    def format_date(date_value):
        parsed = parse_date(date_value)
        if parsed is None:
            return "Not set"
        return parsed.strftime("%b %d, %Y")
    
    # Helper function to calculate duration
    def calculate_duration(date_from, date_to):
        parsed_from = parse_date(date_from)
        parsed_to = parse_date(date_to)
        if parsed_from is None or parsed_to is None:
            return "Not set"
        delta = parsed_to - parsed_from
        days = delta.days + 1
        from_str = parsed_from.strftime("%b %d")
        to_str = parsed_to.strftime("%b %d, %Y")
        return f"{days} Day{'s' if days != 1 else ''} ({from_str} - {to_str})"
    
    # Helper function to format budget
    def format_budget(min_val, max_val):
        if not min_val and not max_val:
            return "Not set"
        
        # Convert string to int if possible
        try:
            min_int = int(min_val) if min_val else None
        except (ValueError, TypeError):
            min_int = None
            
        try:
            max_int = int(max_val) if max_val else None
        except (ValueError, TypeError):
            max_int = None
        
        min_str = f"₱{min_int:,}" if min_int else "Not set"
        max_str = f"₱{max_int:,}" if max_int else "Not set"
        
        if min_int and max_int:
            return f"{min_str} - {max_str}"
        elif min_int:
            return f"From {min_str}"
        elif max_int:
            return f"Up to {max_str}"
        return "Not set"
    
    # Helper function to create summary card
    def create_summary_card(icon, icon_color, title, value):
        return ft.Container(
            bgcolor="surface",
            border_radius=16,
            border=ft.border.all(1, ft.Colors.with_opacity(0.08, "onSurface")),
            padding=16,
            margin=ft.margin.only(bottom=8),
            content=ft.Row(
                controls=[
                    ft.Container(
                        width=48,
                        height=48,
                        border_radius=24,
                        bgcolor=ft.Colors.with_opacity(0.1, icon_color),
                        alignment=ft.alignment.center,
                        content=ft.Icon(icon, color=icon_color, size=28)
                    ),
                    ft.Column(
                        controls=[
                            ft.Text(title, size=12, color="onSurfaceVariant", weight=ft.FontWeight.W_500),
                            ft.Text(
                                value if value else "Not set",
                                size=16,
                                weight=ft.FontWeight.BOLD,
                                color="onSurface"
                            )
                        ],
                        spacing=4,
                        expand=True,
                        alignment=ft.MainAxisAlignment.CENTER
                    )
                ],
                spacing=16,
                vertical_alignment=ft.CrossAxisAlignment.CENTER
            )
        )
    
    # -------------------------
    # Image Gallery - Use images from itinerary places
    # -------------------------
    # Collect images from itinerary places
    image_urls = []
    itinerary_data = trip_data.get("itinerary", [])
    for day_data in itinerary_data:
        places = day_data.get("places", [])
        for place in places:
            image_url = place.get("image_url")
            if image_url and image_url not in image_urls:
                image_urls.append(image_url)
                if len(image_urls) >= 5:  # Limit to 5 images
                    break
        if len(image_urls) >= 5:
            break
    
    # Build image row - similar to destination_card.py
    def build_carousel_items():
        if image_urls:
            images = [
                ft.Container(
                    width=300,
                    height=248,
                    border_radius=16,
                    clip_behavior=ft.ClipBehavior.HARD_EDGE,
                    content=ft.Image(
                        src=url,
                        fit=ft.ImageFit.COVER,
                        error_content=ft.Container(bgcolor="grey")
                    )
                ) for url in image_urls
            ]
            return [ft.Container(width=16)] + images + [ft.Container(width=16)]
        else:
            # Show placeholder if no images
            return [
                ft.Container(width=16),
                ft.Container(
                    width=300,
                    height=248,
                    border_radius=16,
                    bgcolor="surfaceVariant",
                    alignment=ft.alignment.center,
                    content=ft.Column(
                        alignment=ft.MainAxisAlignment.CENTER,
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                        controls=[
                            ft.Icon(ft.Icons.IMAGE, size=50, color="onSurfaceVariant"),
                            ft.Text("No images available", color="onSurfaceVariant", size=12)
                        ]
                    )
                ),
                ft.Container(width=16)
            ]
    
    images_row = ft.Container(
        height=248,
        padding=ft.padding.only(top=16, bottom=16),
        content=ft.Row(
            scroll=ft.ScrollMode.HIDDEN,
            spacing=12,
            controls=build_carousel_items()
        )
    )

    # -------------------------
    # Tabs Content
    # -------------------------
    
    # Tab 1: Summary - Display all inputs from plan_trip
    destination = trip_data.get("destination", "")
    date_from = trip_data.get("date_from")
    date_to = trip_data.get("date_to")
    budget_min = trip_data.get("budget_min", "")
    budget_max = trip_data.get("budget_max", "")
    travel_style = trip_data.get("travel_style", "")
    time_preference = trip_data.get("time_preference", "")
    activity = trip_data.get("activity", "")
    dietary = trip_data.get("dietary", "")
    
    summary_content = ft.Container(
        padding=20,
        content=ft.Column(
            controls=[
                ft.Text("Trip Summary", size=24, weight=ft.FontWeight.BOLD, color="onSurface"),
                ft.Container(height=8),
                
                # Destination
                create_summary_card(
                    ft.Icons.LOCATION_ON,
                    ft.Colors.BLUE,
                    "Destination",
                    destination if destination else "Not set"
                ),
                
                # Duration
                create_summary_card(
                    ft.Icons.CALENDAR_MONTH,
                    ft.Colors.GREEN,
                    "Duration",
                    calculate_duration(date_from, date_to)
                ),
                
                # Budget Range
                create_summary_card(
                    ft.Icons.MONETIZATION_ON,
                    ft.Colors.ORANGE,
                    "Budget Range",
                    format_budget(budget_min, budget_max)
                ),
                
                # Travel Style
                create_summary_card(
                    ft.Icons.CATEGORY,
                    ft.Colors.PURPLE,
                    "Travel Style",
                    travel_style if travel_style else "Not set"
                ),
                
                # Time-base Preference
                create_summary_card(
                    ft.Icons.ACCESS_TIME,
                    ft.Colors.INDIGO,
                    "Time-base Preference",
                    time_preference if time_preference else "Not set"
                ),
                
                # Activity
                create_summary_card(
                    ft.Icons.EXPLORE,
                    ft.Colors.RED,
                    "Activity",
                    activity if activity else "Not set"
                ),
                
                # Dietary Requirements
                create_summary_card(
                    ft.Icons.RESTAURANT,
                    ft.Colors.TEAL,
                    "Dietary Requirements",
                    dietary if dietary and dietary != "None" else "None"
                ),
            ],
            scroll=ft.ScrollMode.AUTO,
            spacing=0,
        )
    )

    # Tab 2: Itinerary
    # Helper to create an itinerary card
    def create_itinerary_card(place_data, place_name, rating=None, location=None, description=None, image_url=None):
        rating_text = f"{rating:.1f}" if rating else "N/A"
        location_text = location or "Location not available"
        
        # Build column controls, filtering out None values
        column_controls = [
            ft.Text(place_name, weight=ft.FontWeight.BOLD, size=16, color="onSurface"),
        ]
        
        if rating:
            column_controls.append(
                ft.Row([
                    ft.Icon(ft.Icons.STAR, size=16, color=ft.Colors.AMBER),
                    ft.Text(rating_text, size=14, color="onSurface")
                ], spacing=2)
            )
        
        column_controls.append(
            ft.Text(location_text, size=12, color="onSurfaceVariant")
        )
        
        if description:
            column_controls.append(
                ft.Text(description, size=12, color="onSurfaceVariant")
            )
        
        card_content = [
            ft.Icon(ft.Icons.LOCATION_ON, size=40, color=ft.Colors.RED_400),
            ft.Column(
                controls=column_controls,
                spacing=2,
                expand=True
            )
        ]
        
        # Handler for card click - navigate to destination view
        def handle_card_click(e):
            if page is None:
                # Try to get page from the control
                control_page = e.control.page if hasattr(e.control, 'page') else None
                if control_page is None:
                    print("Warning: Cannot navigate - page not available")
                    return
                nav_page = control_page
            else:
                nav_page = page
            
            # Normalize place data for destination view
            normalized_place = {
                "place_id": place_data.get("place_id") or place_data.get("id"),
                "name": place_data.get("name", place_name),
                "address": place_data.get("formatted_address") or place_data.get("address") or location_text,
                "rating": place_data.get("rating", rating) or 0.0,
                "user_rating_count": place_data.get("user_rating_count", 0),
                "description": place_data.get("description", description),
                "photos": place_data.get("photos", []),
                "reviews": place_data.get("reviews", []),
                "image_url": place_data.get("image_url", image_url),
                "google_maps_url": place_data.get("google_maps_url"),
                "location": place_data.get("location"),
            }
            
            # Navigate to destination view by pushing a new view
            # This allows the back button to return to plan_summary
            from .destination_card import build_destination_page
            from .nav_bar import create_navigation_bar
            
            def on_back_from_destination(e):
                # Pop the destination view to go back to plan_summary
                if len(nav_page.views) > 1:
                    nav_page.views.pop()
                    nav_page.update()
            
            # Get navigation controller for nav bar index
            navigation_controller = getattr(nav_page, "_navigation_controller", None)
            nav_index = navigation_controller.current_nav_index if navigation_controller else 1  # Default to Plans tab
            
            def on_nav_change(e):
                if not navigation_controller:
                    return
                idx = e.control.selected_index
                navigation_controller.current_nav_index = idx
                
                # Navigate using the navigation controller to mimic home_view behavior
                if idx == 0:
                    navigation_controller.navigate_home()
                elif idx == 1:
                    navigation_controller.navigate_plans()
                elif idx == 2:
                    navigation_controller.navigate_favorites()
                else:
                    nav_page.go(nav_page.route or "/")

            nav_page.views.append(
                ft.View(
                    "/destination",
                    controls=[build_destination_page(nav_page, normalized_place, on_back=on_back_from_destination)],
                    padding=0,
                    bgcolor="background",
                    navigation_bar=create_navigation_bar(
                        selected_index=nav_index,
                        on_change=on_nav_change,
                    ),
                )
            )
            nav_page.update()
        
        return ft.Container(
            bgcolor="surface",
            border_radius=16,
            border=ft.border.all(1, ft.Colors.with_opacity(0.08, "onSurface")),
            padding=8,
            margin=ft.margin.only(bottom=8),
            ink=True,  # Add ripple effect on click
            on_click=handle_card_click,
            content=ft.Row(
                controls=card_content,
                alignment=ft.MainAxisAlignment.START,
                vertical_alignment=ft.CrossAxisAlignment.CENTER
            )
        )
    
    # Build itinerary from trip_data
    itinerary_items = []
    itinerary_data = trip_data.get("itinerary", [])
    
    if itinerary_data and len(itinerary_data) > 0:
        for day_data in itinerary_data:
            day_num = day_data.get("day", 1)
            day_date = day_data.get("date", "")
            places = day_data.get("places", [])
            
            # Day header
            day_text = f"Day {day_num}"
            if day_date:
                try:
                    parsed_date = parse_date(day_date)
                    if parsed_date:
                        day_text += f" - {parsed_date.strftime('%b %d, %Y')}"
                except:
                    pass
            
            itinerary_items.append(
                ft.Text(day_text, size=18, weight=ft.FontWeight.BOLD, color="onSurface")
            )
            
            # Places for this day
            if places and len(places) > 0:
                for place in places:
                    place_name = place.get("name", "Unknown Place")
                    rating = place.get("rating")
                    location = place.get("formatted_address") or place.get("location", "")
                    description = place.get("description", "")
                    image_url = place.get("image_url")
                    
                    itinerary_items.append(
                        create_itinerary_card(
                            place_data=place,  # Pass full place data
                            place_name=place_name,
                            rating=rating,
                            location=location,
                            description=description,
                            image_url=image_url
                        )
                    )
            else:
                itinerary_items.append(
                    ft.Text("No places scheduled for this day.", size=12, color="onSurfaceVariant", italic=True)
                )
            
            # Add spacing between days (except after last day)
            if day_data != itinerary_data[-1]:
                itinerary_items.append(ft.Container(height=16))
    else:
        # No itinerary data - show message
        itinerary_items.append(
            ft.Text("Itinerary is being generated...", size=14, color="onSurfaceVariant", italic=True)
        )

    itinerary_content = ft.Container(
        padding=20,
        content=ft.Column(
            controls=itinerary_items,
            scroll=ft.ScrollMode.AUTO,
        )
    )

    # Tab 3: Tips
    tips_list = trip_data.get("tips", [])
    tips_controls = [
        ft.Text("Travel Tips", size=20, weight=ft.FontWeight.BOLD, color="onSurface"),
    ]
    
    if tips_list and len(tips_list) > 0:
        for i, tip in enumerate(tips_list, 1):
            tips_controls.append(
                ft.Text(f"{i}. {tip}", size=14, color="onSurface")
            )
    else:
        tips_controls.append(
            ft.Text("No tips available yet.", size=14, color="onSurfaceVariant", italic=True)
        )
    
    tips_content = ft.Container(
        padding=20,
        content=ft.Column(
            controls=tips_controls,
            scroll=ft.ScrollMode.AUTO,
        )
    )

    # Tabs Control
    tabs = ft.Tabs(
        selected_index=0,
        animation_duration=300,
        indicator_color="primary",
        label_color="primary",
        unselected_label_color="onSurfaceVariant",
        divider_color="transparent",
        tab_alignment=ft.TabAlignment.CENTER,
        tabs=[
            ft.Tab(text="Summary", content=summary_content),
            ft.Tab(text="Itinerary", content=itinerary_content),
            ft.Tab(text="Tips", content=tips_content),
        ],
        expand=True,
    )

    # Create delete button click handler
    def create_delete_handler(pid, callback, page_ref):
        """Create a closure for the delete button click handler."""
        def delete_handler(e):
            handle_delete_plan(e, pid, callback, page_ref)
        return delete_handler
    
    # -------------------------
    # Layout Assembly
    # -------------------------
    content = ft.SafeArea(
        content=ft.Container(
            width=APP_WIDTH,
            content=ft.Column(
                controls=[
                    # Header
                    ft.Container(
                        padding=ft.padding.only(left=8, top=8, right=8),
                        content=ft.Row(
                            [
                                ft.IconButton(icon=ft.Icons.ARROW_BACK, on_click=on_back),
                                ft.Text("Plan Summary", size=24, weight=ft.FontWeight.BOLD),
                                ft.IconButton(
                                    icon=ft.Icons.DELETE_OUTLINE,
                                    icon_color="error",
                                    tooltip="Delete Plan",
                                    on_click=create_delete_handler(plan_id, on_back, page)
                                ) if plan_id else ft.Container(),  # Only show delete button if plan_id is available
                            ],
                            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                        )
                    ),
                    
                    # Scrollable Images
                    images_row,
                    
                    # Tabs
                    tabs,
                ],
                spacing=0,
                expand=True,
            ),
            expand=True
        ),
        expand=True,
    )

    return content
