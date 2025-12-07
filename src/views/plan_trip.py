import flet as ft
import datetime
import threading
from services.ai_engine import AIEngine
from core.supabase_client import get_supabase_client

def build_plan_trip_view(page: ft.Page, on_back) -> tuple[ft.Control, list]:
    """
    View for planning a trip.
    
    Parameters
    ----------
    page:
        The Flet Page instance.
    on_back:
        Callback fired when the back button is clicked.
    
    Returns
    -------
    tuple:
        A tuple containing the content control and a list of overlay controls (date pickers).
    """
    
    # -------------------------
    # Controls & State
    # -------------------------

    # Duration DatePickers
    date_from = ft.DatePicker(
        first_date=datetime.datetime.now(),
        date_picker_entry_mode=ft.DatePickerEntryMode.CALENDAR_ONLY,
    )
    date_to = ft.DatePicker(
        first_date=datetime.datetime.now(),
        date_picker_entry_mode=ft.DatePickerEntryMode.CALENDAR_ONLY,
    )
    
    # Buttons for triggering DatePickers
    btn_date_from = ft.ElevatedButton(
        "From",
        icon=ft.Icons.CALENDAR_MONTH,
        expand=True
    )
    
    btn_date_to = ft.ElevatedButton(
        "To",
        icon=ft.Icons.CALENDAR_MONTH,
        expand=True
    )

    # Event Handlers for Date Logic
    def on_date_from_change(e):
        if date_from.value:
            btn_date_from.text = date_from.value.strftime("%b %d, %Y")
            btn_date_from.update()
            
    def on_date_to_change(e):
        if date_to.value:
            btn_date_to.text = date_to.value.strftime("%b %d, %Y")
            btn_date_to.update()
            
    date_from.on_change = on_date_from_change
    date_to.on_change = on_date_to_change

    # Helper to open date pickers
    def open_date_from(e):
        e.control.page.open(date_from)

    def open_date_to(e):
        e.control.page.open(date_to)
        
    btn_date_from.on_click = open_date_from
    btn_date_to.on_click = open_date_to

    # Budget Range
    budget_min = ft.TextField(label="Minimum", prefix_text="₱", keyboard_type=ft.KeyboardType.NUMBER, expand=True)
    budget_max = ft.TextField(label="Maximum", prefix_text="₱", keyboard_type=ft.KeyboardType.NUMBER, expand=True)

    # Destination
    destination_input = ft.TextField(hint_text="Camarines Sur", border_radius=10)

    # Travel Style
    travel_style_input = ft.Dropdown(
        options=[
            ft.dropdown.Option("Adventure"),
            ft.dropdown.Option("Luxury"),
            ft.dropdown.Option("Slow Travel"),
            ft.dropdown.Option("Backpacking"),
            ft.dropdown.Option("Cultural"),
            ft.dropdown.Option("Solo"),
            ft.dropdown.Option("Family"),
        ],
        border_radius=10,
        width=float("inf"),
    )

    # Time-base Preference
    time_preference_input = ft.Dropdown(
        options=[
            ft.dropdown.Option("Early Bird (Morning Person)"),
            ft.dropdown.Option("Night Owl"),
            ft.dropdown.Option("Flexible"),
            ft.dropdown.Option("Strict Schedule"),
            ft.dropdown.Option("Spontaneous"),
        ],
        border_radius=10,
        hint_text="Select preference",
        width=float("inf"),
    )

    # Dietary
    dietary_input = ft.Dropdown(
        options=[
            ft.dropdown.Option("None"),
            ft.dropdown.Option("Vegetarian"),
            ft.dropdown.Option("Vegan"),
            ft.dropdown.Option("Halal"),
            ft.dropdown.Option("Kosher"),
            ft.dropdown.Option("Gluten-Free"),
        ],
        border_radius=10,
        width=float("inf"),
    )

    def toggle_chip(e):
        # If the chip is selected, deselect all others
        if e.control.selected:
            for chip in activity_chips:
                if chip != e.control:
                    chip.selected = False
                    chip.update()
        e.control.update()
        
    # Activities Chips
    # Using a predefined list of activities
    trip_activities = [
         "Amusement Park", "Aquarium", "Art Gallery", "Bar", "Beach", 
         "Cafe", "Campground", "Casino", "Museum", "Night Club", "Park", 
         "Restaurant", "Shopping Mall", "Spa", "Stadium", 
         "Tourist Attraction", "Zoo", "Historical Site", "Hiking Area"
    ]
    
    activity_chips = []
    for activity in trip_activities:
        activity_chips.append(
            ft.Chip(
                label=ft.Text(activity),
                selected=False,
                selected_color=ft.Colors.BLUE_200,
                on_select=toggle_chip
            )
        )

    # -------------------------
    # Layout
    # -------------------------
    def handle_plan_trip(e):
        # Validate inputs
        if not destination_input.value or not destination_input.value.strip():
            page.snack_bar = ft.SnackBar(
                content=ft.Text("Please enter a destination"),
                bgcolor="error"
            )
            page.snack_bar.open = True
            page.update()
            return
        
        if not date_from.value or not date_to.value:
            page.snack_bar = ft.SnackBar(
                content=ft.Text("Please select both start and end dates"),
                bgcolor="error"
            )
            page.snack_bar.open = True
            page.update()
            return
        
        if date_to.value < date_from.value:
            page.snack_bar = ft.SnackBar(
                content=ft.Text("End date must be after start date"),
                bgcolor="error"
            )
            page.snack_bar.open = True
            page.update()
            return
        
        if not budget_min.value or not budget_max.value:
            page.snack_bar = ft.SnackBar(
                content=ft.Text("Please enter budget range"),
                bgcolor="error"
            )
            page.snack_bar.open = True
            page.update()
            return
        
        if not travel_style_input.value:
            page.snack_bar = ft.SnackBar(
                content=ft.Text("Please select a travel style"),
                bgcolor="error"
            )
            page.snack_bar.open = True
            page.update()
            return
        
        if not time_preference_input.value:
            page.snack_bar = ft.SnackBar(
                content=ft.Text("Please select a time preference"),
                bgcolor="error"
            )
            page.snack_bar.open = True
            page.update()
            return
        
        selected_activities = [chip.label.value for chip in activity_chips if chip.selected]
        if not selected_activities or len(selected_activities) == 0:
            page.snack_bar = ft.SnackBar(
                content=ft.Text("Please select an activity"),
                bgcolor="error"
            )
            page.snack_bar.open = True
            page.update()
            return
        
        # Get user ID
        supabase = get_supabase_client()
        if not supabase:
            page.snack_bar = ft.SnackBar(
                content=ft.Text("Error: Database connection not available"),
                bgcolor="error"
            )
            page.snack_bar.open = True
            page.update()
            return
        
        try:
            user_response = supabase.auth.get_user()
            if not user_response or not user_response.user:
                page.snack_bar = ft.SnackBar(
                    content=ft.Text("Please log in to create a plan"),
                    bgcolor="error"
                )
                page.snack_bar.open = True
                page.update()
                return
            user_id = user_response.user.id
        except Exception as ex:
            print(f"Error getting user: {ex}")
            page.snack_bar = ft.SnackBar(
                content=ft.Text("Please log in to create a plan"),
                bgcolor="error"
            )
            page.snack_bar.open = True
            page.update()
            return
        
        # Disable button and show loading
        e.control.disabled = True
        e.control.text = "Generating Plan..."
        page.update()
        
        # Gather trip details
        destination = destination_input.value.strip()
        start_date = date_from.value.date() if isinstance(date_from.value, datetime.datetime) else date_from.value
        end_date = date_to.value.date() if isinstance(date_to.value, datetime.datetime) else date_to.value
        budget_min_val = budget_min.value
        budget_max_val = budget_max.value
        travel_style = travel_style_input.value
        time_preference = time_preference_input.value
        activity = selected_activities[0]  # Only one activity selected
        dietary = dietary_input.value or "None"
        
        # Navigate to plans view immediately (plan will show as generating)
        on_back(None)
        
        # Generate plan in background thread
        def generate_plan_async():
            try:
                import asyncio
                
                # Create new event loop for this thread
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                
                try:
                    ai_engine = AIEngine()
                    plan = loop.run_until_complete(ai_engine.generate_plan(
                        user_id=user_id,
                        destination=destination,
                        date_from=start_date,
                        date_to=end_date,
                        budget_min=budget_min_val,
                        budget_max=budget_max_val,
                        travel_style=travel_style,
                        time_preference=time_preference,
                        activity=activity,
                        dietary=dietary,
                        country_code="PH"  # Default to Philippines, could be made configurable
                    ))
                    
                    # Cleanup
                    loop.run_until_complete(ai_engine.cleanup())
                    
                    if plan:
                        # Refresh plans view to show updated plan
                        refresh_plans_view()
                    else:
                        show_error("Failed to generate plan")
                finally:
                    loop.close()
                
            except Exception as ex:
                print(f"Error generating plan: {ex}")
                import traceback
                traceback.print_exc()
                show_error(str(ex))
        
        def refresh_plans_view():
            # Navigate to plans route to trigger a refresh
            # This will rebuild the view and fetch updated plans
            if page.route != "/plans":
                page.go("/plans")
            else:
                # If already on plans, trigger a route change event to refresh
                # We'll need to rebuild the view
                page.update()
        
        def show_error(error):
            # Reset button state
            e.control.disabled = False
            e.control.text = "Plan Trip"
            page.snack_bar = ft.SnackBar(
                content=ft.Text(f"Error generating plan: {str(error)}"),
                bgcolor="error"
            )
            page.snack_bar.open = True
            page.update()
        
        # Start generation in background thread
        thread = threading.Thread(target=generate_plan_async, daemon=True)
        thread.start()
    
    content = ft.SafeArea(
        ft.Container(
            padding=20,  # Added padding inside SafeArea
            content=ft.Column(
                [
                    # Header
                    ft.Row(
                        [
                            ft.IconButton(icon=ft.Icons.ARROW_BACK, on_click=on_back),
                            ft.Text("Plan Your Trip", size=24, weight=ft.FontWeight.BOLD),
                        ],
                        alignment=ft.MainAxisAlignment.START,
                    ),
                    
                    ft.Divider(),
                    
                    # Destination
                    ft.Text("Destination", weight=ft.FontWeight.BOLD),
                    destination_input,
                    
                    # Duration
                    ft.Text("Duration", weight=ft.FontWeight.BOLD),
                    ft.Row(
                        [
                            btn_date_from,
                            btn_date_to,
                        ]
                    ),
                    
                    # Budget Range
                    ft.Text("Budget Range", weight=ft.FontWeight.BOLD),
                    ft.Row([budget_min, budget_max]),
                    
                    # Travel Style
                    ft.Text("Travel Style", weight=ft.FontWeight.BOLD),
                    travel_style_input,

                    # Time-base Preference (New Field)
                    ft.Text("Time-base Preference", weight=ft.FontWeight.BOLD),
                    time_preference_input,
                    
                    # Activities
                    ft.Text("Activity (Select 1)", weight=ft.FontWeight.BOLD),
                    ft.Container(
                        content=ft.Row(
                            controls=activity_chips,
                            wrap=True,
                            spacing=10,
                            run_spacing=10,
                        ),
                        padding=10,
                    ),
                    
                    # Dietary
                    ft.Text("Dietary Requirements (Optional)", weight=ft.FontWeight.BOLD),
                    dietary_input,
                    
                    ft.Container(height=20), # Spacer
                    
                    # Plan Trip Button
                    ft.ElevatedButton(
                        "Plan Trip",
                        style=ft.ButtonStyle(
                            color="white",
                            bgcolor="blue",
                            padding=20,
                            shape=ft.RoundedRectangleBorder(radius=10),
                        ),
                        width=float("inf"), # Full width
                        on_click=handle_plan_trip,
                    )
                ],
                scroll=ft.ScrollMode.AUTO,
                spacing=15,
                expand=True, # Allow Column to expand and scroll
            ),
            expand=True, # Allow Container to expand
        ),
        expand=True, # Allow SafeArea to expand
    )
    
    # Return the content and the overlay controls (date pickers)
    return content, [date_from, date_to]
