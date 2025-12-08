import flet as ft
import asyncio
from services.api_service import APIService
from services.favorites_service import FavoritesService
from state import AuthStateController

class DestinationView(ft.Container):
    def __init__(self, page: ft.Page, place: dict, on_back=None):
        super().__init__(expand=True, bgcolor="background")
        self.page_ref = page
        # Normalize initial data
        self.place = self._normalize_place_data(place)
        self.on_back = on_back
        
        # Reuse shared services from page if available, otherwise create new ones
        if hasattr(page, "_shared_services"):
            self.api = page._shared_services.get("api_service", APIService())
            self.favorites_service = page._shared_services.get("favorites_service", FavoritesService())
        else:
            self.api = APIService()
            self.favorites_service = FavoritesService()
        
        self._fetch_task = None  # Track async fetch task for cleanup
        
        # Check initial favorite status
        self.place["is_favorite"] = self.favorites_service.is_favorite(self.place["place_id"])
        
        # State variables
        self.is_description_expanded = False
        self.related_places = []  # Store related places data
        
        # UI References for updates
        self.description_text = ft.Text(
            value=self.place.get("description") or "Loading description...",
            size=14,
            color="onSurfaceVariant",
            max_lines=3,  # Initially show 3 lines
            overflow=ft.TextOverflow.ELLIPSIS,
        )
        self.carousel_ref = ft.Ref[ft.Row]()
        self.reviews_column_ref = ft.Ref[ft.Column]()
        self.highlights_grid_ref = ft.Ref[ft.GridView]()
        self.title_section_ref = ft.Ref[ft.Column]() # Ref for title section
        self.description_expand_button_ref = ft.Ref[ft.TextButton]()
        self.related_places_column_ref = ft.Ref[ft.Column]()  # Ref for related places section
        self.related_places_items_ref = ft.Ref[ft.Column]()  # Ref for related places items (without title)
        self.favorite_button_ref = ft.Ref[ft.IconButton]()  # Ref for favorite button in header
        self.main_scroll_ref = ft.Ref[ft.Column]()  # Ref for main scrollable column
        self.map_image_ref = ft.Ref[ft.Image]()  # Ref for map image
        
        self.content = ft.SafeArea(content=self._build_layout(), expand=True)
        
    def _normalize_place_data(self, place: dict) -> dict:
        """Ensure consistent keys from different sources (Home vs API)."""
        return {
            "place_id": place.get("place_id") or place.get("id"),
            "name": place.get("name") or place.get("title") or "Unknown Place",
            "address": place.get("address") or place.get("formatted_address") or "Unknown Address",
            "rating": place.get("rating", 0.0),
            "user_rating_count": place.get("user_rating_count", 0),
            "description": place.get("description"),
            "photos": place.get("photos", []),
            "reviews": place.get("reviews", []),
            "image_url": place.get("image_url"), # Legacy/Single image
            "google_maps_url": place.get("google_maps_url"),
        }

    def did_mount(self):
        # Store task reference for potential cancellation
        self._fetch_task = self.page_ref.run_task(self._fetch_full_details)
    
    def will_unmount(self):
        """Cleanup when view is removed"""
        # Note: Flet doesn't provide direct task cancellation,
        # but we can mark that we're no longer active
        self._fetch_task = None

    async def update_place(self, new_place: dict):
        """
        Update the destination view with a new place.
        This method replaces all data and refreshes the UI.
        """
        print(f"\n=== DEBUG: update_place called ===")
        print(f"DEBUG: New place: {new_place.get('name')}")
        
        # Normalize and update place data
        self.place = self._normalize_place_data(new_place)
        
        # Reset state
        self.is_description_expanded = False
        self.related_places = []
        
        # Update favorite status
        self.place["is_favorite"] = self.favorites_service.is_favorite(self.place["place_id"])
        
        # Update description text
        self.description_text.value = self.place.get("description") or "Loading description..."
        self.description_text.max_lines = 3
        self.description_text.overflow = ft.TextOverflow.ELLIPSIS
        if self.description_text.page:
            self.description_text.update()
        
        # Update description expand button
        if self.description_expand_button_ref.current:
            self.description_expand_button_ref.current.text = "more"
            if self.description_expand_button_ref.current.page:
                self.description_expand_button_ref.current.update()
        
        # Update favorite button in header
        if self.favorite_button_ref.current:
            self.favorite_button_ref.current.icon = ft.Icons.FAVORITE if self.place.get("is_favorite") else ft.Icons.FAVORITE_BORDER
            self.favorite_button_ref.current.icon_color = "red" if self.place.get("is_favorite") else "onBackground"
            if self.favorite_button_ref.current.page:
                self.favorite_button_ref.current.update()
        
        # Scroll to top when new place is loaded
        if self.main_scroll_ref.current and self.main_scroll_ref.current.page:
            self.main_scroll_ref.current.scroll_to(offset=0, duration=300)
        
        # Update title section
        if self.title_section_ref.current and self.title_section_ref.current.page:
            self.title_section_ref.current.controls = self._build_title_section_controls()
            self.title_section_ref.current.update()
        
        # Update map image if location is available
        location = self.place.get("location")
        if location:
            lat = location.get("latitude")
            lng = location.get("longitude")
            if lat is not None and lng is not None:
                map_url = self.api.get_static_map_url(
                    lat,
                    lng,
                    width=600,
                    height=200,
                    zoom=15
                )
                if map_url and self.map_image_ref.current:
                    self.map_image_ref.current.src = map_url
                    self.map_image_ref.current.visible = True
                    if self.map_image_ref.current.page:
                        self.map_image_ref.current.update()
        
        # Update favorite button in header
        if self.favorite_button_ref.current:
            self.favorite_button_ref.current.icon = ft.Icons.FAVORITE if self.place.get("is_favorite") else ft.Icons.FAVORITE_BORDER
            self.favorite_button_ref.current.icon_color = "red" if self.place.get("is_favorite") else "onBackground"
            if self.favorite_button_ref.current.page:
                self.favorite_button_ref.current.update()
        
        # Update carousel
        if self.carousel_ref.current and self.carousel_ref.current.page:
            self.carousel_ref.current.controls = self._build_carousel_items()
            self.carousel_ref.current.update()
        
        # Update reviews
        if self.reviews_column_ref.current and self.reviews_column_ref.current.page:
            self.reviews_column_ref.current.controls = self._build_review_items()
            self.reviews_column_ref.current.update()
        
        # Clear related places initially
        if self.related_places_items_ref.current and self.related_places_items_ref.current.page:
            self.related_places_items_ref.current.controls = [
                ft.Text("Loading related places...", size=12, color="onSurfaceVariant", italic=True)
            ]
            self.related_places_items_ref.current.update()
        
        # Fetch full details for the new place
        await self._fetch_full_details()

    def _handle_related_place_click(self, place: dict):
        """
        Handle click on a related place card.
        Updates the destination view to show the clicked place.
        """
        print(f"DEBUG: Related place clicked: {place.get('name')}")
        # Run the async update in a task
        self.page_ref.run_task(self.update_place, place)

    def _open_google_maps(self, e):
        """
        Open Google Maps for the current place.
        Works on both web and mobile - will open app if installed on mobile.
        """
        location = self.place.get("location")
        google_maps_url = self.place.get("google_maps_url")
        address = self.place.get("address", "")
        
        # Use the google_maps_url if available (from API)
        if google_maps_url:
            url = google_maps_url
        elif location and location.get("latitude") and location.get("longitude"):
            # Construct Google Maps URL from coordinates
            lat = location.get("latitude")
            lng = location.get("longitude")
            # This URL format works on both web and mobile (opens app if installed)
            url = f"https://www.google.com/maps/search/?api=1&query={lat},{lng}"
        elif address:
            # Fallback to address search
            url = f"https://www.google.com/maps/search/?api=1&query={address}"
        else:
            print("DEBUG: No location data available to open Google Maps")
            return
        
        print(f"DEBUG: Opening Google Maps: {url}")
        self.page_ref.launch_url(url)

    async def _fetch_full_details(self):
        place_id = self.place.get("place_id")
        print(f"\n=== DEBUG: _fetch_full_details called ===")
        print(f"DEBUG: place_id = {place_id}")
        
        if not place_id:
            print("DEBUG: No place_id found, returning early")
            return

        # 1. Fetch details from Google Places API
        print(f"DEBUG: Calling get_place_details for {place_id}")
        details = await self.api.get_place_details(place_id)
        print(f"DEBUG: get_place_details returned: {details}")
        
        if "error" not in details:
            print("DEBUG: No error in details response")
            # Update state with new details
            self.place.update(details)
            
            # Update UI components
            # Prioitize editorial summary if available
            description_from_api = self.place.get("description")
            print(f"DEBUG: Description from API: {description_from_api}")
            
            if description_from_api:
                print("DEBUG: Setting description text from API")
                self.description_text.value = description_from_api
                if self.description_text.page:
                    self.description_text.update()
            else:
                print("DEBUG: No description in API response")
            
            if self.carousel_ref.current and self.carousel_ref.current.page:
                self.carousel_ref.current.controls = self._build_carousel_items()
                self.carousel_ref.current.update()
                
            if self.reviews_column_ref.current and self.reviews_column_ref.current.page:
                self.reviews_column_ref.current.controls = self._build_review_items()
                self.reviews_column_ref.current.update()

            # Update title section (rating, count, etc.)
            if self.title_section_ref.current and self.title_section_ref.current.page:
                # Rebuild the controls list for the column
                self.title_section_ref.current.controls = self._build_title_section_controls()
                self.title_section_ref.current.update()
            
            # Update map image if location is available
            location = self.place.get("location")
            print(f"DEBUG: _fetch_full_details - location after update: {location}")
            if location:
                lat = location.get("latitude")
                lng = location.get("longitude")
                print(f"DEBUG: _fetch_full_details - lat: {lat}, lng: {lng}")
                
                if lat is not None and lng is not None:
                    map_url = self.api.get_static_map_url(
                        lat,
                        lng,
                        width=800,  # Increased width for better aspect ratio
                        height=200,
                        zoom=15
                    )
                    print(f"DEBUG: _fetch_full_details - Generated map_url: {map_url[:100] if map_url else 'None'}...")
                    
                    # Update map image if ref exists
                    if self.map_image_ref.current:
                        if map_url:
                            self.map_image_ref.current.src = map_url
                            self.map_image_ref.current.visible = True
                            self.map_image_ref.current.fit = ft.ImageFit.COVER  # Maintain aspect ratio
                            if self.map_image_ref.current.page:
                                self.map_image_ref.current.update()
                            print("DEBUG: _fetch_full_details - Map image updated successfully")
                        else:
                            print("DEBUG: _fetch_full_details - map_url is empty, API key might be missing")
                            print(f"DEBUG: MAPS_STATIC_API_KEY exists: {bool(self.api.config.MAPS_STATIC_API_KEY)}")
                            if not self.api.config.MAPS_STATIC_API_KEY:
                                print("ERROR: MAPS_STATIC_API_KEY is not set in environment variables!")
                    else:
                        print("DEBUG: _fetch_full_details - map_image_ref.current is None")
                else:
                    print("DEBUG: _fetch_full_details - lat or lng is None")
            else:
                print("DEBUG: _fetch_full_details - location is None or missing")
                
                # 3. Fetch nearby/related places if we have location data
            if location and location.get("latitude") and location.get("longitude"):
                print(f"DEBUG: Fetching nearby places for location: {location}")
                nearby_places = await self.api.get_nearby_places(
                    location.get("latitude"),
                    location.get("longitude"),
                    radius=5000,
                    max_results=5
                )
                
                # Check if we got an error response
                if isinstance(nearby_places, dict) and "error" in nearby_places:
                    print(f"DEBUG: Error fetching nearby places: {nearby_places.get('error')}")
                    self.related_places = []  # Set empty list on error
                elif isinstance(nearby_places, list) and len(nearby_places) > 0:
                    # Filter out the current place from results
                    current_place_id = self.place.get("place_id")
                    self.related_places = [p for p in nearby_places if p.get("place_id") != current_place_id][:3]
                    print(f"DEBUG: Found {len(self.related_places)} related places")
                else:
                    print(f"DEBUG: No nearby places found or invalid response: {nearby_places}")
                    self.related_places = []
                
                # Update related places section
                if self.related_places_items_ref.current and self.related_places_items_ref.current.page:
                    self.related_places_items_ref.current.controls = self._build_related_places_items()
                    self.related_places_items_ref.current.update()
        else:
            print(f"DEBUG: Error in API response: {details.get('error')}")

        # 2. If description is still missing, set a default message
        if not self.place.get("description"):
            print("DEBUG: Description still missing after API call")
            self.description_text.value = "Description not available."
            if self.description_text.page:
                self.description_text.update()
        else:
            print(f"DEBUG: Description available: {self.place.get('description')[:50]}...")

    def _build_layout(self):
        return ft.Column(
            ref=self.main_scroll_ref,
            spacing=0,
            expand=True,
            scroll=ft.ScrollMode.AUTO,
            controls=[
                self._build_header(),
                self._build_image_carousel(),
                self._build_title_section(),
                self._build_tabs(),
            ]
        )

    def _build_header(self):
        return ft.Container(
            padding=ft.padding.only(left=16, right=16, top=16, bottom=8),
            bgcolor="background",
            content=ft.Row(
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                controls=[
                    ft.IconButton(
                        icon=ft.Icons.ARROW_BACK,
                        icon_color="onBackground",
                        on_click=self.on_back if self.on_back else lambda e: self.page_ref.go("/")
                    ),
                    ft.Text("About", size=18, weight=ft.FontWeight.W_600, color="onBackground"),
                    ft.IconButton(
                        ref=self.favorite_button_ref,
                        icon=ft.Icons.FAVORITE if self.place.get("is_favorite") else ft.Icons.FAVORITE_BORDER,
                        icon_color="red" if self.place.get("is_favorite") else "onBackground",
                        on_click=self._toggle_favorite
                    )
                ]
            )
        )

    def _show_guest_account_dialog(self):
        """Show dialog prompting guest user to create account for full functionality."""
        def go_to_signup(e):
            """Handle sign up button click - navigate to login view."""
            # Navigate to login view for registration/login flow
            self.page_ref.close(dialog)
            
            # Clear any view stack or route handlers
            try:
                if hasattr(self.page_ref, 'views') and isinstance(self.page_ref.views, list):
                    self.page_ref.views.clear()
            except Exception:
                pass

            try:
                if hasattr(self.page_ref, 'on_route_change'):
                    self.page_ref.on_route_change = None
            except Exception:
                pass
            
            try:
                if hasattr(self.page_ref, 'on_view_pop'):
                    self.page_ref.on_view_pop = None
            except Exception:
                pass

            # Import and launch login view
            from views.login_view import main as login_main
            try:
                self.page_ref.controls.clear()
            except Exception:
                pass
            
            try:
                self.page_ref.clean()
            except Exception:
                pass
            
            try:
                self.page_ref.route = "/"
            except Exception:
                pass
            
            try:
                login_main(self.page_ref)
                self.page_ref.update()
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
                ft.TextButton("Ok", on_click=lambda e: self.page_ref.close(dialog)),
                ft.ElevatedButton(
                    "Sign up",
                    on_click=go_to_signup,
                    bgcolor="primary",
                    color="white"
                ),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )
        self.page_ref.open(dialog)

    def _toggle_favorite(self, e):
        # Check if user is a guest
        auth_state_controller = getattr(self.page_ref, "_auth_state_controller", None)
        if auth_state_controller:
            print(f"DEBUG: Auth state - is_guest: {auth_state_controller.is_guest}, is_authenticated: {auth_state_controller.is_authenticated}")
            if auth_state_controller.is_guest:
                # Guest users cannot add favorites - show dialog
                print("DEBUG: Guest user detected, showing account creation dialog")
                self._show_guest_account_dialog()
                return
        else:
            print("DEBUG: No auth_state_controller found on page")
        
        is_fav = self.favorites_service.toggle_favorite(self.place)
        self.place["is_favorite"] = is_fav
        e.control.icon = ft.Icons.FAVORITE if is_fav else ft.Icons.FAVORITE_BORDER
        e.control.icon_color = "red" if is_fav else "onBackground"
        e.control.update()

    def _build_carousel_items(self):
        photos = self.place.get("photos", [])
        image_urls = []
        
        if photos:
            image_urls = [self.api.get_photo_url(p["photo_reference"]) for p in photos[:5]]
        elif self.place.get("image_url"):
             image_urls = [self.place.get("image_url")]
        else:
            image_urls = [
                "https://picsum.photos/800/600?random=1",
                "https://picsum.photos/800/600?random=2",
                "https://picsum.photos/800/600?random=3",
            ]

        images = [
            ft.Container(
                width=300,
                height=250,
                border_radius=16,
                clip_behavior=ft.ClipBehavior.HARD_EDGE,
                content=ft.Image(src=url, fit=ft.ImageFit.COVER, error_content=ft.Container(bgcolor="grey"))
            ) for url in image_urls
        ]
        
        return [ft.Container(width=16)] + images + [ft.Container(width=16)]

    def _build_image_carousel(self):
        return ft.Container(
            height=250,
            padding=ft.padding.only(top=16, bottom=16),
            content=ft.Row(
                ref=self.carousel_ref,
                scroll=ft.ScrollMode.HIDDEN,
                spacing=12,
                controls=self._build_carousel_items()
            )
        )

    def _build_title_section_controls(self):
        name = self.place.get("name")
        rating = self.place.get("rating")
        reviews_count = self.place.get("user_rating_count")
        address = self.place.get("address")
        
        return [
            ft.Text(name, size=24, weight=ft.FontWeight.BOLD, color="onBackground"),
            ft.Row(
                spacing=8,
                controls=[
                    ft.Icon(ft.Icons.STAR, color="amber", size=16),
                    ft.Text(f"{rating}", weight=ft.FontWeight.BOLD, color="onBackground"),
                    ft.Text(f"({reviews_count} reviews)", color="onSurfaceVariant", size=12),
                ]
            ),
            ft.Row(
                spacing=4,
                vertical_alignment=ft.CrossAxisAlignment.START,
                controls=[
                    ft.Icon(ft.Icons.LOCATION_ON, color="primary", size=16),
                    ft.Container(
                        expand=True,
                        content=ft.Text(address, color="onSurfaceVariant", size=12, max_lines=2, overflow=ft.TextOverflow.ELLIPSIS),
                    )
                ]
            )
        ]

    def _build_title_section(self):
        return ft.Container(
            padding=ft.padding.symmetric(horizontal=24),
            margin=ft.margin.only(bottom=16),
            content=ft.Column(
                ref=self.title_section_ref,
                spacing=8,
                controls=self._build_title_section_controls()
            )
        )

    def _build_tabs(self):
        tabs = ft.Tabs(
            selected_index=0,
            indicator_color="primary",
            label_color="primary",
            unselected_label_color="onSurfaceVariant",
            divider_color="transparent",
            tab_alignment=ft.TabAlignment.CENTER, # Center the tabs
            tabs=[
                ft.Tab(text="About", content=self._build_about_tab()),
                ft.Tab(text="Overview", content=self._build_overview_tab()),
            ],
        )
        return tabs

    def _build_about_tab(self):
        return ft.Container(
            padding=ft.padding.all(24),
            content=ft.Column(
                spacing=24,
                controls=[
                    self._build_description_section(),
                    self._build_location_section(),
                    self._build_related_places_section(),
                ]
            )
        )

    def _build_description_section(self):
        return ft.Column(
            spacing=8,
            controls=[
                ft.Text("Description", size=16, weight=ft.FontWeight.BOLD, color="onBackground"),
                self.description_text,
                ft.TextButton(
                    ref=self.description_expand_button_ref,
                    text="more",
                    style=ft.ButtonStyle(color="primary"),
                    on_click=self._toggle_description,
                ),
            ]
        )
    
    def _toggle_description(self, e):
        """Toggle between expanded and collapsed description view"""
        self.is_description_expanded = not self.is_description_expanded
        
        if self.is_description_expanded:
            # Expand: remove max_lines limit
            self.description_text.max_lines = None
            self.description_text.overflow = None
            if self.description_expand_button_ref.current:
                self.description_expand_button_ref.current.text = "less"
        else:
            # Collapse: set max_lines back to 3
            self.description_text.max_lines = 3
            self.description_text.overflow = ft.TextOverflow.ELLIPSIS
            if self.description_expand_button_ref.current:
                self.description_expand_button_ref.current.text = "more"
        
        # Update both components
        if self.description_text.page:
            self.description_text.update()
        if self.description_expand_button_ref.current and self.description_expand_button_ref.current.page:
            self.description_expand_button_ref.current.update()

    def _build_location_section(self):
        """Build the location section with address and static map."""
        location = self.place.get("location")
        address = self.place.get("address", "")
        
        print(f"DEBUG: _build_location_section - location: {location}")
        print(f"DEBUG: _build_location_section - address: {address}")
        
        # Generate map URL if we have location data
        map_url = ""
        if location:
            lat = location.get("latitude")
            lng = location.get("longitude")
            print(f"DEBUG: _build_location_section - lat: {lat}, lng: {lng}")
            
            if lat is not None and lng is not None:
                # Get container width if available, otherwise use a reasonable default
                # Using a wider aspect ratio (4:1) to better fill the container
                map_url = self.api.get_static_map_url(
                    lat,
                    lng,
                    width=800,  # Increased width for better aspect ratio
                    height=200,
                    zoom=15
                )
                print(f"DEBUG: _build_location_section - map_url: {map_url[:100] if map_url else 'None'}...")
        
        # Always create the Image with ref so we can update it when location data arrives
        # If no map URL initially, show a placeholder container, but still create the image ref
        if map_url:
            # We have a map URL, show the image - use COVER to maintain aspect ratio
            map_content = ft.Image(
                ref=self.map_image_ref,
                src=map_url,
                fit=ft.ImageFit.COVER,  # Use COVER to maintain aspect ratio and fill container
                width=None,  # Full width
                height=200,
                error_content=ft.Container(
                    height=200,
                    border_radius=16,
                    bgcolor="#E0E0E0",
                    alignment=ft.alignment.center,
                    content=ft.Column(
                        alignment=ft.MainAxisAlignment.CENTER,
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                        controls=[
                            ft.Icon(ft.Icons.MAP, size=40, color="grey"),
                            ft.Text("Map unavailable", color="grey", size=12)
                        ]
                    )
                )
            )
        else:
            # No map URL yet, create placeholder but also create hidden image with ref for later update
            map_content = ft.Stack(
                [
                    # Loading placeholder (visible)
                    ft.Container(
                        height=200,
                        width=None,  # Full width
                        border_radius=16,
                        bgcolor="#E0E0E0",
                        alignment=ft.alignment.center,
                        content=ft.Column(
                            alignment=ft.MainAxisAlignment.CENTER,
                            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                            controls=[
                                ft.Icon(ft.Icons.MAP, size=40, color="grey"),
                                ft.Text("Loading map...", color="grey", size=12)
                            ]
                        )
                    ),
                    # Hidden image with ref (will be shown when URL is set)
                    ft.Image(
                        ref=self.map_image_ref,
                        src="",
                        fit=ft.ImageFit.COVER,  # Use COVER to maintain aspect ratio
                        width=None,  # Full width
                        height=200,
                        visible=False,
                        error_content=ft.Container(
                            height=200,
                            border_radius=16,
                            bgcolor="#E0E0E0",
                            alignment=ft.alignment.center,
                            content=ft.Column(
                                alignment=ft.MainAxisAlignment.CENTER,
                                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                                controls=[
                                    ft.Icon(ft.Icons.MAP, size=40, color="grey"),
                                    ft.Text("Map unavailable", color="grey", size=12)
                                ]
                            )
                        )
                    )
                ]
            )
        
        # Create clickable map container
        map_container = ft.Container(
            height=200,
            width=None,  # Full width
            border_radius=16,
            clip_behavior=ft.ClipBehavior.HARD_EDGE,
            content=map_content,
            on_click=self._open_google_maps,
            ink=True,  # Add ripple effect on click
        )
        
        return ft.Column(
            spacing=8,
            controls=[
                ft.Text("Location", size=16, weight=ft.FontWeight.BOLD, color="onBackground"),
                ft.Text(address, size=12, color="onSurfaceVariant"),
                map_container
            ]
        )

    def _build_related_places_items(self):
        """Build the list of related places items."""
        items = []
        
        if not self.related_places:
            # Show empty state message
            items.append(
                ft.Text(
                    "No related places found nearby.",
                    size=12,
                    color="onSurfaceVariant",
                    italic=True
                )
            )
            return items
        
        for place in self.related_places:
            # Get photo URL if available
            photo_url = ""
            if place.get("photos") and len(place["photos"]) > 0:
                photo_url = self.api.get_photo_url(place["photos"][0]["photo_reference"], max_width=200)
            else:
                photo_url = "https://picsum.photos/200/200?random=" + str(hash(place.get("name", "")) % 1000)
            
            # Format distance
            distance_text = "N/A"
            if place.get("distance_km"):
                if place["distance_km"] < 1:
                    distance_text = f"{int(place['distance_km'] * 1000)} m"
                else:
                    distance_text = f"{place['distance_km']} km"
            
            items.append(
                ft.Container(
                    padding=10,
                    border_radius=12,
                    bgcolor="surface",
                    border=ft.border.all(1, "#E0E0E0"),
                    ink=True,  # Add ink ripple effect
                    on_click=lambda e, p=place: self._handle_related_place_click(p),
                    content=ft.Row(
                        controls=[
                            ft.Container(
                                width=80,
                                height=80,
                                border_radius=12,
                                clip_behavior=ft.ClipBehavior.HARD_EDGE,
                                content=ft.Image(
                                    src=photo_url,
                                    fit=ft.ImageFit.COVER,
                                    error_content=ft.Container(
                                        bgcolor="grey",
                                        content=ft.Icon(ft.Icons.PLACE, size=40, color="white")
                                    )
                                )
                            ),
                            ft.Column(
                                alignment=ft.MainAxisAlignment.CENTER,
                                spacing=4,
                                expand=True,
                                controls=[
                                    ft.Text(
                                        place.get("name", "Unknown Place"),
                                        size=14,
                                        weight=ft.FontWeight.W_600,
                                        color="onBackground"
                                    ),
                                    ft.Text(
                                        f"Distance: {distance_text}",
                                        size=12,
                                        color="onSurfaceVariant"
                                    ),
                                ]
                            ),
                            ft.Icon(
                                ft.Icons.CHEVRON_RIGHT,
                                size=20,
                                color="onSurfaceVariant"
                            )
                        ]
                    )
                )
            )
        
        return items

    def _build_related_places_section(self):
        return ft.Column(
            ref=self.related_places_column_ref,
            spacing=12,
            controls=[
                ft.Text("Related Places", size=16, weight=ft.FontWeight.BOLD, color="onBackground"),
                ft.Column(
                    ref=self.related_places_items_ref,
                    spacing=12,
                    controls=self._build_related_places_items()
                )
            ]
        )

    def _build_overview_tab(self):
        return ft.Container(
            padding=ft.padding.all(24),
            content=ft.Column(
                spacing=24,
                controls=[
                    self._build_highlights_section(),
                    self._build_reviews_section(),
                ]
            )
        )

    def _build_highlights_section(self):
        # Mock highlights
        highlights = [
            {"icon": ft.Icons.WIFI, "label": "Free Wifi"},
            {"icon": ft.Icons.POOL, "label": "Pool"},
            {"icon": ft.Icons.AC_UNIT, "label": "AC"},
            {"icon": ft.Icons.RESTAURANT, "label": "Dining"},
            {"icon": ft.Icons.LOCAL_PARKING, "label": "Parking"},
            {"icon": ft.Icons.FITNESS_CENTER, "label": "Gym"},
        ]

        items = []
        for item in highlights:
            items.append(
                ft.Container(
                    width=150, # Approximate width for 2 columns on mobile, or use expand/flex in Row if needed
                    padding=12,
                    border_radius=12,
                    bgcolor="surfaceVariant", # Light background for item
                    content=ft.Row(
                        spacing=12,
                        controls=[
                            ft.Icon(item["icon"], size=20, color="primary"),
                            ft.Text(item["label"], size=13, weight=ft.FontWeight.W_500)
                        ]
                    )
                )
            )

        return ft.Column(
            spacing=12,
            controls=[
                ft.Text("Highlights", size=16, weight=ft.FontWeight.BOLD, color="onBackground"),
                ft.Row(
                    wrap=True,
                    spacing=10,
                    run_spacing=10,
                    controls=items,
                )
            ]
        )

    def _build_review_items(self):
        reviews = self.place.get("reviews", [])
        if not reviews:
            return [ft.Text("No reviews yet.", color="grey")]
        
        review_cards = []
        for review in reviews[:3]:
            review_cards.append(
                ft.Container(
                    padding=16,
                    border_radius=12,
                    border=ft.border.all(1, "#E0E0E0"),
                    content=ft.Column(
                        spacing=8,
                        controls=[
                            ft.Row(
                                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                                controls=[
                                    ft.Row(
                                        spacing=8,
                                        controls=[
                                            ft.CircleAvatar(
                                                radius=16,
                                                foreground_image_src=review.get("author_photo", "") or "https://picsum.photos/50/50"
                                            ),
                                            ft.Text(review.get("author_name", "Anonymous"), weight=ft.FontWeight.BOLD, size=13)
                                        ]
                                    ),
                                    ft.Container(
                                        padding=ft.padding.symmetric(horizontal=8, vertical=4),
                                        border_radius=12,
                                        bgcolor="surfaceVariant",
                                        content=ft.Row(
                                            spacing=4,
                                            controls=[
                                                ft.Icon(ft.Icons.STAR, size=12, color="amber"),
                                                ft.Text(f"{review.get('rating')}", size=11, weight=ft.FontWeight.BOLD)
                                            ]
                                        )
                                    )
                                ]
                            ),
                            ft.Text(
                                review.get("text", ""),
                                size=12,
                                color="onSurfaceVariant",
                                max_lines=3,
                                overflow=ft.TextOverflow.ELLIPSIS
                            ),
                            ft.Text(review.get("relative_time", ""), size=11, color="grey")
                        ]
                    )
                )
            )
        
        return [
            ft.Row(
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                controls=[
                    ft.Text(f"Reviews ({self.place.get('user_rating_count', 0)})", size=16, weight=ft.FontWeight.BOLD, color="onBackground"),
                    ft.TextButton("View All", style=ft.ButtonStyle(color="primary"))
                ]
            ),
            *review_cards
        ]

    def _build_reviews_section(self):
        return ft.Column(
            ref=self.reviews_column_ref,
            spacing=12,
            controls=self._build_review_items()
        )

    def _show_all_reviews(self, e):
        # Create a new list for the bottom sheet to avoid modifying the main view's list directly if we want them separate
        # But here we want to show all.
        
        self.all_reviews_data = self.place.get("reviews", [])[:]
        # If less than 10, maybe duplicate for demo purposes if needed, or just show what we have.
        # The requirement is "display at least 10 ratings". 
        # If API returns 5, we might need to mock to reach 10 for the initial view if strictly required,
        # or just load more immediately. Let's start with what we have and load more.
        
        self.bs_reviews_list = ft.ListView(expand=True, spacing=16, padding=24)
        self.bs_reviews_list.on_scroll_interval = 0
        self.bs_reviews_list.on_scroll = self._on_reviews_scroll
        
        # Initial population
        self._populate_reviews_list()

        self.bottom_sheet = ft.BottomSheet(
            content=ft.Container(
                padding=ft.padding.only(top=16),
                bgcolor="surface",
                border_radius=ft.border_radius.only(top_left=24, top_right=24),
                content=ft.Column(
                    controls=[
                        ft.Container(
                            alignment=ft.alignment.center,
                            padding=10,
                            content=ft.Container(
                                width=40, height=4, bgcolor="outlineVariant", border_radius=2
                            )
                        ),
                        ft.Container(
                            padding=ft.padding.symmetric(horizontal=24),
                            content=ft.Text("All Reviews", size=20, weight=ft.FontWeight.BOLD, color="onBackground")
                        ),
                        ft.Container(
                            expand=True,
                            content=self.bs_reviews_list
                        )
                    ]
                )
            ),
            on_dismiss=lambda e: print("Bottom sheet dismissed")
        )
        self.page_ref.open(self.bottom_sheet)
        
        # Google Places API usually returns 5 reviews. We show what we have.
        # if len(self.all_reviews_data) < 10:
        #      self._load_more_reviews()

    def _populate_reviews_list(self):
        self.bs_reviews_list.controls.clear()
        for review in self.all_reviews_data:
            self.bs_reviews_list.controls.append(self._build_single_review_card(review))
        
        # Add "View on Google Maps" button
        if self.place.get("google_maps_url"):
            google_maps_button = ft.Container(
                padding=ft.padding.symmetric(vertical=20),
                content=ft.ElevatedButton(
                    "View more on Google Maps",
                    icon=ft.Icons.MAP,
                    style=ft.ButtonStyle(
                        color="onPrimary",
                        bgcolor="primary",
                        shape=ft.RoundedRectangleBorder(radius=12),
                        padding=16,
                    ),
                    on_click=lambda e: self.page_ref.launch_url(self.place.get("google_maps_url"))
                ),
                alignment=ft.alignment.center,
            )
            self.bs_reviews_list.controls.append(google_maps_button)
        
        if self.bs_reviews_list.page:
            self.bs_reviews_list.update()

    def _build_single_review_card(self, review):
        return ft.Container(
            padding=16,
            border_radius=12,
            border=ft.border.all(1, "#E0E0E0"),
            content=ft.Column(
                spacing=8,
                controls=[
                    ft.Row(
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                        controls=[
                            ft.Row(
                                spacing=8,
                                controls=[
                                    ft.CircleAvatar(
                                        radius=16,
                                        foreground_image_src=review.get("author_photo", "") or "https://picsum.photos/50/50"
                                    ),
                                    ft.Text(review.get("author_name", "Anonymous"), weight=ft.FontWeight.BOLD, size=13, color="onBackground")
                                ]
                            ),
                            ft.Container(
                                padding=ft.padding.symmetric(horizontal=8, vertical=4),
                                border_radius=12,
                                bgcolor="surfaceVariant",
                                content=ft.Row(
                                    spacing=4,
                                    controls=[
                                        ft.Icon(ft.Icons.STAR, size=12, color="amber"),
                                        ft.Text(f"{review.get('rating')}", size=11, weight=ft.FontWeight.BOLD)
                                    ]
                                )
                            )
                        ]
                    ),
                    ft.Text(
                        review.get("text", ""),
                        size=13,
                        color="onSurfaceVariant",
                    ),
                    ft.Text(review.get("relative_time", ""), size=11, color="grey")
                ]
            )
        )

    def _on_reviews_scroll(self, e: ft.OnScrollEvent):
        if e.pixels >= e.max_scroll_extent - 50:
            self._load_more_reviews()

    def _load_more_reviews(self):
        if hasattr(self, "is_loading_reviews") and self.is_loading_reviews:
            return
        
        self.is_loading_reviews = True
        if hasattr(self, "loading_indicator"):
            self.loading_indicator.visible = True
            self.loading_indicator.update()
        
        # Simulate network delay
        async def load_task():
            import asyncio
            # await asyncio.sleep(1.5) # No need to simulate delay if we have no more data to fetch
            
            # Since Google Places API v1 (and legacy) typically returns only up to 5 reviews in the details call,
            # and there is no direct pagination for reviews in this endpoint to get more,
            # we will stop loading more. 
            # If we had a backend that cached reviews or used a different method, we would fetch here.
            
            # For now, we just stop the loading indicator as there are no more "real" reviews to fetch from this endpoint.
            self.is_loading_reviews = False
            if hasattr(self, "loading_indicator"):
                self.loading_indicator.visible = False
                self.loading_indicator.update()
            
        self.page_ref.run_task(load_task)

    def _build_review_items(self):
        reviews = self.place.get("reviews", [])
        if not reviews:
            return [ft.Text("No reviews yet.", color="grey")]
        
        review_cards = []
        for review in reviews[:3]:
            review_cards.append(
                ft.Container(
                    padding=16,
                    border_radius=12,
                    border=ft.border.all(1, "#E0E0E0"),
                    content=ft.Column(
                        spacing=8,
                        controls=[
                            ft.Row(
                                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                                controls=[
                                    ft.Row(
                                        spacing=8,
                                        controls=[
                                            ft.CircleAvatar(
                                                radius=16,
                                                foreground_image_src=review.get("author_photo", "") or "https://picsum.photos/50/50"
                                            ),
                                            ft.Text(review.get("author_name", "Anonymous"), weight=ft.FontWeight.BOLD, size=13)
                                        ]
                                    ),
                                    ft.Container(
                                        padding=ft.padding.symmetric(horizontal=8, vertical=4),
                                        border_radius=12,
                                        bgcolor="surfaceVariant",
                                        content=ft.Row(
                                            spacing=4,
                                            controls=[
                                                ft.Icon(ft.Icons.STAR, size=12, color="amber"),
                                                ft.Text(f"{review.get('rating')}", size=11, weight=ft.FontWeight.BOLD)
                                            ]
                                        )
                                    )
                                ]
                            ),
                            ft.Text(
                                review.get("text", ""),
                                size=12,
                                color="onSurfaceVariant",
                                max_lines=3,
                                overflow=ft.TextOverflow.ELLIPSIS
                            ),
                            ft.Text(review.get("relative_time", ""), size=11, color="grey")
                        ]
                    )
                )
            )
        
        return [
            ft.Row(
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                controls=[
                    ft.Text(f"Reviews ({self.place.get('user_rating_count', 0)})", size=16, weight=ft.FontWeight.BOLD, color="onBackground"),
                    ft.TextButton("View All", style=ft.ButtonStyle(color="primary"), on_click=self._show_all_reviews)
                ]
            ),
            *review_cards
        ]

def build_destination_page(page: ft.Page, place: dict, on_back=None) -> ft.Control:
    """
    Entry point for the destination page.
    Returns a DestinationView control.
    """
    return DestinationView(page, place, on_back)
