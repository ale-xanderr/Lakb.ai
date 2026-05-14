import flet as ft
from .components.nav_bar import create_navigation_bar
from .components.search_bar import SearchBar, build_filter_sheet, CategoryTabs
from .components.status_dialog import create_info_message, create_error_message
from .components.loading_indicator import create_loading_indicator
from .components.feature_card import build_feature_card
from state import ServiceManager, FavoritesStateController, NavigationController

def build_favorites_view(page: ft.Page, selected_place_state: dict, favorites_service=None) -> ft.Control:
    """
    Builds the Favorites View content.
    Displays a grid of favorite places with filtering and search capabilities.
    
    Args:
        page: The Flet page instance.
        selected_place_state: Dictionary to store the selected place for navigation.
        favorites_service: Optional injected service instance.
        
    Returns:
        ft.Control: The main content control for the view.
    """
    # Initialize state managers
    service_manager = ServiceManager()
    if not service_manager._page:
        service_manager.initialize(page)
    
    favorites_state_controller = FavoritesStateController(page)
    
    # Get services
    if favorites_service is None:
        favorites_service = service_manager.favorites_service
    api_service = service_manager.api_service
    
    print(f"Building Favorites View. Initial count: {len(favorites_state_controller.favorites_data)}")
    
    grid_ref = ft.Ref[ft.GridView]()
    search_bar_ref = ft.Ref[ft.SearchBar]()
    error_dialog_ref = ft.Ref[ft.Container]() # Reference to error dialog container

    def dummy_click(e):
        pass

    # Get navigation controller from page if available
    navigation_controller = getattr(page, "_navigation_controller", None)
    
    # Helper function for card click
    def handle_card_click_favorites(e, data):
        """Handle card click in favorites view"""
        selected_place_state["value"] = data
        if navigation_controller:
            navigation_controller.navigate_destination(data)
        else:
            page.go("/destination")
    
    # Helper function for favorite toggle
    def handle_favorite_toggle(e, item, is_fav):
        """Handle favorite toggle - reload grid to reflect changes"""
        # Always refresh data from service to ensure consistency
        favorites_state_controller.favorites_data = favorites_service.get_favorites(force_refresh=True)
        print(f"DEBUG Favorites View: Refreshed after toggle, now have {len(favorites_state_controller.favorites_data)} favorites")
        filter_and_update_grid()
    
    def load_favorites_data():
        """Load favorites data asynchronously"""
        # Always force refresh from Supabase to get latest data
        # This ensures new favorites added from home view are shown
        favorites_state_controller.favorites_data = favorites_service.get_favorites(force_refresh=True)
        print(f"DEBUG Favorites View: Loaded {len(favorites_state_controller.favorites_data)} favorites from Supabase (force refresh)")
        
        # Update the grid with actual data
        filter_and_update_grid()

    # Set UI refs in state controller
    favorites_state_controller.set_ui_refs(
        grid_ref=grid_ref,
        search_bar_ref=search_bar_ref,
        error_dialog_ref=error_dialog_ref
    )
    
    # --- Filtering Logic ---
    def filter_and_update_grid():
        """Filter favorites based on search query and category"""
        # Optimize: Skip filtering if no filters are applied
        has_filters = (favorites_state_controller.filter_query or 
                      favorites_state_controller.filter_category)
        
        if has_filters:
            filtered = favorites_state_controller.get_filtered_favorites()
        else:
            # No filters, use all favorites directly
            filtered = favorites_state_controller.favorites_data
        
        print(f"DEBUG Filter: Found {len(filtered)} matching favorites")
        
        # Update error/info dialog based on results
        if error_dialog_ref.current:
            if len(favorites_state_controller.favorites_data) == 0:
                # No favorites at all
                error_dialog_ref.current.content = create_info_message("You haven't added any favorites yet. Browse places and tap the heart icon to add them here.")
                error_dialog_ref.current.visible = True
            elif len(filtered) == 0 and (favorites_state_controller.filter_query or favorites_state_controller.filter_category):
                # Have favorites but no matches for current filter
                q = favorites_state_controller.filter_query
                cat = favorites_state_controller.filter_category
                if q and cat:
                    error_dialog_ref.current.content = create_info_message(f"No favorites found matching '{q}' in category '{cat}'.")
                elif q:
                    error_dialog_ref.current.content = create_info_message(f"No favorites found matching '{q}'.")
                else:
                    error_dialog_ref.current.content = create_info_message(f"No favorites found in category '{cat}'.")
                error_dialog_ref.current.visible = True
            else:
                # Have results, hide dialog
                error_dialog_ref.current.visible = False
            
            if error_dialog_ref.current.page:
                error_dialog_ref.current.update()
        
        if grid_ref.current:
            grid_ref.current.controls = [
                build_feature_card(
                    data=x,
                    page=page,
                    on_card_click=handle_card_click_favorites,
                    on_favorite_toggle=handle_favorite_toggle,
                    mode="compact",
                    api_service=api_service
                ) for x in filtered
            ]
            if grid_ref.current.page:
                grid_ref.current.update()

    def handle_search(e):
        """Handle search submission - update query state and filter results"""
        favorites_state_controller.filter_query = e.control.value if e.control.value else ""
        if search_bar_ref.current:
            search_bar_ref.current.close_view()
        print(f"DEBUG Favorites Search: Query='{favorites_state_controller.filter_query}'")
        filter_and_update_grid()
        
    def handle_text_change(e):
        """Handle text changes - clear filter when search is emptied"""
        favorites_state_controller.filter_query = e.control.value if e.control.value else ""
        if not favorites_state_controller.filter_query:
            print("DEBUG Favorites: Search cleared, showing all favorites")
            filter_and_update_grid()

    def handle_filter_selection(category):
        favorites_state_controller.filter_category = category
        filter_and_update_grid()

    def on_filter_click(e):
        page.open(build_filter_sheet(page, handle_filter_selection, current_category=favorites_state_controller.filter_category))

    # Initialize grid with loading indicator
    # Actual cards will be populated asynchronously
    initial_controls = [create_loading_indicator("Loading your favorites...")]

    # Grid Layout
    grid = ft.GridView(
        ref=grid_ref,
        expand=True,
        runs_count=2,
        max_extent=200,
        child_aspect_ratio=0.65,
        spacing=8,
        run_spacing=10,
        padding=ft.padding.symmetric(horizontal=24),
        controls=initial_controls,
    )
    
    # Trigger async loading immediately (no delay)
    import threading
    thread = threading.Thread(target=load_favorites_data, daemon=True)
    thread.start()

    def toggle_filter(e):
        if tabs_container:
            tabs_container.visible = not tabs_container.visible
            tabs_container.update()
            page.update()  # Update page to reflect visibility change

    tabs_container = ft.Container(
        padding=ft.padding.only(left=24),
        margin=ft.margin.only(bottom=12), # Match home_view spacing
        content=CategoryTabs(page, handle_filter_selection, selected_category=favorites_state_controller.filter_category),
        visible=False,
        animate_opacity=300,
    )

    content = ft.SafeArea(
        expand=True,
        content=ft.Column(
            expand=True,
            spacing=0,
            controls=[
                # Fixed spacer - 12px
                ft.Container(height=12),
                
                # Title
                ft.Container(
                    padding=ft.padding.symmetric(horizontal=24),
                    content=ft.Text("Favorites", size=28, weight=ft.FontWeight.BOLD, color="onBackground"),
                ),
                
                # Fixed spacer - 12px
                ft.Container(height=12),
                
                # Search Bar
                ft.Container(
                    padding=ft.padding.symmetric(horizontal=24),
                    content=SearchBar(
                        ref=search_bar_ref,
                        on_submit=handle_search,
                        on_change=handle_text_change,
                        on_tap=lambda _: search_bar_ref.current.open_view() if search_bar_ref.current else None,
                        on_filter_click=toggle_filter,
                        bar_hint_text="Search favorites...",
                        view_hint_text="Search your favorites...",
                    ),
                ),
                
                # Fixed spacer - 12px
                ft.Container(height=12),
                
                # Filter tabs container
                tabs_container,
                
                # Error/Status Dialog Container (shown below tabs when there's an error or info)
                ft.Container(
                    ref=error_dialog_ref,
                    padding=ft.padding.symmetric(horizontal=24),
                    visible=False,
                ),
                
                # Fixed spacer - 12px
                ft.Container(height=12),
                
                # Grid content
                ft.Container(
                    expand=True,
                    content=grid
                )
            ]
        )
    )
    
    return content, load_favorites_data
