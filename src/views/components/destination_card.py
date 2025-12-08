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
        
        # State for Related Places
        self.related_places = [] 

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
        self.related_column_ref = ft.Ref[ft.Column]() 
        self.location_column_ref = ft.Ref[ft.Column]() 
        self.title_section_ref = ft.Ref[ft.Column]() 
        
        self.content = ft.SafeArea(content=self._build_layout(), expand=True)
        
    def _normalize_place_data(self, place: dict) -> dict:
        """Ensure consistent keys from different sources (Home vs API)."""
        # Extract Lat/Lng if available in geometry
        geo = place.get("geometry", {}).get("location", {})
        return {
            "place_id": place.get("place_id") or place.get("id"),
            "name": place.get("name") or place.get("title") or "Unknown Place",
            "address": place.get("address") or place.get("formatted_address") or "Unknown Address",
            "rating": place.get("rating", 0.0),
            "user_rating_count": place.get("user_rating_count", 0),
            "description": place.get("description"),
            "photos": place.get("photos", []),
            "reviews": place.get("reviews", []),
            "image_url": place.get("image_url"), 
            "google_maps_url": place.get("google_maps_url"),
            "lat": place.get("lat") or geo.get("lat"),
            "lng": place.get("lng") or geo.get("lng"),
        }

    def did_mount(self):
        self.page_ref.run_task(self._fetch_full_details)

    async def _fetch_full_details(self):
        place_id = self.place.get("place_id")
        if not place_id:
            print("DEBUG: No Place ID found, cannot fetch details.")
            return

        print(f"DEBUG: Fetching details for {place_id}...")
        
        # 1. Fetch details from Google Places API
        try:
            details = await self.api.get_place_details(place_id)
            print(f"DEBUG: API Response Keys: {details.keys()}") # Check if 'reviews' is here
        except Exception as e:
            print(f"DEBUG: API Network Error: {e}")
            return

        if "error" not in details:
            self.place.update(details)
            
            # Debug: Check review count specifically
            revs = self.place.get("reviews", [])
            print(f"DEBUG: Found {len(revs)} reviews.")

            if "location" in details:
                self.place["lat"] = details["location"]["lat"]
                self.place["lng"] = details["location"]["lng"]

            # Update UI components
            self.description_text.value = self.place.get("description") or "Description not available."
            self.description_text.update()
            
            if self.carousel_ref.current:
                self.carousel_ref.current.controls = self._build_carousel_items()
                self.carousel_ref.current.update()
                
            # FORCE UPDATE REVIEWS
            if self.reviews_column_ref.current:
                print("DEBUG: Updating Reviews Column")
                self.reviews_column_ref.current.controls = self._build_review_items()
                self.reviews_column_ref.current.update()

            if self.title_section_ref.current:
                self.title_section_ref.current.controls = self._build_title_section_controls()
                self.title_section_ref.current.update()
            
            if self.location_column_ref.current:
                self.location_column_ref.current.controls = self._build_location_controls()
                self.location_column_ref.current.update()

            await self._fetch_related_places()
        else:
            print(f"DEBUG: API returned error: {details.get('error')}")

        # 4. AI Description Fallback
        if not self.place.get("description") or self.place.get("description") == "Loading description...":
            await self._fetch_ai_description()

    async def _fetch_related_places(self):
        """Fetches real nearby places using the coordinates."""
        lat, lng = self.place.get("lat"), self.place.get("lng")
        if not lat or not lng: return

        res = self.api.search_places(location=f"{lat},{lng}", limit=4)
        
        if res.get("results"):
            # Filter out the current place
            self.related_places = [p for p in res["results"] if p.get("place_id") != self.place.get("place_id")]
            
            if self.related_column_ref.current:
                self.related_column_ref.current.controls = self._build_related_places_items()
                self.related_column_ref.current.update()

    async def _fetch_ai_description(self):
        """Fixes the AI connection using the correct API method."""
        name = self.place.get("name")
        location = self.place.get("address")
        
        prompt = f"Write a 2-sentence inviting description for a tourist destination named {name} located at {location}."
        
        import asyncio
        loop = asyncio.get_event_loop()
        desc = await loop.run_in_executor(None, self.api.get_ai_recommendation, prompt)
        
        if desc:
            self.place["description"] = desc
            self.description_text.value = desc
            self.description_text.update()
        else:
            self.description_text.value = "Overview available in highlights."
            self.description_text.update()

    def _build_layout(self):
        return ft.Column(
            spacing=0, expand=True,
            controls=[
                self._build_header(),
                ft.Container(
                    expand=True,
                    content=ft.ListView(
                        padding=0, spacing=0,
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
                        icon=ft.Icons.ARROW_BACK, icon_color="onBackground",
                        on_click=self.on_back if self.on_back else lambda e: self.page_ref.go("/")
                    ),
                    ft.Text("Details", size=18, weight=ft.FontWeight.W_600, color="onBackground"),
                    ft.IconButton(
                        icon=ft.Icons.FAVORITE if self.place.get("is_favorite") else ft.Icons.FAVORITE_BORDER,
                        icon_color="red" if self.place.get("is_favorite") else "onBackground",
                        on_click=self._toggle_favorite
                    ),
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
            image_urls = ["https://placehold.co/800x600?text=No+Image"]

        images = [
            ft.Container(
                width=300, height=250, border_radius=16, clip_behavior=ft.ClipBehavior.HARD_EDGE,
                content=ft.Image(src=url, fit=ft.ImageFit.COVER, error_content=ft.Container(bgcolor="grey"))
            ) for url in image_urls
        ]
        return [ft.Container(width=16)] + images + [ft.Container(width=16)]

    def _build_image_carousel(self):
        return ft.Container(
            height=250, padding=ft.padding.only(top=16, bottom=16),
            content=ft.Row(
                ref=self.carousel_ref, scroll=ft.ScrollMode.HIDDEN, spacing=12,
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
            padding=ft.padding.symmetric(horizontal=24), margin=ft.margin.only(bottom=16),
            content=ft.Column(ref=self.title_section_ref, spacing=8, controls=self._build_title_section_controls())
        )

    def _build_tabs(self):
        tabs = ft.Tabs(
            selected_index=0, indicator_color="primary", label_color="primary", unselected_label_color="onSurfaceVariant",
            divider_color="transparent", tab_alignment=ft.TabAlignment.CENTER,
            tabs=[
                ft.Tab(text="About", content=self._build_about_tab()),
                ft.Tab(text="Reviews", content=self._build_overview_tab()),
            ],
            expand=True,
        )
        return ft.Container(expand=True, content=tabs)

    def _build_about_tab(self):
        return ft.Container(
            padding=ft.padding.all(24),
            content=ft.Column(
                spacing=24, scroll=ft.ScrollMode.ADAPTIVE,
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

    def _build_location_controls(self):
        lat = self.place.get("lat")
        lng = self.place.get("lng")
        
        if not lat or not lng:
             return [ft.Text("Map data unavailable.", color="grey")]

        # Google Static Maps URL
        map_url = (
            f"https://maps.googleapis.com/maps/api/staticmap?"
            f"center={lat},{lng}&zoom=14&size=600x300&maptype=roadmap"
            f"&markers=color:red%7C{lat},{lng}"
            f"&key={self.api.config.GOOGLE_PLACES_API_KEY}"
        )
        
        # External Directions Link
        google_maps_link = f"https://www.google.com/maps/search/?api=1&query={lat},{lng}"
        if self.place.get("place_id"):
             google_maps_link += f"&query_place_id={self.place.get('place_id')}"

        return [
            ft.Text("Location", size=16, weight=ft.FontWeight.BOLD, color="onBackground"),
            ft.Text(self.place.get("address", ""), size=12, color="onSurfaceVariant"),
            ft.Container(
                height=180, border_radius=16, clip_behavior=ft.ClipBehavior.HARD_EDGE,
                content=ft.Stack([
                    ft.Image(src=map_url, fit=ft.ImageFit.COVER, width=float("inf"), height=180, error_content=ft.Container(bgcolor="#E0E0E0", content=ft.Icon(ft.Icons.BROKEN_IMAGE))),
                    ft.Container(
                        alignment=ft.alignment.bottom_right, padding=10,
                        content=ft.FloatingActionButton(
                            icon=ft.Icons.DIRECTIONS, text="Go", bgcolor="#4CAF50", height=40,
                            on_click=lambda _: self.page_ref.launch_url(google_maps_link)
                        )
                    )
                ])
            )
        ]

    def _build_location_section(self):
        return ft.Column(
            ref=self.location_column_ref,
            spacing=8,
            controls=self._build_location_controls()
        )

    def _build_related_places_items(self):
        if not self.related_places:
            return [ft.Text("Finding nearby places...", italic=True, color="grey")]

        items = []
        for p in self.related_places[:3]: 
            photo_ref = p.get("photos", [{}])[0].get("photo_reference")
            img_url = self.api.get_photo_url(photo_ref, max_width=200) if photo_ref else "https://placehold.co/200x200"

            items.append(
                ft.Container(
                    padding=10, border_radius=12, bgcolor="surface", border=ft.border.all(1, "#E0E0E0"),
                    on_click=lambda e, pl=p: self._navigate_to_related(pl),
                    content=ft.Row(
                        controls=[
                            ft.Container(
                                width=80, height=80, border_radius=12, clip_behavior=ft.ClipBehavior.HARD_EDGE,
                                content=ft.Image(src=img_url, fit=ft.ImageFit.COVER)
                            ),
                            ft.Column(
                                alignment=ft.MainAxisAlignment.CENTER, spacing=4,
                                controls=[
                                    ft.Text(p.get("name"), size=14, weight=ft.FontWeight.W_600, color="onBackground"),
                                    ft.Row([ft.Icon(ft.Icons.STAR, size=12, color="amber"), ft.Text(str(p.get("rating", "N/A")), size=12)])
                                ]
                            )
                        ]
                    )
                )
            )
        return items

    def _navigate_to_related(self, place_data):
        new_view = DestinationView(self.page_ref, place_data, on_back=lambda _: self.page_ref.go("/summary"))
        self.page_ref.views[-1].controls[0] = new_view 
        self.page_ref.update()

    def _build_related_places_section(self):
        return ft.Column(
            spacing=12,
            controls=[
                ft.Text("You might also like", size=16, weight=ft.FontWeight.BOLD, color="onBackground"),
                ft.Column(ref=self.related_column_ref, spacing=12, controls=[ft.ProgressBar(width=100, color="primary")])
            ]
        )

    def _build_overview_tab(self):
        return ft.Container(
            padding=ft.padding.all(24),
            content=ft.Column(
                spacing=24, scroll=ft.ScrollMode.ADAPTIVE,
                controls=[self._build_reviews_section()]
            )
        )

    def _build_review_items(self):
        reviews = self.place.get("reviews", [])
        if not reviews: return [ft.Text("No reviews yet.", color="grey")]
        
        cards = []
        for review in reviews[:3]:
            cards.append(self._build_single_review_card(review))
        
        return [
            ft.Row(
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                controls=[
                    ft.Text(f"Reviews ({self.place.get('user_rating_count', 0)})", size=16, weight=ft.FontWeight.BOLD, color="onBackground"),
                ]
            ),
            *cards
        ]

    def _build_single_review_card(self, review):
        return ft.Container(
            padding=16, border_radius=12, border=ft.border.all(1, "#E0E0E0"),
            content=ft.Column(
                spacing=8,
                controls=[
                    ft.Row(
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                        controls=[
                            ft.Row([
                                ft.CircleAvatar(radius=16, foreground_image_src=review.get("author_photo", "")),
                                ft.Text(review.get("author_name", "Anonymous"), weight=ft.FontWeight.BOLD, size=13, color="onBackground")
                            ]),
                            ft.Row([ft.Icon(ft.Icons.STAR, size=12, color="amber"), ft.Text(f"{review.get('rating')}", size=11, weight=ft.FontWeight.BOLD)])
                        ]
                    ),
                    ft.Text(review.get("text", ""), size=13, color="onSurfaceVariant"),
                    ft.Text(review.get("relative_time", ""), size=11, color="grey")
                ]
            )
        )

    def _build_reviews_section(self):
        return ft.Column(ref=self.reviews_column_ref, spacing=12, controls=self._build_review_items())