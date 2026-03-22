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
    profile_service = service_manager.profile_service
    
    # Reference to the column that holds the cards, so we can update it
    places_column_ref = ft.Ref[ft.Column]()
    load_more_btn_ref = ft.Ref[ft.Container]()
    section_title_ref = ft.Ref[ft.Text]()
    search_bar_ref = ft.Ref[ft.SearchBar]()
    error_dialog_ref = ft.Ref[ft.Container]()
    header_container_ref = ft.Ref[ft.Container]()
    
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

        # 0 = Home, 1 = Plans, 2 = Favorites
        navigation_controller.current_nav_index = idx
        if idx == 0:
            # If already on home, reset to device location
            if page.route == "/":
                reset_to_device_location()
            else:
                navigation_controller.navigate_home()
        elif idx == 1:
            navigation_controller.navigate_plans()
        elif idx == 2:
            navigation_controller.navigate_favorites()
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
            view_elevation=0,
            divider_color=ft.Colors.TRANSPARENT,
            bar_shadow_color=ft.Colors.TRANSPARENT,
            bar_border_side=ft.BorderSide(width=0.5, color=ft.Colors.GREY_400),
            bar_shape=ft.RoundedRectangleBorder(radius=8),
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

        def _fetch_and_update():
            # Fetch data (Sync call in background)
            print("DEBUG: Calling api_service.search_places in background...")
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
                        
        # Start the background thread
        import threading
        threading.Thread(target=_fetch_and_update, daemon=True).start()

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
            
            controls_to_animate = []
            
            if len(places_state_controller.data) > 0:
                # Refresh favorite status before rendering
                for place in places_state_controller.data:
                    place["is_favorite"] = favorites_service.is_favorite(place.get("place_id"))
                
                # Render place cards
                for i, place in enumerate(places_state_controller.data):
                    card = build_feature_card(
                        data=place,
                        page=page,
                        on_card_click=handle_card_click_home,
                        mode="full",
                        api_service=api_service
                    )
                    
                    # Wrap in animation container for staggered entrance
                    # Start with opacity 0 and slightly shifted down
                    anim_card = ft.Container(
                        content=card,
                        opacity=0,
                        offset=ft.Offset(0, 0.2), # Start lower (20% of height)
                        animate_opacity=400,
                        animate_offset=ft.Animation(400, ft.AnimationCurve.DECELERATE),
                    )
                    
                    places_column_ref.current.controls.append(anim_card)
                    controls_to_animate.append(anim_card)
            
            # If no data and not showing error, keep the loading indicator (it's already there)
            # The loading indicator will be replaced when data arrives or error shows
            
            try:
                places_column_ref.current.update()
                
                # Trigger staggered animation
                if controls_to_animate:
                    import threading
                    def animate_items():
                        import time
                        # Initial delay before starting sequence
                        time.sleep(0.1)
                        for control in controls_to_animate:
                            # Verify page existence to avoid errors if user navigated away
                            if not control.page:
                                break
                            
                            # Update properties to final state
                            control.opacity = 1
                            control.offset = ft.Offset(0, 0)
                            try:
                                control.update()
                            except:
                                break
                            
                            # Stagger delay
                            time.sleep(0.08) 
                            
                    threading.Thread(target=animate_items, daemon=True).start()
                    
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
        # Setup initial UI controls with placeholder/default values
        name_text = ft.Text("Hello, Traveler", size=28, weight=ft.FontWeight.BOLD, color="onBackground", max_lines=1, overflow=ft.TextOverflow.ELLIPSIS)
        avatar_content = ft.Text("T", size=20, weight=ft.FontWeight.BOLD, color="white")
        avatar = ft.CircleAvatar(
            radius=24,
            bgcolor="primary",
            foreground_image_src=None,
            content=avatar_content
        )

        def fetch_latest_profile(u_id, current_name, current_avatar):
            try:
                profile_data = profile_service.get_user_profile(u_id)
                if profile_data:
                    # Cache in session to prevent flashing on returning to Home View
                    page.session.set(f"profile_{u_id}", profile_data)
                    new_name = profile_data.get("first_name")
                    new_avatar = profile_data.get("avatar_url")
                    
                    changed = False
                    if new_name and new_name != current_name:
                         name_text.value = f"Hello, {new_name}"
                         avatar_content.value = new_name[0].upper()
                         changed = True
                    if new_avatar and new_avatar != current_avatar:
                         avatar.foreground_image_src = new_avatar
                         avatar.content = None
                         changed = True
                         
                    if changed and name_text.page:
                         try:
                             name_text.update()
                             avatar.update()
                         except Exception:
                             pass
            except Exception:
                pass

        user_name = "Traveler"
        avatar_src = None
        initial = "T"
        user_id = None
        
        if auth_state_controller.is_authenticated:
            user = auth_state_controller.user
            email = ""
            meta = {}
            
            if hasattr(user, 'user') and user.user:
                 user_obj = user.user
                 email = getattr(user_obj, 'email', "")
                 user_id = getattr(user_obj, 'id', None)
                 meta = getattr(user_obj, 'user_metadata', {}) or {}
            elif isinstance(user, dict):
                 email = user.get("email", "")
                 user_id = user.get("id")
                 meta = user.get("user_metadata", {}) or {}
            else:
                 email = getattr(user, 'email', "")
                 user_id = getattr(user, 'id', None)
                 meta = getattr(user, 'user_metadata', {}) or {}
                 
            user_name = meta.get("first_name") or meta.get("full_name") or (email.split("@")[0] if email else "Traveler")
            avatar_src = meta.get("avatar_url")
            
            if user_id:
                # Synchronously check cached profile to prevent "Hello, Test" flash
                cached = page.session.get(f"profile_{user_id}")
                if cached:
                    if cached.get("first_name"):
                        user_name = cached.get("first_name")
                    if cached.get("avatar_url"):
                        avatar_src = cached.get("avatar_url")
            
            if user_name:
                 initial = user_name[0].upper()
                 name_text.value = f"Hello, {user_name}"
                 if avatar_src:
                     avatar.foreground_image_src = avatar_src
                     avatar.content = None
                 else:
                     avatar_content.value = initial
                     avatar.content = avatar_content
                     
            if user_id:
                import threading
                threading.Thread(target=fetch_latest_profile, args=(user_id, user_name, avatar_src), daemon=True).start()
                
        elif auth_state_controller.is_guest:
             name_text.value = "Hello, Guest"
             avatar_content.value = "G"
             avatar.content = avatar_content
             
        # Return the built row
        return ft.Row(
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            controls=[
                ft.Column(
                    spacing=0,
                    expand=True,
                    controls=[
                        name_text,
                        ft.Text("Welcome to Lakb.ai", size=14, color=ft.Colors.with_opacity(0.7, "onBackground"), italic=True),
                    ]
                ),
                ft.Container(
                    on_click=lambda _: navigation_controller.navigate_settings(),
                    content=avatar
                )
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
            margin=ft.margin.only(bottom=12), # Add margin when visible
            content=build_category_tabs(),
            visible=False, # Hidden by default
            animate_opacity=300, 
        )

        def toggle_filter(e):
            if tabs_container:
                tabs_container.visible = not tabs_container.visible
                tabs_container.update()
                page.update()  # Update page to reflect visibility change
            
        # Refresh favorite status for all items asynchronously to prevent UI block
        def refresh_favorites_async():
            if not places_state_controller.data:
                return
            changed = False
            for p in places_state_controller.data:
                old_state = p.get("is_favorite", False)
                new_state = favorites_service.is_favorite(p.get("place_id"))
                if old_state != new_state:
                    p["is_favorite"] = new_state
                    changed = True
            if changed and places_column_ref.current:
                # Need to update UI. render_places will handle it properly 
                try:
                    render_places()
                except Exception:
                    pass
                
        if places_state_controller.data:
            import threading
            threading.Thread(target=refresh_favorites_async, daemon=True).start()
        
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
                # Fixed spacer
                ft.Container(height=12),

                # Container for Header
                ft.Container(ref=header_container_ref, padding=ft.padding.symmetric(horizontal=24), content=build_header()),

                # Fixed spacer
                ft.Container(height=12),

                # Container for Search Bar
                ft.Container(padding=ft.padding.symmetric(horizontal=24), content=build_search_bar(on_filter_click=toggle_filter)),

                # Fixed spacer
                ft.Container(height=12),

                # Filter tabs container
                tabs_container,

                # Removed extra spacers to keep layout tight when tabs are hidden
                ft.Container(
                    padding=ft.padding.symmetric(horizontal=24),
                    content=ft.Text(initial_title, ref=section_title_ref, size=24, weight=ft.FontWeight.BOLD, color="onBackground"),
                ),

                # FIxed Container
                ft.Container(height=12),

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
                ft.Container(height=32),
            ],
        )

        return ft.Container(
            expand=True,
            gradient=ft.LinearGradient(
                begin=ft.alignment.top_center,
                end=ft.alignment.bottom_center,
                colors=[
                    ft.Colors.with_opacity(0.15, ft.Colors.GREEN),
                    ft.Colors.with_opacity(0.0, ft.Colors.GREEN),
                ],
            ),
            content=ft.SafeArea(
                expand=True,
                content=ft.Column(
                    expand=True,
                    spacing=0,
                    controls=[
                        content_scroll,
                    ],
                ),
            )
        )

    # --- Helper Layout Function ---
    def apply_gradient_background(content: ft.Control) -> ft.Container:
        return ft.Container(
            expand=True,
            gradient=ft.LinearGradient(
                begin=ft.alignment.top_center,
                end=ft.alignment.bottom_center,
                colors=[
                    ft.Colors.with_opacity(0.15, ft.Colors.GREEN),
                    ft.Colors.with_opacity(0.0, ft.Colors.GREEN),
                ],
            ),
            content=content
        )

    # --- Persistent UI Shell ---
    # Define these ONCE so they persist across tab changes
    
    # 1. Navigation Bar
    nav_bar = create_navigation_bar(
        selected_index=0,
        on_change=handle_nav_change,
    )

    # 2. Body Content Switcher (Animated)
    body_switcher = ft.AnimatedSwitcher(
        transition=ft.AnimatedSwitcherTransition.FADE,
        duration=300,
        reverse_duration=150,
        switch_in_curve=ft.AnimationCurve.EASE_OUT,
        switch_out_curve=ft.AnimationCurve.EASE_IN,
        content=ft.Container(expand=True), # Initial placeholder
        expand=True, # Ensure switcher fills the view so child scroll works
    )

    # 3. Root View (Standard shell for Home/Plans/Favorites)
    root_view = ft.View(
        "/",
        controls=[body_switcher],
        padding=0,
        bgcolor="background",
        navigation_bar=nav_bar
    )
    
    # 4. View Cache & State
    # Cache content controls to preserve state (like scroll position) where possible
    views_cache = {} 
    plans_refresh_wrapper: dict = {"func": None}
    favorites_refresh_wrapper: dict = {"func": None}
    home_refresh_wrapper: dict = {"func": None}

    # --- Handlers & Helpers ---

    def show_guest_account_dialog(current_page: ft.Page):
        """Show dialog prompting guest user to create account."""
        def go_to_signup(e):
             current_page.close(dialog)
             # Import and launch login view
             from views.login_view import main as login_main
             try:
                 current_page.views.clear()
                 login_main(current_page)
             except Exception as ex:
                 print(f"Error launching login: {ex}")

        dialog = ft.AlertDialog(
            modal=True,
            title=ft.Text("Create Account for Full Access"),
            content=ft.Text("To create trip plans and access all features, please create an account."),
            actions=[
                ft.TextButton("Ok", on_click=lambda e: current_page.close(dialog)),
                ft.ElevatedButton("Sign up", on_click=go_to_signup, bgcolor="primary", color="white"),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )
        current_page.open(dialog)

    def on_new_plan(e):
        if auth_state_controller.is_guest:
            show_guest_account_dialog(page)
            return
        navigation_controller.navigate_to("/plan_trip")
        
    def on_open_plan(e, plan_data):
        """Navigate to plan summary view"""
        from .components.plan_summary import build_plan_summary_view
        
        if plan_data.get("is_generating", False):
            page.snack_bar = ft.SnackBar(content=ft.Text("Plan is still being generated..."), bgcolor="info")
            page.snack_bar.open = True
            page.update()
            return
        
        trip_data = plan_data.get("data", {}) if plan_data else {}
        plan_id = plan_data.get("id") if plan_data else None
        refresh_func = plans_refresh_wrapper["func"]
        
        def on_back_with_refresh(e):
            if len(page.views) > 1:
                page.views.pop()
                if refresh_func:
                    refresh_func()
                page.update()
        
        # Manually push view (Sub-View logic)
        page.views.append(
            ft.View(
                "/plan_summary",
                controls=[apply_gradient_background(
                    build_plan_summary_view(
                        on_back=on_back_with_refresh, 
                        trip_data=trip_data, 
                        page=page, 
                        plan_id=plan_id, 
                        on_delete_callback=refresh_func
                    )
                )],
                padding=0,
                bgcolor="background"
            )
        )
        page.update()

    # --- Routing Logic ---
    def route_change(e: ft.RouteChangeEvent):
        current_route = page.route or "/"
        print(f"DEBUG: Route changing to {current_route}")

        # 1. Handle Root Routes (Tabs)
        if current_route in ["/", "/plans", "/favorites"]:
            # Clean up any DatePicker overlays left behind by a previous /plan_trip visit.
            # plan_trip adds DatePicker controls to page.overlay each time it renders; without
            # explicit removal they accumulate across multiple visits and login/logout cycles.
            plan_trip_overlays = getattr(page, "_plan_trip_overlays", None)
            if plan_trip_overlays:
                for o in plan_trip_overlays:
                    try:
                        if o in page.overlay:
                            page.overlay.remove(o)
                    except Exception:
                        pass
                page._plan_trip_overlays = None

            # Rather than clearing the entire view stack destroying Flet's current UI DOM:
            if page.views and page.views[0] == root_view:
                # We simply pop any sub-routes off the top until only the root view remains
                while len(page.views) > 1:
                    page.views.pop()
            else:
                # Fallback: Root view missing, recreate stack
                page.views.clear()
                page.views.append(root_view)
            
            # Update FAB visibility (Only Plans has FAB)
            if current_route == "/plans":
                root_view.floating_action_button = create_floating_action_button(on_click=on_new_plan)
            else:
                root_view.floating_action_button = None
            
            # Update Content & Nav Bar
            if current_route == "/plans":
                nav_bar.selected_index = 1
                if "/plans" not in views_cache:
                    content, refresh = build_plans_view(page, on_open_plan=on_open_plan)
                    # Wrap in gradient
                    views_cache["/plans"] = apply_gradient_background(content)
                    plans_refresh_wrapper["func"] = refresh
                else:
                    if "func" in plans_refresh_wrapper and plans_refresh_wrapper["func"]:
                        import threading
                        threading.Thread(target=plans_refresh_wrapper["func"], daemon=True).start()
                        
                body_switcher.content = views_cache["/plans"]
                
            elif current_route == "/favorites":
                nav_bar.selected_index = 2
                
                # Check if we already have the view cached
                if "/favorites" not in views_cache:
                    selected_place_wrapper = {"value": navigation_controller.selected_place}
                    content, refresh = build_favorites_view(page, selected_place_wrapper, favorites_service=favorites_service)
                    views_cache["/favorites"] = apply_gradient_background(content)
                    favorites_refresh_wrapper["func"] = refresh
                else:
                    if "func" in favorites_refresh_wrapper and favorites_refresh_wrapper["func"]:
                        import threading
                        threading.Thread(target=favorites_refresh_wrapper["func"], daemon=True).start()

                body_switcher.content = views_cache["/favorites"]

            else: # Home
                nav_bar.selected_index = 0
                if "/" not in views_cache:
                    # build_home_content has internal gradient
                    views_cache["/"] = build_home_content()
                    home_refresh_wrapper["func"] = load_initial_places
                else:
                    if header_container_ref.current:
                        header_container_ref.current.content = build_header()
                        try:
                            header_container_ref.current.update()
                        except Exception:
                            pass
                    if "func" in home_refresh_wrapper and home_refresh_wrapper["func"]:
                        # Silently reload items
                        import threading
                        threading.Thread(target=home_refresh_wrapper["func"], daemon=True).start()
                body_switcher.content = views_cache["/"]
                
                # Check location logic on Home
                if not places_state_controller.location:
                   import threading
                   threading.Timer(0.1, geolocation_service.request_location).start()

        # 2. Handle Sub-Routes (Push on top)
        elif current_route == "/destination":
             # Ensure root is present for back nav
             if len(page.views) == 0: page.views.append(root_view)
             
             def on_back(e): navigation_controller.navigate_back()
             page.views.append(
                ft.View(
                    "/destination",
                    controls=[apply_gradient_background(build_destination_page(page, navigation_controller.selected_place, on_back=on_back))],
                    padding=0,
                    bgcolor="background",
                    navigation_bar=create_navigation_bar(selected_index=nav_bar.selected_index, on_change=handle_nav_change)
                )
             )
             
        elif current_route == "/settings":
             # Ensure root is present for back nav
             if len(page.views) == 0: page.views.append(root_view)
             
             page.views.append(
                ft.View(
                    "/settings",
                    controls=[apply_gradient_background(build_settings_content(page))],
                    padding=0,
                    bgcolor="background",
                    navigation_bar=create_navigation_bar(selected_index=-1, on_change=handle_nav_change)
                )
             )
             
        elif current_route == "/plan_trip":
             if len(page.views) == 0: page.views.append(root_view)
             def on_back_trip(e): navigation_controller.navigate_plans()
             content, overlays = build_plan_trip_view(page, on_back=on_back_trip)
             # Track what we added so we can remove it when navigating away.
             # Without this, each visit appends new DatePicker controls to
             # page.overlay and they are never cleaned up — over many login/logout
             # cycles or repeated plan-trip visits this causes overlay bloat.
             page._plan_trip_overlays = overlays
             for o in overlays: page.overlay.append(o)
             page.views.append(
                ft.View(
                    "/plan_trip", 
                    controls=[apply_gradient_background(content)], 
                    padding=0, 
                    bgcolor="background"
                    # No navigation bar for plan trip form
                )
             )
             
        elif current_route == "/profile_edit":
             if len(page.views) == 0: page.views.append(root_view)
             from .profile_view import build_profile_edit_view
             page.views.append(
                ft.View(
                    "/profile_edit",
                    controls=[apply_gradient_background(build_profile_edit_view(page))],
                    padding=0,
                    bgcolor="background"
                    # No navigation bar for edit screen
                )
             )
        
        page.update()

    def view_pop(e):
        if len(page.views) > 1:
            page.views.pop()
            top_view = page.views[-1]
            page.go(top_view.route)
        else:
            # If at root, maybe minimize or ignore?
            pass

    # CRITICAL: Always install our route_change as the authoritative handler.
    # main.py's OAuth handler must have been cleared before calling home_main().
    # We also set _view_route_change_handler for backward-compat with helpers
    # that check that attribute (e.g. settings_view, destination_card…).
    page._view_route_change_handler = route_change
    page.on_route_change = route_change
    page.on_view_pop = view_pop

    # ALWAYS reset route to "/" when home_view first loads.
    # Any stale route (e.g. "/settings" left over from the previous session
    # after logout) would cause route_change() to render the wrong screen.
    page.route = "/"

    # Trigger initial load
    route_change(None)


if __name__ == "__main__":
    ft.app(target=main)