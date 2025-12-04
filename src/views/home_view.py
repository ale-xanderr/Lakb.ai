import flet as ft
from .components.nav_bar import create_navigation_bar
from .components.destination_card import build_destination_page
from .settings_view import build_settings_content
from .favorites_view import build_favorites_view
from .app_config import configure_page
from services.api_service import APIService
from services.favorites_service import FavoritesService

def main(page: ft.Page):
    # 1. Device / window configuration (centralized)
    configure_page(page, title="Travel App Home")

    # --- Theme Configuration ---
    # Define custom color schemes for Light and Dark modes
    
    # Light Theme
    page.theme = ft.Theme(
        color_scheme=ft.ColorScheme(
            background="#fafdfc",
            on_background="#091a13",
            primary="#46bd8d",
            secondary="#95cbd9",
            tertiary="#76a2ce",
            surface="#FFFFFF",
            on_surface="#091a13",
            on_surface_variant="#5f6368",
        ),
        font_family="Poppins",
        page_transitions=ft.PageTransitionsTheme(
            android=ft.PageTransitionTheme.NONE,
            ios=ft.PageTransitionTheme.NONE,
            macos=ft.PageTransitionTheme.NONE,
            linux=ft.PageTransitionTheme.NONE,
            windows=ft.PageTransitionTheme.NONE,
        ),
    )

    # Dark Theme
    page.dark_theme = ft.Theme(
        color_scheme=ft.ColorScheme(
            background="#010403",
            on_background="#e4f6ef",
            primary="#42b889",
            secondary="#265c69",
            tertiary="#315c87",
            surface="#12161C",
            on_surface="#e4f6ef",
            on_surface_variant="#a0b3af",
        ),
        font_family="Poppins",
        page_transitions=ft.PageTransitionsTheme(
            android=ft.PageTransitionTheme.NONE,
            ios=ft.PageTransitionTheme.NONE,
            macos=ft.PageTransitionTheme.NONE,
            linux=ft.PageTransitionTheme.NONE,
            windows=ft.PageTransitionTheme.NONE,
        ),
    )

    # Set initial background color to follow theme
    page.bgcolor = "background"

    # --- Fonts Setup ---
    page.fonts = {
        "Courgette": "https://github.com/google/fonts/raw/main/ofl/courgette/Courgette-Regular.ttf",
        "Poppins": "https://github.com/google/fonts/raw/main/ofl/poppins/Poppins-Regular.ttf",
        "PoppinsBold": "https://github.com/google/fonts/raw/main/ofl/poppins/Poppins-Bold.ttf",
    }

    # --- Simple routing state ---
    selected_place = {"value": None}
    current_nav_index = {"value": 0}

    # --- Bottom navigation handler ---
    def handle_nav_change(e: ft.ControlEvent):
        idx = e.control.selected_index

        # 0 = Home, 1 = Favorites, 2 = Plans, 3 = Profile/Settings
        current_nav_index["value"] = idx
        if idx == 0:
            page.go("/")
        elif idx == 1:
            page.go("/favorites")
        elif idx == 3:
            page.go("/settings")
        else:
            # For now, keep the current route for unimplemented tabs
            page.go(page.route or "/")

    # --- API & State ---
    api_service = APIService()
    favorites_service = FavoritesService()
    
    places_state = {
        "data": [],
        "next_page_token": None,
        "query": "",
        "type": "lodging" # Default type
    }
    
    # Reference to the column that holds the cards, so we can update it
    places_column_ref = ft.Ref[ft.Column]()
    load_more_btn_ref = ft.Ref[ft.Container]()
    section_title_ref = ft.Ref[ft.Text]()

    def load_places(load_more=False, query=None, place_type=None, update_ui=True):
        """
        Fetch places from API and update the UI.
        """
        # If not loading more, reset state
        if not load_more:
            places_state["data"] = []
            places_state["next_page_token"] = None
            if query is not None:
                places_state["query"] = query
            if place_type is not None:
                places_state["type"] = place_type
        
        # Prepare args
        kwargs = {}
        if places_state["query"]:
            kwargs["query"] = places_state["query"]
        
        # Only use type if no query, or if API supports both (it does)
        if places_state["type"]:
            kwargs["place_type"] = places_state["type"]
            
        if load_more and places_state["next_page_token"]:
            kwargs["page_token"] = places_state["next_page_token"]
        elif load_more and not places_state["next_page_token"]:
            return # No more pages

        # Fetch data (Sync call)
        print("DEBUG: Calling api_service.search_places...")
        result = api_service.search_places(**kwargs)
        
        if "results" in result:
            new_places = result["results"]
            print(f"DEBUG: load_places got {len(new_places)} results")
            # Filter out places without photos if desired, or just add them
            for p in new_places:
                p["is_favorite"] = favorites_service.is_favorite(p.get("place_id"))
            
            places_state["data"].extend(new_places)
            places_state["next_page_token"] = result.get("next_page_token")
            
            # Update UI
            if update_ui:
                print("DEBUG: Updating UI in load_places")
                render_places()
        else:
            print(f"API Error or No Results: {result}")
            if not load_more:
                 places_state["data"] = []
                 if update_ui:
                    render_places()

    def render_places():
        # Update Title
        if section_title_ref.current:
            q = places_state["query"]
            t = places_state["type"]
            title_text = "Popular Places"
            
            if q and t:
                title_text = f"Popular {t} in {q}"
            elif q:
                title_text = f"Popular in {q}"
            elif t:
                title_text = f"Popular {t}"
            
            # Capitalize nicely
            import string
            section_title_ref.current.value = string.capwords(title_text)
            section_title_ref.current.update()

        if places_column_ref.current and places_column_ref.current.page:
            places_column_ref.current.controls.clear()
            for place in places_state["data"]:
                places_column_ref.current.controls.append(build_feature_card(place))
            
            places_column_ref.current.update()
            
        if load_more_btn_ref.current and load_more_btn_ref.current.page:
            load_more_btn_ref.current.visible = bool(places_state["next_page_token"])
            load_more_btn_ref.current.update()

    # --- MOCK API DATA REMOVED ---

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

    def build_search_bar(on_filter_click):
        return ft.Container(
            bgcolor="surface", # Use Surface for search bar (White in Light, Dark in Dark)
            border_radius=30,
            padding=ft.padding.symmetric(horizontal=20, vertical=8),
            shadow=ft.BoxShadow(blur_radius=15, spread_radius=1, color=ft.Colors.with_opacity(0.12, ft.Colors.BLACK)),
            content=ft.Row(
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
                controls=[
                    ft.Icon(ft.Icons.SEARCH, color="#B0B0B0", size=24), # Hardcoded grey
                    ft.TextField(
                        hint_text="Search",
                        hint_style=ft.TextStyle(color="#B0B0B0", size=16),
                        border=ft.InputBorder.NONE,
                        expand=True,
                        text_style=ft.TextStyle(color="onBackground"),
                        content_padding=ft.padding.symmetric(vertical=4),
                        on_submit=handle_search # Trigger search on enter
                    ),
                    ft.IconButton(
                        icon=ft.Icons.TUNE,
                        icon_color="onBackground",
                        icon_size=24,
                        on_click=on_filter_click
                    )
                ]
            )
        )
        
    def handle_search(e):
        query = e.control.value
        load_places(query=query)

    # State for category tabs
    selected_category = {"value": "Hotel"}

    def build_more_categories_sheet():
        """
        Builds a bottom sheet with categorized filters.
        """
        # We need to define the bottom sheet first to reference it in the close callback
        # Fix: Provide a placeholder content to satisfy the constructor
        bs = ft.BottomSheet(content=ft.Container())

        def on_category_click(e, category):
            # Close bottom sheet
            page.close(bs)
            # Update selected category and load places
            selected_category["value"] = category
            # We might want to update the tabs row to reflect this if the category is in the top list,
            # but since it's "More", it might not be. 
            # For now, just load the places.
            load_places(place_type=category)

        def build_section(icon, title, items):
            return ft.Column(
                spacing=10,
                controls=[
                    ft.Row(
                        controls=[
                            ft.Icon(icon, color="primary"),
                            ft.Text(title, weight=ft.FontWeight.BOLD, size=16, color="onBackground")
                        ]
                    ),
                    ft.Row(
                        wrap=True,
                        spacing=8,
                        run_spacing=8,
                        controls=[
                            ft.Container(
                                padding=ft.padding.symmetric(horizontal=16, vertical=8),
                                border=ft.border.all(1, "#E0E0E0"),
                                border_radius=20,
                                content=ft.Text(item, color="onBackground", size=12),
                                on_click=lambda e, i=item: on_category_click(e, i)
                            ) for item in items
                        ]
                    )
                ]
            )

        bs.content = ft.Container(
            padding=20,
            bgcolor="surface",
            border_radius=ft.border_radius.only(top_left=20, top_right=20),
            content=ft.Column(
                tight=True,
                scroll=ft.ScrollMode.AUTO,
                controls=[
                    ft.Container(
                        alignment=ft.alignment.center,
                        content=ft.Container(width=40, height=4, bgcolor="#E0E0E0", border_radius=2)
                    ),
                    ft.Container(height=10),
                    build_section(ft.Icons.RESTAURANT, "Food & Drink", ["Restaurant", "Bar", "Cafe", "Bakery"]),
                    ft.Divider(color="transparent", height=10),
                    build_section(ft.Icons.ATTRACTIONS, "Things to Do", ["Park", "Gym", "Museum", "Library", "Tourist Attraction", "Art Gallery", "Casino"]),
                    ft.Divider(color="transparent", height=10),
                    build_section(ft.Icons.SHOPPING_BAG, "Shopping", ["Shopping Mall", "Convenience Store", "Supermarket", "Clothing Store"]),
                    ft.Divider(color="transparent", height=10),
                    build_section(ft.Icons.HOTEL, "Services", ["Lodging", "Hotel", "Hospital", "Bank", "ATM"]),
                    ft.Container(height=20),
                ]
            )
        )
        return bs

    def build_category_tabs():
        # Expanded list of categories as requested
        tabs = ["Hotel", "Cafe", "Restaurant", "Lodging"]
        
        # Create the Row first so we can reference it in the update function
        tabs_row = ft.Row(scroll=ft.ScrollMode.HIDDEN, spacing=10)

        def update_tabs():
            tabs_row.controls.clear()
            for tab in tabs:
                is_active = (tab == selected_category["value"])
                # Active: Primary bg, White text
                # Inactive: Transparent bg, OnBackground text
                bg_color = "primary" if is_active else "transparent"
                text_color = "#FFFFFF" if is_active else "onBackground"
                border = None if is_active else ft.border.all(1, "#E0E0E0")
                
                def on_tab_click(e, t=tab):
                    selected_category["value"] = t
                    update_tabs()
                    tabs_row.update()
                    # Trigger API filter
                    load_places(place_type=t) 

                tabs_row.controls.append(
                    ft.Container(
                        padding=ft.padding.symmetric(horizontal=24, vertical=12),
                        bgcolor=bg_color,
                        border=border,
                        border_radius=25,
                        content=ft.Text(tab, color=text_color, weight=ft.FontWeight.W_500),
                        on_click=on_tab_click
                    )
                )
            
            # Add "More" button
            tabs_row.controls.append(
                ft.Container(
                    padding=ft.padding.symmetric(horizontal=24, vertical=12),
                    bgcolor="transparent",
                    border=ft.border.all(1, "#E0E0E0"),
                    border_radius=25,
                    content=ft.Row(
                         spacing=4,
                         controls=[
                             ft.Text("More", color="onBackground", weight=ft.FontWeight.W_500),
                             ft.Icon(ft.Icons.KEYBOARD_ARROW_DOWN, color="onBackground", size=16)
                         ]
                    ),
                    on_click=lambda e: page.open(build_more_categories_sheet())
                )
            )
        
        # Initial population
        update_tabs()
        return tabs_row

    # 4. Feature Card (Updated layout: image, title + address, heart button)
    def build_feature_card(data):
        # Map API data to UI fields
        # API keys: name, formatted_address, photos, place_id, rating
        title = data.get("name", "Unknown")
        address = data.get("formatted_address", "")
        place_id = data.get("place_id")
        
        image_url = None
        if "photos" in data and len(data["photos"]) > 0:
            photo_ref = data["photos"][0]["photo_reference"]
            image_url = api_service.get_photo_url(photo_ref)
        
        # Image Logic: Check if URL exists, otherwise show placeholder Icon
        image_content = None
        if image_url:
            image_content = ft.Image(
                src=image_url,
                fit=ft.ImageFit.COVER,
                width=float("inf"), # Expand width
                height=float("inf"), # Expand height to fill container
            )
        else:
            # Placeholder for missing API image
            image_content = ft.Column(
                alignment=ft.MainAxisAlignment.CENTER,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                controls=[
                    ft.Icon(ft.Icons.IMAGE_NOT_SUPPORTED_OUTLINED, color="#B0B0B0", size=40),
                    ft.Text("No Image", color="#B0B0B0", size=12)
                ]
            )

        def on_card_click(e):
            # Store selected place and navigate to destination screen
            # We might need to fetch full details if not all info is here
            # For now, pass what we have.
            # Map back to expected format for destination view if needed
            # Destination view likely expects 'title', 'address', 'image_url', 'description', 'price'
            # We'll adapt it on the fly or here.
            adapted_data = {
                "title": title,
                "address": address,
                "image_url": image_url,
                "description": "Description not available from Search API", # Details API needed for this
                "price": "N/A",
                "rating": data.get("rating", 0),
                "id": place_id,
                "is_favorite": data.get("is_favorite", False)
            }
            selected_place["value"] = adapted_data
            page.go("/destination")

        def toggle_favorite(e, item):
            is_fav = favorites_service.toggle_favorite(item)
            item["is_favorite"] = is_fav
            e.control.icon = ft.Icons.FAVORITE if is_fav else ft.Icons.FAVORITE_BORDER
            e.control.icon_color = "red" if is_fav else "primary"
            e.control.update()

        # Use theme colors
        card_bg = "surface" 

        return ft.Container(
            bgcolor=card_bg,
            border_radius=24,
            border=ft.border.all(1, ft.Colors.with_opacity(0.08, "onSurface")),
            padding=16,
            margin=ft.margin.only(bottom=16),  # Add spacing between cards
            on_click=on_card_click,
            content=ft.Column(
                spacing=8,
                controls=[
                    # Image Container
                    ft.Container(
                        height=180,
                        border_radius=18,
                        bgcolor="#2A2A2A",  # Background for placeholder
                        clip_behavior=ft.ClipBehavior.HARD_EDGE,  # Ensures image stays inside rounded corners
                        content=image_content,
                    ),

                    ft.Container(height=8),

                    # Title + Address + Heart button (row)
                    ft.Row(
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                        vertical_alignment=ft.CrossAxisAlignment.CENTER,
                        controls=[
                            ft.Column(
                                spacing=2,
                                alignment=ft.MainAxisAlignment.CENTER,
                                expand=True, # Take all available space to push button to right and constrain text
                                controls=[
                                    ft.Text(
                                        title,
                                        color="onSurface", # Adapts to theme
                                        size=18,
                                        weight=ft.FontWeight.BOLD,
                                        max_lines=1, # Truncate long titles
                                        overflow=ft.TextOverflow.ELLIPSIS,
                                    ),
                                    ft.Text(
                                        address,
                                        color="onSurfaceVariant", # Adapts to theme
                                        size=11,
                                        max_lines=1, # Truncate long addresses
                                        overflow=ft.TextOverflow.ELLIPSIS,
                                    ),
                                ],
                            ),
                            ft.IconButton(
                                icon=ft.Icons.FAVORITE if data.get("is_favorite") else ft.Icons.FAVORITE_BORDER,
                                icon_color="red" if data.get("is_favorite") else "primary",
                                bgcolor="background", # This might be light or dark depending on theme
                                style=ft.ButtonStyle(
                                    shape={
                                        ft.ControlState.DEFAULT: ft.RoundedRectangleBorder(
                                            radius=9999
                                        )
                                    },
                                    padding=10,
                                ),
                                on_click=lambda e: toggle_favorite(e, data),
                            ),
                        ],
                    ),
                ]
            )
        )

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
            tabs_container.visible = not tabs_container.visible
            tabs_container.update()
            
        # Initial Load if empty
        if not places_state["data"]:
            load_places(update_ui=False)
        
        # Refresh favorite status for all items (in case changed in Favorites view)
        # Create a fresh service instance to ensure we have the latest data from disk
        current_fav_service = FavoritesService()
        for p in places_state["data"]:
            p["is_favorite"] = current_fav_service.is_favorite(p.get("place_id"))

        # Calculate initial title based on current state
        initial_title = "Popular in Europe"
        q = places_state.get("query")
        t = places_state.get("type")
        
        if q and t:
            initial_title = f"Popular {t} in {q}"
        elif q:
            initial_title = f"Popular in {q}"
        elif t:
            initial_title = f"Popular {t}"
            
        import string
        initial_title = string.capwords(initial_title)

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
                # Inject generated cards here
                ft.Container(
                    padding=ft.padding.symmetric(horizontal=24),
                    content=ft.Column(
                        ref=places_column_ref,
                        spacing=0, 
                        controls=[build_feature_card(p) for p in places_state["data"]] # Initial render
                    ),
                ),
                ft.Container(
                    ref=load_more_btn_ref,
                    padding=ft.padding.all(24),
                    alignment=ft.alignment.center,
                    visible=bool(places_state["next_page_token"]),
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
        page.views.clear()

        if page.route == "/destination" and selected_place["value"] is not None:
            # Determine back destination based on current nav index
            def on_back(e):
                if current_nav_index["value"] == 1:
                    page.go("/favorites")
                else:
                    page.go("/")

            page.views.append(
                ft.View(
                    "/destination",
                    controls=[build_destination_page(page, selected_place["value"], on_back=on_back)],
                    padding=0,
                    bgcolor="background",
                    navigation_bar=create_navigation_bar(
                        selected_index=current_nav_index["value"],
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
            page.views.append(
                ft.View(
                    "/favorites",
                    controls=[build_favorites_view(page, selected_place)],
                    padding=0,
                    bgcolor="background",
                    navigation_bar=create_navigation_bar(
                        selected_index=1,
                        on_change=handle_nav_change,
                    ),
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

        page.update()

    page.on_route_change = route_change
    page.go(page.route or "/")


if __name__ == "__main__":
    ft.app(target=main)