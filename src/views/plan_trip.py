import flet as ft
import datetime
from services.ai_engine import AIEngine
from core.supabase_client import get_supabase_client

def build_plan_trip_view(page: ft.Page, on_back) -> tuple[ft.Control, list]:
    # Colors - Use Flet theme tokens
    BG_COLOR = "background"
    CARD_BG = "surface"
    ACCENT_GREEN = "primary"
    BORDER_DEFAULT = "secondary"
    LABEL_COLOR = "onSurfaceVariant"
    TEXT_COLOR = "onSurface"
    CHIP_BG_SELECTED = ft.Colors.with_opacity(0.15, "primary")

    state = {"step": 1}

    # --- Date Pickers ---
    date_from = ft.DatePicker(first_date=datetime.datetime.now())
    date_to = ft.DatePicker(first_date=datetime.datetime.now())

    def update_date_display():
        start_str = date_from.value.strftime("%b %d, %Y") if date_from.value else "Select start date"
        end_str = date_to.value.strftime("%b %d, %Y") if date_to.value else "End date"
        date_btn.content.controls[1].value = f"{start_str}  →  {end_str}"
        try:
            date_btn.update()
        except Exception:
            pass

    def on_date_from_change(e):
        update_date_display()
        if date_from.value:
            if not date_to.value or date_to.value < date_from.value:
                date_to.value = date_from.value
            try:
                page.open(date_to)
            except Exception:
                pass

    def on_date_to_change(e):
        update_date_display()

    date_from.on_change = on_date_from_change
    date_to.on_change = on_date_to_change

    def open_date_picker(e):
        # Open date_from, which then natively chains into opening date_to
        try:
            page.open(date_from)
        except Exception:
            pass

    date_btn = ft.Container(
        content=ft.Row([
            ft.Icon(ft.Icons.CALENDAR_MONTH, color=ACCENT_GREEN, size=20),
            ft.Text("Select start date  →  End date", size=13, color=TEXT_COLOR)
        ]),
        border=ft.border.all(1, BORDER_DEFAULT),
        border_radius=12,
        bgcolor=CARD_BG,
        padding=14,
        on_click=open_date_picker,
        ink=True,
        width=float("inf"),
        height=52
    )

    # --- Step 1 Controls ---
    destination_input = ft.TextField(
        value="Camarines Sur",
        text_size=13,
        color=TEXT_COLOR,
        border_color=BORDER_DEFAULT,
        border_width=1,
        border_radius=12,
        bgcolor=CARD_BG,
        focused_border_color=ACCENT_GREEN,
        focused_border_width=1,
        suffix_icon=ft.Icons.EDIT,
        content_padding=14,
        height=52,
    )

    # Destination Preview Card
    destination_preview_card = ft.Container(
        bgcolor=CARD_BG,
        border_radius=16,
        padding=16,
        width=float("inf"),
        content=ft.Row([
            ft.Icon(ft.Icons.LOCATION_ON, color=ACCENT_GREEN, size=24),
            ft.Column([
                ft.Text("Camarines Sur", color=TEXT_COLOR, size=15, weight=ft.FontWeight.W_500),
                ft.Text("Tap to change destination", color=LABEL_COLOR, size=12)
            ], spacing=2)
        ], spacing=12),
        on_click=lambda e: destination_input.focus(),
        ink=True
    )

    def update_preview_card(e=None):
        destination_preview_card.content.controls[1].controls[0].value = destination_input.value or "Where to?"
        destination_preview_card.update()

    destination_input.on_change = update_preview_card

    # --- Step 2 Controls ---
    budget_min = ft.TextField(
        hint_text="e.g. 1,000",
        text_size=13,
        color=TEXT_COLOR,
        border_color=BORDER_DEFAULT,
        border_width=1,
        border_radius=12,
        bgcolor=CARD_BG,
        focused_border_color=ACCENT_GREEN,
        focused_border_width=1,
        content_padding=14,
        keyboard_type=ft.KeyboardType.NUMBER,
        height=52
    )
    
    budget_max = ft.TextField(
        hint_text="e.g. 5,000",
        text_size=13,
        color=TEXT_COLOR,
        border_color=BORDER_DEFAULT,
        border_width=1,
        border_radius=12,
        bgcolor=CARD_BG,
        focused_border_color=ACCENT_GREEN,
        focused_border_width=1,
        content_padding=14,
        keyboard_type=ft.KeyboardType.NUMBER,
        height=52
    )

    budget_row = ft.Row([
        ft.Column([ft.Text("Min", size=11, color=LABEL_COLOR), budget_min], expand=True, spacing=8),
        ft.Column([ft.Text("Max", size=11, color=LABEL_COLOR), budget_max], expand=True, spacing=8),
    ], spacing=12, width=float("inf"))

    travel_style_input = ft.Dropdown(
        hint_text="e.g. Adventure, Relaxed, Cultural…",
        options=[
            ft.dropdown.Option("Adventure"),
            ft.dropdown.Option("Luxury"),
            ft.dropdown.Option("Slow Travel"),
            ft.dropdown.Option("Backpacking"),
            ft.dropdown.Option("Cultural"),
            ft.dropdown.Option("Solo"),
            ft.dropdown.Option("Family"),
        ],
        text_size=13,
        color=TEXT_COLOR,
        border_color=BORDER_DEFAULT,
        border_width=1,
        border_radius=12,
        bgcolor=CARD_BG,
        focused_border_color=ACCENT_GREEN,
        content_padding=14,
        width=float("inf")
    )

    trip_pace_input = ft.Dropdown(
        hint_text="Select pace…",
        options=[
            ft.dropdown.Option("Morning person"),
            ft.dropdown.Option("Night owl"),
            ft.dropdown.Option("Flexible"),
        ],
        text_size=13,
        color=TEXT_COLOR,
        border_color=BORDER_DEFAULT,
        border_width=1,
        border_radius=12,
        bgcolor=CARD_BG,
        focused_border_color=ACCENT_GREEN,
        content_padding=14,
        width=float("inf")
    )

    # --- Step 3 Controls ---
    activities_opts = [
        "Amusement Park", "Aquarium", "Art Gallery", "Bar", "Beach", 
        "Cafe", "Campground", "Casino", "Museum", "Night Club", 
        "Park", "Restaurant", "Shopping Mall", "Spa", "Stadium", 
        "Tourist Attraction", "Zoo", "Historical Site", "Hiking Area"
    ]

    def on_chip_click(e):
        for c in chips_row.controls:
            label_text = c.content.controls[1].value.replace("✓ ", "")
            if c == e.control:
                c.data["selected"] = True
                c.bgcolor = CHIP_BG_SELECTED
                c.border = ft.border.all(1.5, ACCENT_GREEN)
                c.content.controls[1].value = f"✓ {label_text}"
                c.content.controls[1].color = ACCENT_GREEN
            else:
                c.data["selected"] = False
                c.bgcolor = CARD_BG
                c.border = ft.border.all(1, BORDER_DEFAULT)
                c.content.controls[1].value = label_text
                c.content.controls[1].color = TEXT_COLOR
            c.update()

    # 2 columns pill grid wrapper
    def create_chip(act):
        return ft.Container(
            content=ft.Row([
                ft.Container(), # Empty logic wrapper replaced by string prefix
                ft.Text(act, size=14, color=TEXT_COLOR, weight=ft.FontWeight.W_500, text_align=ft.TextAlign.CENTER, expand=True)
            ], alignment=ft.MainAxisAlignment.CENTER),
            bgcolor=CARD_BG,
            border=ft.border.all(1, BORDER_DEFAULT),
            border_radius=24, # full pill
            height=48,
            on_click=on_chip_click,
            data={"selected": False},
        )

    # Use a generic Row wrapped over to act as Grid if we force exact widths, or just rely on a standard two column setup via Rows.
    chips_row = ft.Column(spacing=10)
    for i in range(0, len(activities_opts), 2):
        row_controls = []
        c1 = ft.Container(content=create_chip(activities_opts[i]), expand=True)
        row_controls.append(c1)
        if i + 1 < len(activities_opts):
            c2 = ft.Container(content=create_chip(activities_opts[i+1]), expand=True)
            row_controls.append(c2)
        else:
            c2 = ft.Container(expand=True)
            row_controls.append(c2)
        chips_row.controls.append(ft.Row(row_controls, spacing=10, width=float("inf")))

    # Need a flat list of actual interactable controls to iterate for selection:
    def get_all_chips():
        all_chips = []
        for r in chips_row.controls:
            for c in r.controls:
                if isinstance(c.content, ft.Container) and "selected" in c.content.data:
                    all_chips.append(c.content)
        return all_chips
    
    # Overwrite the on_chip_click to use get_all_chips internally
    def on_chip_click_real(e):
        for c in get_all_chips():
            label_text = c.content.controls[1].value.replace("✓ ", "")
            if c == e.control:
                c.data["selected"] = True
                c.bgcolor = CHIP_BG_SELECTED
                c.border = ft.border.all(1.5, ACCENT_GREEN)
                c.content.controls[1].value = f"✓ {label_text}"
                c.content.controls[1].color = ACCENT_GREEN
            else:
                c.data["selected"] = False
                c.bgcolor = CARD_BG
                c.border = ft.border.all(1, BORDER_DEFAULT)
                c.content.controls[1].value = label_text
                c.content.controls[1].color = TEXT_COLOR
            c.update()
            
    # Re-apply the on_click internally
    for c in get_all_chips():
        c.on_click = on_chip_click_real

    dietary_input = ft.Dropdown(
        hint_text="Select dietary requirement",
        options=[
            ft.dropdown.Option("None"),
            ft.dropdown.Option("Vegetarian"),
            ft.dropdown.Option("Vegan"),
            ft.dropdown.Option("Halal"),
            ft.dropdown.Option("Kosher"),
            ft.dropdown.Option("Gluten-Free"),
        ],
        text_size=13,
        color=TEXT_COLOR,
        border_color=BORDER_DEFAULT,
        border_width=1,
        border_radius=12,
        bgcolor=CARD_BG,
        focused_border_color=ACCENT_GREEN,
        content_padding=14,
        width=float("inf")
    )

    # --- Layout components ---
    step_title = ft.Text("", size=12, color=LABEL_COLOR, weight=ft.FontWeight.W_500)
    progress_bar = ft.ProgressBar(value=0.33, color=ACCENT_GREEN, bgcolor=CARD_BG, bar_height=3, border_radius=2, width=float("inf"))
    step_content_container = ft.Container(expand=True, padding=ft.padding.only(top=16))
    
    # Back button ghost style
    btn_back = ft.OutlinedButton(
        content=ft.Text("Back", size=14, color=LABEL_COLOR, weight=ft.FontWeight.W_500),
        on_click=lambda e: change_step(-1), 
        visible=False,
        style=ft.ButtonStyle(
            shape=ft.RoundedRectangleBorder(radius=12),
            side=ft.BorderSide(1, BORDER_DEFAULT)
        ),
        width=float("inf"),
        height=48
    )
    
    # CTA button primary style
    btn_cta = ft.ElevatedButton(
        "Next →", 
        style=ft.ButtonStyle(
            color=BG_COLOR, 
            bgcolor=ACCENT_GREEN, 
            shape=ft.RoundedRectangleBorder(radius=14),
        ),
        width=float("inf"),
        height=56
    )

    def show_alert_dialog(title: str, message: str):
        dialog = ft.AlertDialog(
            modal=True,
            title=ft.Text(title, color=TEXT_COLOR),
            content=ft.Text(message, size=14, color=TEXT_COLOR),
            bgcolor=CARD_BG,
            actions=[ft.TextButton("OK", on_click=lambda e: page.close(dialog), style=ft.ButtonStyle(color=ACCENT_GREEN))],
        )
        page.open(dialog)

    async def handle_cta_click(e):
        if state["step"] < 3:
            # Validate step 1
            if state["step"] == 1:
                if not destination_input.value or not destination_input.value.strip():
                    show_alert_dialog("Missing Information", "Please enter a destination")
                    return
                if not date_from.value or not date_to.value:
                    show_alert_dialog("Missing Information", "Please select both start and end dates")
                    return
                if date_to.value < date_from.value:
                    show_alert_dialog("Invalid Dates", "End date must be after start date")
                    return
            
            # Validate step 2
            if state["step"] == 2:
                if not budget_min.value or not budget_max.value:
                    show_alert_dialog("Missing Information", "Please enter budget range")
                    return
                if not travel_style_input.value:
                    show_alert_dialog("Missing Information", "Please select a travel style")
                    return
                if not trip_pace_input.value:
                    show_alert_dialog("Missing Information", "Please select a trip pace")
                    return

            change_step(1)
        else:
            # Generate Trip
            selected_activities = [c.content.controls[1].value.replace("✓ ", "") for c in get_all_chips() if c.data["selected"]]
            if not selected_activities:
                show_alert_dialog("Missing Information", "Please select an activity")
                return

            supabase = get_supabase_client()
            if not supabase:
                show_alert_dialog("Error", "Database connection not available")
                return
            
            try:
                user_response = supabase.auth.get_user()
                if not user_response or not user_response.user:
                    show_alert_dialog("Authentication Required", "Please log in to create a plan")
                    return
                user_id = user_response.user.id
            except Exception as ex:
                show_alert_dialog("Authentication Required", "Please log in to create a plan")
                return

            btn_cta.disabled = True
            btn_cta.text = "Generating..."
            page.update()

            destination = destination_input.value.strip()
            start_date = date_from.value.date() if isinstance(date_from.value, datetime.datetime) else date_from.value
            end_date = date_to.value.date() if isinstance(date_to.value, datetime.datetime) else date_to.value
            dietary = dietary_input.value or "None"

            status_text = ft.Text("Initializing...", size=16, color=TEXT_COLOR, text_align=ft.TextAlign.CENTER)
            progress_dialog = ft.AlertDialog(
                modal=True,
                bgcolor=CARD_BG,
                title=ft.Text("Generating Plan", weight=ft.FontWeight.BOLD, color=TEXT_COLOR, text_align=ft.TextAlign.CENTER),
                content=ft.Container(
                    content=ft.Column(
                        [ft.ProgressRing(color=ACCENT_GREEN), ft.Container(height=8), status_text],
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                        tight=True,
                    ),
                    padding=20,
                ),
            )
            page.open(progress_dialog)
            
            def update_progress(status: str):
                status_text.value = status
                page.update()
            
            async def generate_plan_async():
                try:
                    ai_engine = AIEngine()
                    plan = await ai_engine.generate_plan(
                        user_id=user_id,
                        destination=destination,
                        date_from=start_date,
                        date_to=end_date,
                        budget_min=budget_min.value,
                        budget_max=budget_max.value,
                        travel_style=travel_style_input.value,
                        time_preference=trip_pace_input.value,
                        activity=selected_activities[0],
                        dietary=dietary,
                        country_code="PH",
                        progress_callback=update_progress
                    )
                    
                    await ai_engine.cleanup()
                    
                    if plan:
                        try:
                            page.close(progress_dialog)
                        except:
                            pass
                        
                        from .components.plan_summary import build_plan_summary_view
                        
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
                            
                        def on_summary_back(e):
                            if len(page.views) > 1:
                                page.views.pop()
                                page.update()
                                
                        trip_data = plan.get("data", {})
                        plan_id = plan.get("id")
                        
                        summary_view = ft.View(
                            "/plan_summary",
                            controls=[apply_gradient_background(
                                build_plan_summary_view(
                                    on_back=on_summary_back,
                                    trip_data=trip_data,
                                    page=page,
                                    plan_id=plan_id
                                )
                            )],
                            padding=0,
                            bgcolor="background"
                        )
                        
                        if len(page.views) > 1:
                            page.views.pop()
                        page.views.append(summary_view)
                        page.route = "/plans"
                        page.update()
                    else:
                        show_error("Failed to generate plan")
                except Exception as ex:
                    show_error(str(ex))

            def show_error(error):
                try: page.close(progress_dialog)
                except: pass
                btn_cta.disabled = False
                btn_cta.text = "Generate my itinerary →"
                show_alert_dialog("Error", f"Error generating plan: {str(error)}")

            page.run_task(generate_plan_async)

    btn_cta.on_click = handle_cta_click

    def render_step():
        step = state["step"]
        if step == 1:
            step_title.value = "Step 1 of 3 — Where & When"
            progress_bar.value = 0.33
            btn_back.visible = False
            btn_cta.text = "Next →"
            step_content_container.content = ft.Column(
                [
                    ft.Text("Destination", size=11, color=LABEL_COLOR, weight=ft.FontWeight.W_500),
                    destination_input,
                    ft.Container(height=16),
                    destination_preview_card,
                    ft.Container(height=24),
                    ft.Text("Travel Dates", size=11, color=LABEL_COLOR, weight=ft.FontWeight.W_500),
                    date_btn
                ],
                spacing=8
            )
        elif step == 2:
            step_title.value = "Step 2 of 3 — Your Style"
            progress_bar.value = 0.67
            btn_back.visible = True
            btn_cta.text = "Next →"
            step_content_container.content = ft.Column(
                [
                    ft.Text("Budget range (₱)", size=11, color=LABEL_COLOR, weight=ft.FontWeight.W_500),
                    budget_row,
                    ft.Container(height=24),
                    ft.Text("Travel Style", size=11, color=LABEL_COLOR, weight=ft.FontWeight.W_500),
                    travel_style_input,
                    ft.Container(height=24),
                    ft.Text("Trip pace", size=11, color=LABEL_COLOR, weight=ft.FontWeight.W_500),
                    trip_pace_input
                ],
                spacing=8
            )
        elif step == 3:
            step_title.value = "Step 3 of 3 — Activities"
            progress_bar.value = 1.0
            btn_back.visible = True
            btn_cta.text = "Generate my itinerary →"
            
            step_content_container.content = ft.Column(
                [
                    ft.Row([
                        ft.Text("Activities", size=11, color=LABEL_COLOR, weight=ft.FontWeight.W_500),
                        ft.Text("— pick one", size=11, color=LABEL_COLOR)
                    ], spacing=4),
                    chips_row,
                    ft.Container(height=24),
                    ft.Text("Dietary Requirements (Optional)", size=11, color=LABEL_COLOR, weight=ft.FontWeight.W_500),
                    dietary_input
                ],
                spacing=8
            )
        
        step_title.update()
        progress_bar.update()
        btn_back.update()
        btn_cta.update()
        step_content_container.update()

    def change_step(delta):
        state["step"] += delta
        render_step()

    # Initial render setup without update() call since not yet on page
    step_title.value = "Step 1 of 3 — Where & When"
    progress_bar.value = 0.33
    step_content_container.content = ft.Column(
        [
            ft.Text("Destination", size=11, color=LABEL_COLOR, weight=ft.FontWeight.W_500),
            destination_input,
            ft.Container(height=16),
            destination_preview_card,
            ft.Container(height=24),
            ft.Text("Travel Dates", size=11, color=LABEL_COLOR, weight=ft.FontWeight.W_500),
            date_btn
        ],
        spacing=8
    )

    content = ft.Container(
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
            ft.Container(
                padding=20,
                content=ft.Column(
                    [
                        # Top Fixed Container for scrollable form
                        ft.Container(
                            expand=True,
                            content=ft.Column(
                                [
                                    # Top Row with Back (Global) and Title
                                    ft.Row(
                                        [
                                            ft.IconButton(icon=ft.Icons.ARROW_BACK, on_click=on_back, icon_color="onBackground"),
                                            ft.Text("Plan Your Trip", size=24, weight=ft.FontWeight.BOLD, color="onBackground"),
                                        ],
                                        alignment=ft.MainAxisAlignment.START,
                                    ),
                                
                                ft.Container(height=8),
                                
                                # Progress Section
                                ft.Column([
                                    step_title,
                                    progress_bar
                                ], spacing=8),
                                
                                ft.Container(height=24),
                                
                                # Form Content
                                step_content_container,
                            ],
                            scroll=ft.ScrollMode.AUTO,
                            expand=True,
                        )
                    ),
                    
                    # Bottom Fixed Actions Container
                    ft.Container(
                        content=ft.Column(
                            [
                                btn_cta,
                                btn_back
                            ], 
                            horizontal_alignment=ft.CrossAxisAlignment.CENTER, 
                            spacing=12
                        ),
                        padding=ft.padding.only(top=16, bottom=24)
                    )
                ],
                expand=True,
            ),
            expand=True,
        ),
    )
)
    
    return content, [date_from, date_to]
