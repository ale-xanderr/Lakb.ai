import flet as ft

def SearchBar(
    on_submit,
    on_change=None,
    on_tap=None,
    on_filter_click=None,
    history=None,
    ref=None,
    bar_hint_text="Search places...",
    view_hint_text="Search for a place...",
):
    """
    A reusable SearchBar component.

    Args:
        on_submit: Callback function when search is submitted.
        on_change: Callback function when text changes.
        on_tap: Callback function when the search bar is tapped.
        on_filter_click: Callback function when filter button is clicked.
        history: List of strings for recent search history.
        ref: ft.Ref for the SearchBar control.
        bar_hint_text: Hint text for the closed bar.
        view_hint_text: Hint text for the open view.
    """
    if ref is None:
        ref = ft.Ref[ft.SearchBar]()

    def close_search(value):
        if ref.current:
            ref.current.close_view(value)
            # Create a fake event to trigger on_submit
            class FakeEvent:
                control = ref.current
            ref.current.value = value
            on_submit(FakeEvent())

    history_controls = []
    if history:
        history_controls = [
            ft.ListTile(
                title=ft.Text(h),
                on_click=lambda e, val=h: close_search(val),
                data=h
            )
            for h in reversed(history)
        ]

    return ft.SearchBar(
        ref=ref,
        bar_hint_text=bar_hint_text,
        view_hint_text=view_hint_text,
        view_leading=ft.IconButton(icon=ft.Icons.ARROW_BACK, on_click=lambda _: ref.current.close_view()),
        bar_leading=ft.Icon(ft.Icons.SEARCH, color="#B0B0B0"),
        bar_trailing=[
            ft.IconButton(
                icon=ft.Icons.TUNE,
                icon_color="onBackground",
                on_click=on_filter_click
            )
        ] if on_filter_click else [],
        controls=history_controls,
        on_submit=on_submit,
        on_change=on_change,
        on_tap=on_tap,
        full_screen=False,
        bar_bgcolor="surface",
        bar_overlay_color=ft.Colors.with_opacity(0.1, "primary"),
    )

def build_filter_sheet(page, on_category_selected, current_category=None):
    """
    Builds a reusable bottom sheet for category filtering.
    
    Args:
        page: The Flet page instance.
        on_category_selected: Callback(category_name) when a category is clicked.
        current_category: The currently selected category (optional).
    """
    bs = ft.BottomSheet(content=ft.Container())

    def on_click(e, category):
        page.close(bs)
        on_category_selected(category)
        
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
                            bgcolor="primary" if current_category == item else "transparent",
                            content=ft.Text(
                                item, 
                                color="white" if current_category == item else "onBackground", 
                                size=12
                            ),
                            on_click=lambda e, i=item: on_click(e, i)
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
                # Add Clear Filter button if a category is selected
                ft.ElevatedButton("Clear Filter", on_click=lambda e: on_click(e, None), width=float("inf")) if current_category else ft.Container(),
            ]
        )
    )
    return bs

class CategoryTabs(ft.Row):
    def __init__(self, page, on_category_selected, selected_category=None):
        super().__init__(scroll=ft.ScrollMode.HIDDEN, spacing=10)
        self.page_ref = page 
        self.on_category_selected = on_category_selected
        self.selected_category = selected_category
        
        # Default categories that are always available
        self.default_categories = ["Hotel", "Cafe", "Restaurant", "Lodging"]
        
        # All categories including those added from "More" filter
        self.all_categories = self.default_categories.copy()
        
        # Visible categories in the row (will be reordered dynamically)
        self.visible_categories = self.default_categories.copy()
        
        self.render()
    
    def render(self):
        self.controls.clear()
        
        def on_chip_select(e):
            """Handle chip selection/deselection"""
            category = e.control.label.value
            
            if self.selected_category == category:
                # Deselect if clicking the same category
                self.selected_category = None
                self.on_category_selected(None)
            else:
                # Select new category
                self.selected_category = category
                self.on_category_selected(category)
                
                # Move selected category to the front
                if category in self.visible_categories:
                    self.visible_categories.remove(category)
                self.visible_categories.insert(0, category)
            
            self.render()
            self.update()
            
            # Add page update to ensure chips reflect selection
            if self.page_ref:
                self.page_ref.update()

        # Create chips for visible categories
        for category in self.visible_categories:
            is_selected = (category == self.selected_category)
            
            chip = ft.Chip(
                label=ft.Text(category, weight=ft.FontWeight.W_500, color="#FFFFFF" if is_selected else "onBackground"),
                bgcolor="primary" if is_selected else "transparent",
                selected_color="primary",
                border_side=ft.BorderSide(1, "#E0E0E0") if not is_selected else ft.BorderSide(0, "transparent"),
                selected=is_selected,
                show_checkmark=is_selected,
                check_color="#FFFFFF",
                on_select=on_chip_select,
                padding=ft.padding.symmetric(horizontal=12, vertical=0),
            )
            
            self.controls.append(chip)
            
        # Add "More" button
        self.controls.append(
            ft.Container(
                padding=ft.padding.symmetric(horizontal=20, vertical=8),
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
                on_click=lambda e: self.page_ref.open(build_filter_sheet(self.page_ref, self.handle_more_selection, self.selected_category))
            )
        )

    def handle_more_selection(self, category):
        """Handle category selection from More filter sheet"""
        if category:
            self.selected_category = category
            self.on_category_selected(category)
            
            # Add category to visible categories if not already present
            if category not in self.all_categories:
                self.all_categories.append(category)
            
            if category not in self.visible_categories:
                self.visible_categories.append(category)
            
            # Move selected category to the front
            if category in self.visible_categories:
                self.visible_categories.remove(category)
            self.visible_categories.insert(0, category)
            
            self.render()
            self.update()
        else:
            # Clear filter
            self.selected_category = None
            self.on_category_selected(None)
            self.render()
            self.update()

