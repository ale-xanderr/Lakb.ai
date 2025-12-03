import flet as ft
from .components.nav_bar import create_navigation_bar
from .components.destination_card import build_destination_page
from .settings_view import build_settings_content
from .favorites_view import build_favorites_view
from .app_config import configure_page
from data.mock_data import PLACES_DATA


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
        ),
        font_family="Poppins",
    )

    # Dark Theme
    page.dark_theme = ft.Theme(
        color_scheme=ft.ColorScheme(
            background="#010403",
            on_background="#e4f6ef",
            primary="#42b889",
            secondary="#265c69",
            tertiary="#315c87",
            surface="#020608",
            on_surface="#e4f6ef",
        ),
        font_family="Poppins",
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

    # --- MOCK API DATA (Placeholder for your future API call) ---
    # You will eventually replace this list with data fetched from your backend
    mock_places_data = PLACES_DATA

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

    def build_search_bar():
        return ft.Container(
            bgcolor="surface", # Use Surface for search bar (White in Light, Dark in Dark)
            border_radius=30,
            padding=ft.padding.symmetric(horizontal=20, vertical=8),
            shadow=ft.BoxShadow(blur_radius=10, color=ft.Colors.with_opacity(0.05, ft.Colors.BLACK)),
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
                    ),
                    ft.Icon(ft.Icons.TUNE, color="onBackground", size=24)
                ]
            )
        )

    # State for category tabs
    selected_category = {"value": "Hotel"}

    def build_category_tabs():
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
        
        # Initial population
        update_tabs()
        return tabs_row

    # 4. Feature Card (Updated layout: image, title + address, heart button)
    def build_feature_card(data):
        # Image Logic: Check if URL exists, otherwise show placeholder Icon
        image_content = None
        if data["image_url"]:
            image_content = ft.Image(
                src=data["image_url"],
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
            selected_place["value"] = data
            page.go("/destination")

        def toggle_favorite(e, item):
            item["is_favorite"] = not item.get("is_favorite", False)
            e.control.icon = ft.Icons.FAVORITE if item["is_favorite"] else ft.Icons.FAVORITE_BORDER
            e.control.icon_color = "red" if item["is_favorite"] else "primary"
            e.control.update()

        # Note: Feature cards seem to be designed with a dark background always (white text).
        # We will use a fixed dark color or Surface if it matches.
        # Given the original code used a very dark color in both modes, we'll stick to a dark color.
        card_bg = "#020608" 

        return ft.Container(
            bgcolor=card_bg,
            border_radius=24,
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
                                controls=[
                                    ft.Text(
                                        data["title"],
                                        color="#FFFFFF", # Always white on dark card
                                        size=18,
                                        weight=ft.FontWeight.BOLD,
                                    ),
                                    ft.Text(
                                        data.get("address", ""),
                                        color="#B0B0B0",
                                        size=11,
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
        place_cards = [build_feature_card(item) for item in mock_places_data]

        content_scroll = ft.Column(
            scroll=ft.ScrollMode.HIDDEN,
            expand=True,
            spacing=0,
            controls=[
                ft.Container(height=10),
                ft.Container(padding=ft.padding.symmetric(horizontal=24), content=build_header()),
                ft.Container(height=25),
                ft.Container(padding=ft.padding.symmetric(horizontal=24), content=build_search_bar()),
                ft.Container(height=25),
                ft.Container(padding=ft.padding.only(left=24), content=build_category_tabs()),
                ft.Container(height=30),
                ft.Container(
                    padding=ft.padding.symmetric(horizontal=24),
                    content=ft.Text("Popular in Europe", font_family="Courgette", size=24, color="onBackground"),
                ),
                ft.Container(height=15),
                # Inject generated cards here
                ft.Container(
                    padding=ft.padding.symmetric(horizontal=24),
                    content=ft.Column(spacing=0, controls=place_cards),
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