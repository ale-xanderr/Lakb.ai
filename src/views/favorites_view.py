import flet as ft
from .components.nav_bar import create_navigation_bar
from data.mock_data import PLACES_DATA

def build_favorites_view(page: ft.Page, selected_place_state: dict) -> ft.Control:
    # --- MOCK DATA (Duplicated from home_view for now) ---
    # --- MOCK DATA (Duplicated from home_view for now) ---
    mock_places_data = [p for p in PLACES_DATA if p.get("is_favorite")]

    def dummy_click(e):
        pass

    # --- Feature Card Builder (Adapted for Grid) ---
    def build_feature_card(data):
        # Image Logic
        image_content = None
        if data["image_url"]:
            image_content = ft.Image(
                src=data["image_url"],
                fit=ft.ImageFit.COVER,
                width=float("inf"),
                height=float("inf"),
            )
        else:
            image_content = ft.Column(
                alignment=ft.MainAxisAlignment.CENTER,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                controls=[
                    ft.Icon(ft.Icons.IMAGE_NOT_SUPPORTED_OUTLINED, color="#B0B0B0", size=40),
                    ft.Text("No Image", color="#B0B0B0", size=12)
                ]
            )

        def on_card_click(e):
            selected_place_state["value"] = data
            page.go("/destination")

        def toggle_favorite(e, item):
            item["is_favorite"] = not item.get("is_favorite", False)
            e.control.icon = ft.Icons.FAVORITE if item["is_favorite"] else ft.Icons.FAVORITE_BORDER
            e.control.icon_color = "red" if item["is_favorite"] else "primary"
            e.control.update()

        card_bg = "#020608"

        return ft.Container(
            bgcolor=card_bg,
            border_radius=24,
            padding=12,
            on_click=on_card_click,
            content=ft.Column(
                spacing=6,
                controls=[
                    # Image Container
                    ft.Container(
                        height=120, # Slightly smaller for grid
                        border_radius=18,
                        bgcolor="#2A2A2A",
                        clip_behavior=ft.ClipBehavior.HARD_EDGE,
                        content=image_content,
                    ),
                    ft.Container(height=4),
                    # Title + Address + Heart button
                    ft.Row(
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                        vertical_alignment=ft.CrossAxisAlignment.CENTER,
                        controls=[
                            ft.Column(
                                spacing=2,
                                alignment=ft.MainAxisAlignment.CENTER,
                                expand=True, # Allow text to take available space
                                controls=[
                                    ft.Text(
                                        data["title"],
                                        color="#FFFFFF",
                                        size=16, # Slightly smaller
                                        weight=ft.FontWeight.BOLD,
                                        no_wrap=True,
                                        overflow=ft.TextOverflow.ELLIPSIS,
                                    ),
                                    ft.Text(
                                        data.get("address", ""),
                                        color="#B0B0B0",
                                        size=10, # Slightly smaller
                                        no_wrap=True,
                                        overflow=ft.TextOverflow.ELLIPSIS,
                                    ),
                                ],
                            ),
                            ft.IconButton(
                                icon=ft.Icons.FAVORITE if data.get("is_favorite") else ft.Icons.FAVORITE_BORDER,
                                icon_color="red" if data.get("is_favorite") else "primary",
                                bgcolor="background",
                                icon_size=20,
                                style=ft.ButtonStyle(
                                    shape={
                                        ft.ControlState.DEFAULT: ft.RoundedRectangleBorder(
                                            radius=9999
                                        )
                                    },
                                    padding=8,
                                ),
                                on_click=lambda e: toggle_favorite(e, data),
                            ),
                        ],
                    ),
                ]
            )
        )

    # Generate cards
    cards = [build_feature_card(item) for item in mock_places_data]

    # Grid Layout
    grid = ft.GridView(
        expand=True,
        runs_count=2,
        max_extent=300, # Adjust as needed
        child_aspect_ratio=0.85, # Adjust card height/width ratio
        spacing=16,
        run_spacing=16,
        padding=24,
        controls=cards,
    )

    return ft.SafeArea(
        expand=True,
        content=ft.Column(
            expand=True,
            spacing=0,
            controls=[
                ft.Container(
                    padding=ft.padding.only(left=24, right=24, top=10, bottom=10),
                    content=ft.Text("Favorites", size=28, weight=ft.FontWeight.BOLD, color="onBackground"),
                ),
                ft.Container(
                    expand=True,
                    content=grid
                )
            ]
        )
    )
