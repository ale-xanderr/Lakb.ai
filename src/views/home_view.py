import flet as ft
from .components.nav_bar import create_navigation_bar
from .components.destination_card import build_destination_page
from .components.search_bar import SearchBar, build_filter_sheet, CategoryTabs
from .components.status_dialog import create_error_message, create_warning_message, create_info_message
from .components.feature_card import build_feature_card
from .components.loading_indicator import create_loading_indicator
from .settings_view import build_settings_content
from .favorites_view import build_favorites_view
from .plans_view import build_plans_view
from .plan_trip import build_plan_trip_view
from .components.floating_action_button import create_floating_action_button
from core.config import configure_page
from state import (
    ServiceManager, 
    PlacesStateController, 
    NavigationController,
    FavoritesStateController
)

def main(page: ft.Page):
    """
    Main entry point for the Home View.
    Sets up the page configuration, initializes state managers, and builds the UI.
    
    Args:
        page: The Flet page instance.
    """
    # 1. Device / window configuration (centralized)
    configure_page(page, title="Travel App Home")

    # --- Theme Configuration ---
    # Use centralized theme configuration
    from core.theme import configure_theme
    configure_theme(page)


    # --- Initialize State Managers ---
    service_manager = ServiceManager()
    if not service_manager._page:
        service_manager.initialize(page)
    
    places_state_controller = PlacesStateController(page)
    navigation_controller = NavigationController(page)
    favorites_state_controller = FavoritesStateController(page)
    
    # Preserve auth_state_controller if it exists (from login_view), otherwise create new one
    from state import AuthStateController
    auth_state_controller = getattr(page, "_auth_state_controller", None)
    if not auth_state_controller:
        auth_state_controller = AuthStateController(page)
        page._auth_state_controller = auth_state_controller
    
    # Store controllers on page for access from other views
    page._places_state_controller = places_state_controller
    page._navigation_controller = navigation_controller
    page._favorites_state_controller = favorites_state_controller
    page._service_manager = service_manager
    
    # Get services from service manager
    api_service = service_manager.api_service
    favorites_service = service_manager.favorites_service
    
    # Reference to the column that holds the cards, so we can update it
    places_column_ref = ft.Ref[ft.Column]()
    load_more_btn_ref = ft.Ref[ft.Container]()
    section_title_ref = ft.Ref[ft.Text]()
    search_bar_ref = ft.Ref[ft.SearchBar]()
    error_dialog_ref = ft.Ref[ft.Container]()
    
    # Set UI refs in state controller
    places_state_controller.set_ui_refs(
        places_column_ref=places_column_ref,
        load_more_btn_ref=load_more_btn_ref,
        section_title_ref=section_title_ref,
        search_bar_ref=search_bar_ref,
        error_dialog_ref=error_dialog_ref
    )

    # --- Bottom navigation handler ---
    def handle_nav_change(e: ft.ControlEvent):
        idx = e.control.selected_index

        # 0 = Home, 1 = Favorites, 2 = Plans, 3 = Profile/Settings
        navigation_controller.current_nav_index = idx
        if idx == 0:
            # If already on home, reset to device location
            if page.route == "/":
                reset_to_device_location()
            else:
                navigation_controller.navigate_home()
        elif idx == 1:
            navigation_controller.navigate_favorites()
        elif idx == 2:
            navigation_controller.navigate_plans()
        elif idx == 3:
            navigation_controller.navigate_settings()
        else:
            # For now, keep the current route for unimplemented tabs
            page.go(page.route or "/")



    def build_search_bar(on_filter_click):
        # Create SearchBar
        # We need to populate controls (suggestions) from history initially
        history_controls = [
            ft.ListTile(
                title=ft.Text(h), 
                on_click=lambda e, val=h: close_search(val),
                data=h
            ) 
            for h in reversed(places_state_controller.recent_searches)
        ]

        return ft.SearchBar(
            ref=search_bar_ref,
            bar_hint_text="Try 'Popular in Nabua' ",
            view_hint_text="Search for a place...",
            view_leading=ft.IconButton(icon=ft.Icons.ARROW_BACK, on_click=lambda _: search_bar_ref.current.close_view()),
            bar_leading=ft.Icon(ft.Icons.SEARCH, color="#B0B0B0"),
            bar_trailing=[
                ft.IconButton(
                    icon=ft.Icons.TUNE,
                    icon_color="onBackground",
                    on_click=on_filter_click
                )
            ],
            controls=history_controls,
            on_submit=handle_search,
            on_change=handle_text_change,
            on_tap=lambda _: search_bar_ref.current.open_view() if search_bar_ref.current else None,
            full_screen=False,
            # Style to match previous design (approx)
            bar_bgcolor="surface",
            bar_overlay_color=ft.Colors.with_opacity(0.1, "primary"),
            # bar_shadow is not a valid property for SearchBar, removing it.
            # Default elevation handles shadow.
        )

    def close_search(value):
        """Helper to close search view and trigger search when clicking a history item"""
        if search_bar_ref.current:
            # Set value properly
            search_bar_ref.current.value = value
            # Close view with the value to ensure it's retained
            search_bar_ref.current.close_view(value)
            # Update the control
            search_bar_ref.current.update()
            
            # Trigger search logic manually
            class FakeEvent:
                control = search_bar_ref.current
            handle_search(FakeEvent())

    def handle_text_change(e):
        """Handle text changes to detect when search is cleared"""
        raw_query = e.control.value
        if not raw_query or raw_query.strip() == "":
            # User cleared the search, reset to popular places
            reset_to_device_location()
    
    def handle_search(e):
        raw_query = e.control.value
        
        # Auto-close the search view after submitting
        if search_bar_ref.current:
            search_bar_ref.current.close_view(raw_query)
            search_bar_ref.current.update()
        
        # 0. Update History
        if raw_query:
            places_state_controller.add_recent_search(raw_query)
            
            # Update search bar suggestion controls with list items
            if search_bar_ref.current:
                search_bar_ref.current.controls = [
                    ft.ListTile(
                        title=ft.Text(h), 
                        on_click=lambda e, val=h: close_search(val),
                        data=h
                    ) 
                    for h in reversed(places_state_controller.recent_searches)
                ]
                # Update the control on the page
                if search_bar_ref.current.page:
                    search_bar_ref.current.update()

        if not raw_query:
            reset_to_device_location()
            return

        # 1. Try to geocode the full query first (e.g. "Legazpi City")
        print(f"DEBUG: Geocoding query: {raw_query}")
        geo_result = api_service.geocode(raw_query)
        
        if geo_result:
            print(f"DEBUG: Found location: {geo_result}")
            places_state_controller.location = f"{geo_result['lat']},{geo_result['lng']}"
            places_state_controller.city_name = geo_result['city']
            # Clear query, use location bias
            load_places(query="", location=places_state_controller.location, update_ui=True)
            return

        # 2. If full query failed, check for " in " pattern (e.g. "Gym in Nabua")
        if " in " in raw_query.lower():
            parts = raw_query.lower().split(" in ")
            # Take the last part as potential location (simplistic but often works)
            potential_location = parts[-1]
            keyword = " in ".join(parts[:-1]) # Reconstruct left part
            
            print(f"DEBUG: Trying to geocode location part: {potential_location}")
            geo_result = api_service.geocode(potential_location)
            
            if geo_result:
                print(f"DEBUG: Found location from split: {geo_result}")
                places_state_controller.location = f"{geo_result['lat']},{geo_result['lng']}"
                places_state_controller.city_name = geo_result['city']
                
                # If keyword is generic like "popular" or "places", ignore it
                if keyword.strip() in ["popular", "places", "popular places"]:
                    load_places(query="", location=places_state_controller.location, update_ui=True)
                else:
                    # Search for the keyword with the new location bias
                    load_places(query=keyword, location=places_state_controller.location, update_ui=True)
                return

        # 3. Fallback: Keyword search
        # Clear type when searching explicitly
        load_places(query=raw_query, place_type=None)

    def load_places(load_more=False, query=None, place_type=None, location=None, update_ui=True):
        """
        Fetch places from API and update the UI.
        """
        # If not loading more, reset state
        if not load_more:
            places_state_controller.data = []
            places_state_controller.next_page_token = None
            if query is not None:
                places_state_controller.query = query
            if place_type is not None:
                places_state_controller.place_type = place_type
            if location is not None:
                places_state_controller.location = location
            
            # Show loading indicator immediately when starting a new search/filter
            if update_ui and places_column_ref.current and places_column_ref.current.page:
                try:
                     places_column_ref.current.controls.clear()
                     places_column_ref.current.controls.append(
                        create_loading_indicator("Searching for places...")
                     )
                     places_column_ref.current.update()
                except Exception:
                    pass # Ignore update errors if view is changing
        
        # Prepare args
        kwargs = {}
        if places_state_controller.query:
            kwargs["query"] = places_state_controller.query
        
        # Only use type if no query, or if API supports both (it does)
        if places_state_controller.place_type:
            kwargs["place_type"] = places_state_controller.place_type
        
        if places_state_controller.location:
            kwargs["location"] = places_state_controller.location
            
        if load_more and places_state_controller.next_page_token:
            kwargs["page_token"] = places_state_controller.next_page_token
        elif load_more and not places_state_controller.next_page_token:
            return # No more pages

        # Fetch data (Sync call)
        print("DEBUG: Calling api_service.search_places...")
        result = api_service.search_places(**kwargs)
        
        # Hide error dialog initially
        if error_dialog_ref.current:
            error_dialog_ref.current.visible = False
        
        if "results" in result:
            new_places = result["results"]
            print(f"DEBUG: load_places got {len(new_places)} results")
            # Filter out places without photos if desired, or just add them
            for p in new_places:
                p["is_favorite"] = favorites_service.is_favorite(p.get("place_id"))
            
            places_state_controller.data = places_state_controller.data + new_places
            places_state_controller.next_page_token = result.get("next_page_token")
            
            # Check if we have no results after loading and show appropriate message
            if not load_more and len(new_places) == 0 and error_dialog_ref.current:
                # Determine what message to show based on what was searched
                if places_state_controller.query:
                    # User searched for something specific but got no results
                    msg = f"No places found for '{places_state_controller.query}'. Please check your spelling or try a different search term."
                    error_dialog_ref.current.content = create_warning_message(msg)
                    error_dialog_ref.current.visible = True
                    if error_dialog_ref.current.page:
                        try:
                            error_dialog_ref.current.update()
                        except Exception:
                            pass
                elif places_state_controller.place_type:
                    # Filtered by category but got no results
                    location_text = f" in {places_state_controller.city_name}" if places_state_controller.city_name else ""
                    msg = f"No {places_state_controller.place_type}s found{location_text}. Try a different category or location."
                    error_dialog_ref.current.content = create_info_message(msg)
                    error_dialog_ref.current.visible = True
                    if error_dialog_ref.current.page:
                        try:
                            error_dialog_ref.current.update()
                        except Exception:
                            pass
            
            # Update UI
            if update_ui:
                print("DEBUG: Updating UI in load_places")
                render_places()
        else:
            # Handle error or no results
            print(f"API Error or No Results: {result}")
            
            # Show error dialog if there's an error message
            error_msg = result.get("error", "")
            if error_msg and error_dialog_ref.current:
                # Create and show error dialog
                error_dialog_ref.current.content = create_error_message(error_msg)
                error_dialog_ref.current.visible = True
                if error_dialog_ref.current.page:
                    try:
                        error_dialog_ref.current.update()
                    except Exception:
                        pass
            
            if not load_more:
                 places_state_controller.data = []
                 if update_ui:
                    render_places()

    def render_places():
        # Update Title
        if section_title_ref.current:
            title_text = places_state_controller.get_section_title()
            
            # Check if control is mounted before update
            if section_title_ref.current and section_title_ref.current.page:
                 section_title_ref.current.value = title_text
                 try:
                     section_title_ref.current.update()
                 except Exception:
                     pass

        if places_column_ref.current and places_column_ref.current.page:
            places_column_ref.current.controls.clear()
            if len(places_state_controller.data) > 0:
                # Refresh favorite status before rendering
                for place in places_state_controller.data:
                    place["is_favorite"] = favorites_service.is_favorite(place.get("place_id"))
                
                # Render place cards
                for place in places_state_controller.data:
                    card = build_feature_card(
                        data=place,
                        page=page,
                        on_card_click=handle_card_click_home,
                        mode="full",
                        api_service=api_service
                    )
                    places_column_ref.current.controls.append(card)
            # If no data and not showing error, keep the loading indicator (it's already there)
            # The loading indicator will be replaced when data arrives or error shows
            
            try:
                places_column_ref.current.update()
            except Exception:
                pass
            
        if load_more_btn_ref.current and load_more_btn_ref.current.page:
            load_more_btn_ref.current.visible = bool(places_state_controller.next_page_token)
            try:
                load_more_btn_ref.current.update()
            except Exception:
                pass

    def reset_to_device_location():
        """
        Reset view to user's device location.
        """
        print("DEBUG: Resetting to device location")
        places_state_controller.reset_to_device_location()
        load_places(query="", update_ui=True)

    # --- Geolocation Integration ---
    def on_location_update(lat, lng, city):
        print(f"DEBUG: Home received location: {lat}, {lng}, {city}")
        loc_str = f"{lat},{lng}"
        
        # Store as device location (baseline)
        places_state_controller.device_location = loc_str
        places_state_controller.device_city = city
        
        # If we haven't set a location yet, or if we are in "initial load" mode, use this
        if not places_state_controller.location:
            places_state_controller.location = loc_str
            places_state_controller.city_name = city
            # Initial load with location bias
            load_places(query="", location=loc_str, update_ui=True)

    # Get or create geolocation service
    geolocation_service = service_manager.geolocation_service
    if geolocation_service is None:
        geolocation_service = service_manager.create_geolocation_service(on_location_update=on_location_update)
    else:
        # Update callback if service already exists
        geolocation_service.on_location_update = on_location_update

    def dummy_click(e):
        pass

    # --- UI Components ---

    def build_header():
        return ft.Column(
            spacing=0,
            controls=[
                ft.Text("Start Now", size=28, weight=ft.FontWeight.BOLD, color="onBackground"),
                ft.Text("Exploring World", size=38, font_family="Courgette", color="primary", height=1.2),
            ]
        )



    # State for category tabs
    selected_category = {"value": None}

    # Removed local build_more_categories_sheet as we use the reusable one now

    def build_category_tabs():
        return CategoryTabs(page, load_more_category, selected_category=selected_category["value"])

    def load_more_category(category):
             if category:
                selected_category["value"] = category
                places_state_controller.place_type = category
                load_places(place_type=category, query=None)
                # Tabs update themselves via internal logic + callback updates state here
    
    def load_initial_places():
        """Load places asynchronously after UI is rendered"""
        import time
        # Small delay to ensure UI is fully rendered
        time.sleep(0.05)
        
        # Check if we already have data (from previous navigation)
        if not places_state_controller.data:
            if places_state_controller.location:
                # Location already available, load with location bias
                load_places(query="", location=places_state_controller.location, update_ui=True)
            else:
                # Load default places (will be updated when location arrives)
                load_places(update_ui=True)

    # Helper function for card click
    def handle_card_click_home(e, data):
        """Handle card click in home view"""
        title = data.get("name") or data.get("title", "Unknown")
        address = data.get("formatted_address") or data.get("address", "")
        place_id = data.get("place_id") or data.get("id")
        
        # Get image URL
        image_url = data.get("image_url")
        if not image_url and "photos" in data and len(data["photos"]) > 0:
            photo_ref = data["photos"][0].get("photo_reference")
            if photo_ref:
                image_url = api_service.get_photo_url(photo_ref)
        
        adapted_data = {
            "title": title,
            "address": address,
            "image_url": image_url,
            "description": "Description not available from Search API",
            "price": "N/A",
            "rating": data.get("rating", 0),
            "id": place_id,
            "is_favorite": data.get("is_favorite", False)
        }
        navigation_controller.navigate_destination(adapted_data)

    def build_home_content() -> ft.Control:
        """Build the main scrollable home screen layout."""
        # place_cards = [build_feature_card(item) for item in mock_places_data] # Removed

        # Category tabs container (initially hidden)
        tabs_container = ft.Container(
            padding=ft.padding.only(left=24),
            margin=ft.margin.symmetric(vertical=10), # Add margin when visible
            content=build_category_tabs(),
            visible=False, # Hidden by default
            animate_opacity=300, 
        )

        def toggle_filter(e):
            if tabs_container:
                tabs_container.visible = not tabs_container.visible
                tabs_container.update()
                page.update()  # Update page to reflect visibility change
            
        # Refresh favorite status for all items (in case changed in Favorites view)
        # Use the shared service instance which caches data
        for p in places_state_controller.data:
            p["is_favorite"] = favorites_service.is_favorite(p.get("place_id"))
        
        # Trigger async loading if we don't have data yet
        # This happens after the UI structure is built and rendered
        if not places_state_controller.data:
            # Schedule async load
            import threading
            threading.Timer(0.1, load_initial_places).start()

        # Calculate initial title based on current state
        initial_title = places_state_controller.get_section_title()

        content_scroll = ft.Column(
            scroll=ft.ScrollMode.HIDDEN,
            expand=True,
            spacing=0,
            controls=[
                ft.Container(height=10),
                ft.Container(padding=ft.padding.symmetric(horizontal=24), content=build_header()),
                ft.Container(height=25),
                ft.Container(padding=ft.padding.symmetric(horizontal=24), content=build_search_bar(on_filter_click=toggle_filter)),
                ft.Container(height=20), # Fixed spacer
                tabs_container,
                # Removed extra spacers to keep layout tight when tabs are hidden
                ft.Container(
                    padding=ft.padding.symmetric(horizontal=24),
                    content=ft.Text(initial_title, ref=section_title_ref, size=24, weight=ft.FontWeight.BOLD, color="onBackground"),
                ),
                ft.Container(height=15),
                # Error/Status Dialog Container (shown below title when there's an error)
                ft.Container(
                    ref=error_dialog_ref,
                    padding=ft.padding.symmetric(horizontal=24),
                    visible=False,
                ),
                # Inject generated cards here
                ft.Container(
                    padding=ft.padding.symmetric(horizontal=24),
                    content=ft.Column(
                        ref=places_column_ref,
                        spacing=0, 
                        controls=[
                            build_feature_card(
                                data=p,
                                page=page,
                                on_card_click=handle_card_click_home,
                                mode="full",
                                api_service=api_service
                            ) for p in places_state_controller.data
                        ] if places_state_controller.data else [create_loading_indicator("Finding amazing places for you...")] # Show loading indicator initially
                    ),
                ),
                ft.Container(
                    ref=load_more_btn_ref,
                    padding=ft.padding.all(24),
                    alignment=ft.alignment.center,
                    visible=bool(places_state_controller.next_page_token),
                    content=ft.ElevatedButton(
                        "Load More",
                        on_click=lambda e: load_places(load_more=True),
                        bgcolor="primary",
                        color="white"
                    )
                ),
                ft.Container(height=30),
            ],
        )

        return ft.SafeArea(
            expand=True,
            content=ft.Column(
                expand=True,
                spacing=0,
                controls=[
                    content_scroll,
                ],
            ),
        )

    # --- Simple routing using Page.views ---
    def route_change(e: ft.RouteChangeEvent):
        # Clean up any existing views before creating new ones
        page.views.clear()

        if page.route == "/destination" and navigation_controller.selected_place is not None:
            # Determine back destination based on current nav index
            def on_back(e):
                navigation_controller.navigate_back()

            page.views.append(
                ft.View(
                    "/destination",
                    controls=[build_destination_page(page, navigation_controller.selected_place, on_back=on_back)],
                    padding=0,
                    bgcolor="background",
                    navigation_bar=create_navigation_bar(
                        selected_index=navigation_controller.current_nav_index,
                        on_change=handle_nav_change,
                    ),
                )
            )
        elif page.route == "/settings":
            page.views.append(
                ft.View(
                    "/settings",
                    controls=[build_settings_content(page)],
                    padding=0,
                    bgcolor="background",
                    navigation_bar=create_navigation_bar(
                        selected_index=3,
                        on_change=handle_nav_change,
                    ),
                )
            )
        elif page.route == "/favorites":
            # Force refresh favorites service before building view to ensure latest data
            try:
                favorites_service.get_favorites(force_refresh=True)
                print("DEBUG Home: Refreshed favorites before showing favorites view")
            except Exception as e:
                print(f"Warning: Could not refresh favorites: {e}")
            
            # Create a wrapper dict for selected_place compatibility
            selected_place_wrapper = {"value": navigation_controller.selected_place}
            
            page.views.append(
                ft.View(
                    "/favorites",
                    controls=[build_favorites_view(page, selected_place_wrapper, favorites_service=favorites_service)],
                    padding=0,
                    bgcolor="background",
                    navigation_bar=create_navigation_bar(
                        selected_index=1,
                        on_change=handle_nav_change,
                    ),
                )
            )
        elif page.route == "/plans":
            # Store refresh function in a list so it persists across rebuilds
            refresh_funcs = []
            
            # Handler for when a plan card is clicked
            def on_open_plan(e, plan_data):
                # Navigate to plan summary view
                from .components.plan_summary import build_plan_summary_view
                
                # Don't allow opening plans that are still generating
                if plan_data.get("is_generating", False):
                    page.snack_bar = ft.SnackBar(
                        content=ft.Text("Plan is still being generated. Please wait..."),
                        bgcolor="info"
                    )
                    page.snack_bar.open = True
                    page.update()
                    return
                
                # Extract trip data from plan_data structure
                # plan_data has: id, title, description, image_url, is_generating, data
                # The 'data' field contains the actual trip information
                trip_data = plan_data.get("data", {}) if plan_data else {}
                plan_id = plan_data.get("id") if plan_data else None
                
                # Get the refresh function (use the latest one if available)
                refresh_plans_func = refresh_funcs[0] if refresh_funcs else None
                
                # Create on_back that includes refresh
                def on_back_with_refresh(e):
                    # Pop the view
                    if len(page.views) > 1:
                        page.views.pop()
                        # Refresh plans after going back (in case a plan was deleted)
                        if refresh_funcs:
                            refresh_funcs[0]()
                        page.update()
                
                page.views.append(
                    ft.View(
                        "/plan_summary",
                        controls=[build_plan_summary_view(on_back=on_back_with_refresh, trip_data=trip_data, page=page, plan_id=plan_id, on_delete_callback=refresh_plans_func)],
                        padding=0,
                        bgcolor="background",
                        # No navigation bar for plan summary
                    )
                )
                page.update()
            
            # Build plans view with the on_open_plan handler
            plans_content, refresh_plans = build_plans_view(page, on_open_plan=on_open_plan)
            # Store refresh function
            refresh_funcs.clear()
            refresh_funcs.append(refresh_plans)
            
            # Handler for floating action button click
            def on_new_plan(e):
                # Check if user is a guest
                auth_state_controller = getattr(page, "_auth_state_controller", None)
                if auth_state_controller and auth_state_controller.is_guest:
                    # Guest users cannot create plans - show dialog
                    show_guest_account_dialog()
                    return
                navigation_controller.navigate_to("/plan_trip")
            
            def show_guest_account_dialog():
                """Show dialog prompting guest user to create account for full functionality."""
                def go_to_signup(e):
                    """Handle sign up button click - navigate to login view."""
                    # Navigate to login view for registration/login flow
                    page.close(dialog)
                    
                    # Clear any view stack or route handlers
                    try:
                        if hasattr(page, 'views') and isinstance(page.views, list):
                            page.views.clear()
                    except Exception:
                        pass

                    try:
                        if hasattr(page, 'on_route_change'):
                            page.on_route_change = None
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
                        "To create trip plans and access all features, please create an account.",
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
            
            # Create floating action button
            fab = create_floating_action_button(on_click=on_new_plan)
            
            page.views.append(
                ft.View(
                    "/plans",
                    controls=[plans_content],
                    padding=0,
                    bgcolor="background",
                    navigation_bar=create_navigation_bar(
                        selected_index=2,
                        on_change=handle_nav_change,
                    ),
                    floating_action_button=fab,
                )
            )
        elif page.route == "/plan_trip":
            def on_back_from_trip(e):
                navigation_controller.navigate_plans()
            
            content, overlay_controls = build_plan_trip_view(page, on_back=on_back_from_trip)
            
            # Add overlay controls (date pickers) to page
            for control in overlay_controls:
                page.overlay.append(control)
            
            page.views.append(
                ft.View(
                    "/plan_trip",
                    controls=[content],
                    padding=0,
                    bgcolor="background",
                    # No navigation bar for plan trip form
                )
            )
        elif page.route == "/profile_edit":
            from .profile_view import build_profile_edit_view
            page.views.append(
                ft.View(
                    "/profile_edit",
                    controls=[build_profile_edit_view(page)],
                    padding=0,
                    bgcolor="background",
                    # No navigation bar for edit screen
                )
            )
        else:
            # Default home route
            page.views.append(
                ft.View(
                    "/",
                    controls=[build_home_content()],
                    padding=0,
                    bgcolor="background",
                    navigation_bar=create_navigation_bar(
                        selected_index=0,
                        on_change=handle_nav_change,
                    ),
                )
            )
            # Request location on home load if not already set
            # This ensures we try to get location when the user lands on home
            # Don't block - request asynchronously so app loads immediately
            if not places_state_controller.location:
                # Request location in background - don't wait for it
                import threading
                def request_location_async():
                    import time
                    time.sleep(0.1)  # Small delay to let UI render first
                    geolocation_service.request_location()
                
                thread = threading.Thread(target=request_location_async, daemon=True)
                thread.start()

        page.update()

    page.on_route_change = route_change
    
    # Robust Initial Routing:
    # 1. Normalize route: redirect auth/splash routes to home ("/")
    if page.route in ["/login", "/splash", "/oauth_callback"] or not page.route:
        page.route = "/"
        
    # 2. Manually trigger route_change to ensure UI builds immediately
    # This prevents "blank page" issues where page.go() might skip the handler
    # if the route hasn't effectively changed (e.g. "/" -> "/")
    route_change(None)
    
    # 3. Sync with Flet internal state (optional but good practice)
    # page.go(page.route) 


if __name__ == "__main__":
    ft.app(target=main)