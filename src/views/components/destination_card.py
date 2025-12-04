import flet as ft
import asyncio
from services.api_service import APIService
from services.favorites_service import FavoritesService

class DestinationView(ft.Container):
    def __init__(self, page: ft.Page, place: dict, on_back=None):
        super().__init__(expand=True, bgcolor="background")
        self.page_ref = page
        # Normalize initial data
        self.place = self._normalize_place_data(place)
        self.on_back = on_back
        self.api = APIService()
        self.favorites_service = FavoritesService()
        
        # Check initial favorite status
        self.place["is_favorite"] = self.favorites_service.is_favorite(self.place["place_id"])
        
        # UI References for updates
        self.description_text = ft.Text(
            value=self.place.get("description") or "Loading description...",
            size=14,
            color="onSurfaceVariant",
            height=1.5,
        )
        self.carousel_ref = ft.Ref[ft.Row]()
        self.reviews_column_ref = ft.Ref[ft.Column]()
        self.highlights_grid_ref = ft.Ref[ft.GridView]()
        self.title_section_ref = ft.Ref[ft.Column]() # Ref for title section
        
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
        }

    def did_mount(self):
        self.page_ref.run_task(self._fetch_full_details)

    async def _fetch_full_details(self):
        place_id = self.place.get("place_id")
        if not place_id:
            return

        # 1. Fetch details from Google Places API
        details = await self.api.get_place_details(place_id)
        
        if "error" not in details:
            # Update state with new details
            self.place.update(details)
            
            # Update UI components
            self.description_text.value = self.place.get("description") or "Description not available."
            if self.description_text.page:
                self.description_text.update()
            
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

        # 2. If description is still missing, generate it
        if not self.place.get("description"):
            await self._fetch_ai_description()

    async def _fetch_ai_description(self):
        name = self.place.get("name")
        location = self.place.get("address")
        
        self.description_text.value = "Generating description..."
        self.description_text.update()
        
        res = await self.api.generate_place_description(name, location)
        
        if "choices" in res:
            desc = res["choices"][0]["message"]["content"]
            self.place["description"] = desc
            self.description_text.value = desc
            if self.description_text.page:
                self.description_text.update()
        elif "error" in res:
            self.description_text.value = "Could not load description."
            if self.description_text.page:
                self.description_text.update()

    def _build_layout(self):
        return ft.Column(
            spacing=0,
            expand=True,
            controls=[
                self._build_header(),
                ft.Container(
                    expand=True,
                    content=ft.ListView(
                        padding=0,
                        spacing=0,
                        controls=[
                            self._build_image_carousel(),
                            self._build_title_section(),
                            self._build_tabs(),
                        ]
                    )
                )
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
                    ft.Row(
                        spacing=0,
                        controls=[
                            ft.IconButton(
                                icon=ft.Icons.FAVORITE if self.place.get("is_favorite") else ft.Icons.FAVORITE_BORDER,
                                icon_color="red" if self.place.get("is_favorite") else "onBackground",
                                on_click=self._toggle_favorite
                            ),
                            ft.IconButton(icon=ft.Icons.SHARE_OUTLINED, icon_color="onBackground"),
                            ft.IconButton(icon=ft.Icons.MORE_VERT, icon_color="onBackground"),
                        ]
                    )
                ]
            )
        )

    def _toggle_favorite(self, e):
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
                controls=[
                    ft.Icon(ft.Icons.LOCATION_ON, color="primary", size=16),
                    ft.Text(address, color="onSurfaceVariant", size=12, no_wrap=True, overflow=ft.TextOverflow.ELLIPSIS),
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
            expand=True,
        )
        return ft.Container(
            expand=True, # Allow tabs to take remaining space
            content=tabs
        )

    def _build_about_tab(self):
        return ft.Container(
            padding=ft.padding.all(24),
            content=ft.Column(
                spacing=24,
                scroll=ft.ScrollMode.ADAPTIVE,
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
            ]
        )

    def _build_location_section(self):
        # Placeholder for map
        return ft.Column(
            spacing=8,
            controls=[
                ft.Text("Location", size=16, weight=ft.FontWeight.BOLD, color="onBackground"),
                ft.Text(self.place.get("address", ""), size=12, color="onSurfaceVariant"),
                ft.Container(
                    height=150,
                    border_radius=16,
                    bgcolor="#E0E0E0",
                    alignment=ft.alignment.center,
                    content=ft.Column(
                        alignment=ft.MainAxisAlignment.CENTER,
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                        controls=[
                            ft.Icon(ft.Icons.MAP, size=40, color="grey"),
                            ft.Text("Map View", color="grey")
                        ]
                    )
                )
            ]
        )

    def _build_related_places_section(self):
        # Mock related places
        related = [
            {"name": "Sunny Beach", "img": "https://picsum.photos/200/200?1", "dist": "2.5 km"},
            {"name": "Mountain Peak", "img": "https://picsum.photos/200/200?2", "dist": "4.0 km"},
            {"name": "City Park", "img": "https://picsum.photos/200/200?3", "dist": "1.2 km"},
        ]
        
        items = []
        for item in related:
            items.append(
                ft.Container(
                    padding=10,
                    border_radius=12,
                    bgcolor="surface",
                    border=ft.border.all(1, "#E0E0E0"),
                    content=ft.Row(
                        controls=[
                            ft.Container(
                                width=80,
                                height=80,
                                border_radius=12,
                                clip_behavior=ft.ClipBehavior.HARD_EDGE,
                                content=ft.Image(src=item["img"], fit=ft.ImageFit.COVER)
                            ),
                            ft.Column(
                                alignment=ft.MainAxisAlignment.CENTER,
                                spacing=4,
                                controls=[
                                    ft.Text(item["name"], size=14, weight=ft.FontWeight.W_600, color="onBackground"),
                                    ft.Text(f"Distance: {item.get('dist', 'N/A')}", size=12, color="onSurfaceVariant"),
                                ]
                            )
                        ]
                    )
                )
            )

        return ft.Column(
            spacing=12,
            controls=[
                ft.Text("Related Places", size=16, weight=ft.FontWeight.BOLD, color="onBackground"),
                ft.Column(spacing=12, controls=items)
            ]
        )

    def _build_overview_tab(self):
        return ft.Container(
            padding=ft.padding.all(24),
            content=ft.Column(
                spacing=24,
                scroll=ft.ScrollMode.ADAPTIVE,
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

def build_destination_page(page: ft.Page, place: dict, on_back=None) -> ft.Control:
    """
    Entry point for the destination page.
    Returns a DestinationView control.
    """
    return DestinationView(page, place, on_back)
