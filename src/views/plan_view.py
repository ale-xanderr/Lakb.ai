import flet as ft
from services.ai_engine import AIEngine
from services.api_service import APIService
from services.db_manager import DBManager

class PlanView:
    def __init__(self, page: ft.Page):
        self.page = page
        self.api_service = APIService()
        self.db_manager = DBManager()
        self.engine = AIEngine(self.api_service, self.db_manager)
        
        # --- STATE ---
        self.saved_plans = self.page.client_storage.get("user_plans") or []
        self.view_mode = "list" if self.saved_plans else "empty"
        self.generated_plan = None
        
        self.container = ft.Container(
            expand=True,
            padding=ft.padding.symmetric(horizontal=24, vertical=20)
        )

        # --- FORM FIELDS ---
        self.destination = ft.TextField(label="Destination", hint_text="e.g., Camarines Sur", bgcolor="surface", border_radius=8, border="none")
        self.duration = ft.TextField(label="Duration (Days)", value="3", keyboard_type=ft.KeyboardType.NUMBER, bgcolor="surface", border_radius=8, border="none")
        self.budget_min = ft.TextField(label="Min", value="1000", keyboard_type=ft.KeyboardType.NUMBER, bgcolor="surface", border_radius=8, border="none", expand=True)
        self.budget_max = ft.TextField(label="Max", value="10000", keyboard_type=ft.KeyboardType.NUMBER, bgcolor="surface", border_radius=8, border="none", expand=True)
        self.travel_style = ft.TextField(label="Travel Style", hint_text="e.g. Adventure", bgcolor="surface", border_radius=8, border="none")
        self.activities = ft.TextField(label="Activities", hint_text="e.g. Hiking", bgcolor="surface", border_radius=8, border="none")
        self.dietary = ft.TextField(label="Dietary", hint_text="e.g. None", bgcolor="surface", border_radius=8, border="none")
        self.time_pref = ft.Dropdown(label="Time Preference", options=[ft.dropdown.Option("Morning"), ft.dropdown.Option("Afternoon"), ft.dropdown.Option("All Day")], value="Morning", bgcolor="surface", border_radius=8)

        self.update_view()

    def update_view(self):
        # FIX: Aggressively remove floating button to prevent persistence
        self.page.floating_action_button = None
        self.container.content = None
        
        if self.view_mode == "empty":
            self.container.content = self._build_empty_state()
        elif self.view_mode == "list":
            self.container.content = self._build_list_state()
        elif self.view_mode == "form":
            self.container.content = self._build_form()
        elif self.view_mode == "generated":
            self.container.content = self._build_generated_state(self.generated_plan or {})

        try:
            self.container.update()
            self.page.update()
        except Exception: pass

    def _build_empty_state(self):
        return ft.Column(
            expand=True,
            alignment=ft.MainAxisAlignment.CENTER,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            controls=[
                ft.Icon(ft.Icons.NOTE_ADD_OUTLINED, size=80, color="primary"),
                ft.Text("No Plan Created Yet", size=20, weight="bold"),
                ft.Text("Create your first travel plan", size=14, color="grey"),
                ft.Container(height=30),
                ft.ElevatedButton("Create Plan", width=200, height=50, bgcolor="#4CAF50", color="white", on_click=self._on_create_plan_click)
            ]
        )

    # --- VIEW 2: LIST STATE ---
    def _build_list_state(self):
        grid = ft.GridView(expand=True, runs_count=2, max_extent=250, child_aspect_ratio=0.75, spacing=10, run_spacing=10)

        for plan in self.saved_plans:
            summary = plan.get("summary_preview", {})
            img_src = plan.get("image_url") or "https://placehold.co/600x400?text=No+Image"
            
            card_content = ft.Container(
                bgcolor="surfaceVariant",
                border_radius=15,
                clip_behavior=ft.ClipBehavior.HARD_EDGE,
                on_click=lambda e, p=plan: self._on_plan_click(p),
                content=ft.Column([
                    ft.Stack(controls=[
                        ft.Image(src=img_src, height=120, width=float("inf"), fit=ft.ImageFit.COVER),
                        ft.Container(
                            alignment=ft.alignment.top_right,
                            padding=ft.padding.all(8),
                            content=ft.IconButton(
                                icon=ft.Icons.DELETE_OUTLINE, icon_color="red",
                                on_click=lambda e, p=plan: self._delete_plan(e, p)
                            )
                        )
                    ]),
                    ft.Container(
                        padding=10,
                        content=ft.Column([
                            ft.Text(summary.get("destination_header", "Unknown"), weight="bold", size=16, no_wrap=True),
                            ft.Text(summary.get("dates", ""), size=12, color="onSurfaceVariant"),
                            ft.Container(height=5),
                            ft.Row([ft.Icon(ft.Icons.DIRECTIONS_RUN, size=12, color="primary"), ft.Text(summary.get("travel_style", "General"), size=10)], spacing=5)
                        ])
                    )
                ], spacing=0)
            )
            grid.controls.append(card_content)

        return ft.Column([
            ft.Row([
                ft.Text("My Plans", size=24, weight="bold"),
                ft.IconButton(ft.Icons.ADD, icon_color="#4CAF50", on_click=self._on_create_plan_click)
            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
            ft.Container(height=10),
            grid
        ], expand=True)

    def _build_form(self):
         return ft.Column(
            scroll=ft.ScrollMode.HIDDEN,
            controls=[
                ft.Row([ft.IconButton(ft.Icons.ARROW_BACK, on_click=self._on_back_to_list), ft.Text("Plan Your Trip", size=24, weight="bold")]),
                ft.Container(height=10),
                ft.Text("Destination"), self.destination, ft.Container(height=10),
                ft.Text("Duration (Days)"), self.duration, ft.Container(height=10),
                ft.Text("Budget Range (PHP)"), ft.Row([self.budget_min, self.budget_max], spacing=10), ft.Container(height=10),
                ft.Text("Travel Style"), self.travel_style, ft.Container(height=10),
                ft.Text("Activity Preferences"), self.activities, ft.Container(height=10),
                ft.Text("Time Preference"), self.time_pref, ft.Container(height=10),
                ft.Text("Dietary Restrictions"), self.dietary, ft.Container(height=20),
                ft.Row([ft.ElevatedButton("Generate Plan", width=200, bgcolor="#4CAF50", color="white", on_click=self._handle_generate)], alignment=ft.MainAxisAlignment.CENTER),
                ft.Container(height=50)
            ]
        )

    def _build_generated_state(self, plan):
        summary = plan.get("summary_preview", {})
        itinerary = plan.get("itinerary", [])
        tips = plan.get("tips") or summary.get("ai_tips") or []
        img_src = plan.get("image_url") or "https://placehold.co/600x400?text=No+Image"
        
        # Tab 1: Summary
        summary_tab = ft.Container(
            padding=20,
            content=ft.Column([
                ft.Text(summary.get("destination_header", ""), size=22, weight="bold"),
                ft.Text(summary.get("ai_insight", "Enjoy your trip!"), italic=True, size=14, color="grey"),
                ft.Divider(),
                self._row_icon(ft.Icons.CALENDAR_MONTH, f"Dates: {summary.get('dates')}"),
                self._row_icon(ft.Icons.MONEY, f"Budget: {summary.get('budget_range')}"),
                self._row_icon(ft.Icons.DIRECTIONS_RUN, f"Style: {summary.get('travel_style')}"),
            ], scroll=ft.ScrollMode.HIDDEN)
        )

        # Tab 2: Itinerary
        itinerary_column = ft.Column(spacing=20, scroll=ft.ScrollMode.HIDDEN)
        for day in itinerary:
            day_places = ft.Column(spacing=10)
            for place in day["places"]:
                day_places.controls.append(
                    ft.Container(
                        bgcolor="surfaceVariant", padding=10, border_radius=8,
                        content=ft.Row([
                            ft.Icon(ft.Icons.PLACE, color="#4CAF50"),
                            ft.Column([
                                ft.Text(place["name"], weight="bold"),
                                ft.Text(place.get("description", "No description"), size=12, italic=True),
                                ft.Text(place["address"] or "Nearby", size=10, color="grey")
                            ])
                        ])
                    )
                )
            itinerary_column.controls.append(ft.Column([ft.Text(f"{day['day_label']}", color="#4CAF50", weight="bold"), day_places]))
        
        itinerary_tab = ft.Container(padding=10, content=itinerary_column)

        # Tab 3: Tips
        tips_view = ft.Column(spacing=10, scroll=ft.ScrollMode.HIDDEN)
        for t in tips:
            tips_view.controls.append(ft.Row([ft.Icon(ft.Icons.LIGHTBULB, size=16, color="yellow"), ft.Text(t, size=14)]))
        tips_tab = ft.Container(padding=20, content=tips_view)

        return ft.Column(
            expand=True,
            controls=[
                ft.Row([ft.IconButton(ft.Icons.ARROW_BACK, on_click=self._on_back_to_list), ft.Text("Plan Summary", size=20, weight="bold")]),
                ft.Container(height=200, border_radius=15, clip_behavior=ft.ClipBehavior.HARD_EDGE, content=ft.Image(src=img_src, fit=ft.ImageFit.COVER, width=float("inf"))),
                ft.Tabs(selected_index=0, tabs=[ft.Tab(text="Summary", content=summary_tab), ft.Tab(text="Itinerary", content=itinerary_tab), ft.Tab(text="Tips", content=tips_tab)], expand=True),
                # REMOVED: Save & Close button
            ]
        )

    def _row_icon(self, icon, text):
        return ft.Row([ft.Icon(icon, size=16, color="#4CAF50"), ft.Text(text, size=14)])

    def _on_create_plan_click(self, e):
        self.view_mode = "form"
        self.update_view()

    def _on_back_to_list(self, e):
        self.saved_plans = self.page.client_storage.get("user_plans") or []
        self.view_mode = "list" if self.saved_plans else "empty"
        self.update_view()

    def _on_plan_click(self, plan):
        self.generated_plan = plan
        self.page.session.set("ai_result", plan)
        self.view_mode = "generated"
        self.page.floating_action_button = None 
        self.update_view()

    def _delete_plan(self, e, plan):
        try:
            self.saved_plans = [p for p in self.saved_plans if p is not plan]
            self.page.client_storage.set("user_plans", self.saved_plans)
            self.view_mode = "list" if self.saved_plans else "empty"
            self.update_view()
        except: pass

    def _handle_generate(self, e):
        if not self.destination.value: return
        self.page.splash = ft.ProgressBar(color="#4CAF50")
        self.page.update()

        try:
            budget = f"PHP {self.budget_min.value}-{self.budget_max.value}"
            plan = self.engine.generate_trip_plan(
                location=self.destination.value,
                duration_days=int(self.duration.value),
                budget_range=budget,
                travel_style=self.travel_style.value,
                activity_preferences=self.activities.value,
                time_preference=self.time_pref.value,
                dietary_restrictions=self.dietary.value
            )
            
            # Fetch Image
            img_url = None
            try:
                res = self.api_service.search_places(query=f"tourist attractions {self.destination.value}", limit=1)
                if res.get("results") and res["results"][0].get("photos"):
                    ref = res["results"][0]["photos"][0]["photo_reference"]
                    img_url = self.api_service.get_photo_url(ref, max_width=600)
            except Exception: pass
            plan["image_url"] = img_url

            self.saved_plans.insert(0, plan)
            self.page.client_storage.set("user_plans", self.saved_plans)
            self.generated_plan = plan
            self.view_mode = "generated"

        except Exception as ex:
            self.page.snack_bar = ft.SnackBar(ft.Text(f"Error: {ex}"))
            self.page.snack_bar.open = True
            self.page.update()

        self.page.splash = None
        self.update_view()

    def get_control(self):
        return self.container