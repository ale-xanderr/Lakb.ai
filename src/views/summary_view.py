import flet as ft

def build_summary_view(page: ft.Page, on_back=None) -> ft.Control:
    """
    Display the full itinerary summary with tabs (Summary | Itinerary | Tips).
    """
    plan = page.session.get("ai_result") or {}
    summary = plan.get("summary_preview", {})
    itinerary = plan.get("itinerary", [])
    tips = plan.get("tips", [])
    
    def handle_back(e):
        if on_back:
            on_back(e)
        else:
            page.go("/plan")
    
    # Tab 1: Summary
    summary_tab = ft.Tab(
        text="Summary",
        content=ft.Container(
            padding=15,
            content=ft.Column([
                ft.Text(summary.get("destination_header", "Unknown"), size=22, weight="bold", color="onBackground"),
                ft.Text(summary.get("sub_header", ""), size=12, color="onSurfaceVariant"),
                ft.Container(height=15),
                
                ft.Row([ft.Icon(ft.Icons.CALENDAR_TODAY, color="primary", size=16), ft.Text(f"Dates: {summary.get('dates', '')}")], spacing=8),
                ft.Row([ft.Icon(ft.Icons.ATTACH_MONEY, color="primary", size=16), ft.Text(f"Budget: {summary.get('budget_range', '')}")], spacing=8),
                ft.Row([ft.Icon(ft.Icons.DIRECTIONS_RUN, color="primary", size=16), ft.Text(f"Style: {summary.get('travel_style', '')}")], spacing=8),
                ft.Row([ft.Icon(ft.Icons.FAVORITE, color="primary", size=16), ft.Text(f"Activities: {summary.get('activities', '')}")], spacing=8),
                ft.Row([ft.Icon(ft.Icons.ACCESS_TIME, color="primary", size=16), ft.Text(f"Time: {summary.get('time_preference', '')}")], spacing=8),
                ft.Row([ft.Icon(ft.Icons.RESTAURANT, color="primary", size=16), ft.Text(f"Diet: {summary.get('dietary_preferences', '')}")], spacing=8),
            ])
        )
    )
    
    # Tab 2: Itinerary
    itinerary_controls = []
    max_days_display = min(7, len(itinerary))  # limit number of days shown
    
    for day in itinerary[:max_days_display]:
        day_card_controls = []
        for place in day.get("places", [])[:5]:  # limit places per day
            
            # --- INTEGRATION START ---
            def on_place_click(e, p=place):
                # Lazy import to avoid circular dependency issues at the top level
                from views.components.destination_card import DestinationView 
                
                # Logic to handle the "Back" button inside the DestinationView
                def return_to_summary(e):
                    page.views.pop() # Remove the destination view
                    page.go("/summary") # Force refresh/ensure we are on summary
                
                # Create the DestinationView with the specific place data
                dest_view = DestinationView(
                    page, 
                    place=p, 
                    on_back=return_to_summary
                )
                
                # Push a new View onto the stack overlaying the current one
                page.views.append(
                    ft.View(
                        "/destination",
                        controls=[dest_view],
                        padding=0,
                        bgcolor="background"
                    )
                )
                page.update()
            # --- INTEGRATION END ---

            row = ft.Row(
                controls=[
                    ft.Icon(ft.Icons.PLACE, size=16, color="primary"),
                    ft.Column([
                        ft.Text(place.get("name", ""), size=12, weight="w500", color="onBackground"),
                        ft.Text(f"★ {place.get('rating', 'N/A')}", size=10, color="onSurfaceVariant"),
                    ], spacing=2, expand=True),
                ],
                spacing=10,
                on_click=on_place_click # Hook up the new click handler
            )
            day_card_controls.append(row)

        day_card = ft.Container(
            bgcolor="surface",
            border_radius=8,
            padding=12,
            margin=ft.margin.symmetric(vertical=8),
            content=ft.Column([
                ft.Text(day.get("day_label", ""), size=14, weight="bold", color="primary"),
                ft.Text(day.get("date", ""), size=11, color="onSurfaceVariant"),
                ft.Container(height=8),
                *day_card_controls
            ], spacing=8)
        )
        itinerary_controls.append(day_card)
            
    itinerary_tab = ft.Tab(
        text="Itinerary",
        content=ft.Container(
            padding=15,
            content=ft.Column(itinerary_controls if itinerary_controls else [ft.Text("No itinerary available")])
        )
    )
    
    # Tab 3: Tips
    tips_controls = [
        ft.Row([
            ft.Icon(ft.Icons.LIGHTBULB, size=16, color="primary"),
            ft.Text(tip, size=12, color="onBackground")
        ], spacing=10)
        for tip in tips
    ]
    
    tips_tab = ft.Tab(
        text="Tips",
        content=ft.Container(
            padding=15,
            content=ft.Column(tips_controls if tips_controls else [ft.Text("No tips available")])
        )
    )
    
    return ft.Column(
        expand=True,
        spacing=0,
        controls=[
            ft.Container(
                padding=20,
                content=ft.Row([
                    ft.IconButton(ft.Icons.ARROW_BACK, on_click=handle_back),
                    ft.Text("Plan Summary", size=20, weight="bold", expand=True),
                ], vertical_alignment=ft.CrossAxisAlignment.CENTER)
            ),
            ft.Divider(height=1),
            ft.Container(
                expand=True,
                content=ft.Tabs(
                    selected_index=0,
                    tabs=[summary_tab, itinerary_tab, tips_tab]
                )
            ),
        ]
    )