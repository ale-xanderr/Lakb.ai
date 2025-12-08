import flet as ft
from .components.plan_card import build_plan_card
from .components.loading_indicator import create_loading_indicator
from .components.status_dialog import create_info_message, create_error_message
from core.supabase_client import get_supabase_client
import threading

def build_plans_view(page: ft.Page, on_open_plan=None) -> tuple[ft.Control, callable]:
    """
    Build the plans view content.
    
    Parameters
    ----------
    page:
        The Flet Page instance.
    on_open_plan:
        Callback fired when a plan card is clicked.
    """
    
    # State for plans
    plans_grid = ft.GridView(
        expand=1,
        runs_count=2,
        max_extent=200,
        child_aspect_ratio=0.8,
        spacing=10,
        run_spacing=10,
        controls=[]
    )
    
    loading_indicator = create_loading_indicator("Loading plans...")
    empty_status_dialog = create_info_message("No plans yet. Create your first trip plan!")
    empty_status_dialog.visible = False
    
    # Container for status messages (empty state or errors)
    status_container_ref = ft.Ref[ft.Container]()
    status_container = ft.Container(
        ref=status_container_ref,
        padding=ft.padding.symmetric(horizontal=24),
        content=empty_status_dialog,
        visible=False,
    )
    
    # Main content
    content = ft.SafeArea(
        expand=True,
        content=ft.Column(
            expand=True,
            spacing=0,
            controls=[
                ft.Container(height=10),
                ft.Container(
                    padding=ft.padding.symmetric(horizontal=24),
                    content=ft.Text("My Plans", size=28, weight=ft.FontWeight.BOLD, color="onBackground"),
                ),
                status_container,
                ft.Container(height=25),
                ft.Container(
                    padding=ft.padding.symmetric(horizontal=24),
                    content=ft.Column(
                        [
                            loading_indicator,
                            plans_grid
                        ],
                        expand=True,
                    ),
                    expand=True,
                )
            ]
        ),
    )
    
    def fetch_plans():
        """Fetch plans from Supabase."""
        supabase = get_supabase_client()
        if not supabase:
            show_error("Database connection not available")
            return
        
        try:
            # Get current user
            user_response = supabase.auth.get_user()
            if not user_response or not user_response.user:
                show_no_plans()
                return
            
            user_id = user_response.user.id
            
            # Fetch plans
            response = supabase.table("plans").select("*").eq("user_id", user_id).order("created_at", desc=True).execute()
            
            plans = []
            if response.data:
                for plan_data in response.data:
                    # Check if plan is still generating
                    data = plan_data.get("data", {})
                    status = data.get("status", "completed")
                    itinerary = data.get("itinerary", [])
                    
                    # Plan is generating if status is "generating" or itinerary is empty
                    is_generating = status == "generating" or (not itinerary or len(itinerary) == 0)
                    
                    plan = {
                        "id": plan_data.get("id"),
                        "title": plan_data.get("title", "Untitled Plan"),
                        "description": plan_data.get("description", ""),
                        "image_url": plan_data.get("image_url"),
                        "is_generating": is_generating,
                        "data": data
                    }
                    plans.append(plan)
            
            display_plans(plans)
            
            # If there are generating plans, set up polling to refresh
            generating_plans = [p for p in plans if p.get("is_generating")]
            if generating_plans:
                # Poll every 3 seconds to check if plans are done generating
                def poll_for_updates():
                    import time
                    poll_supabase = get_supabase_client()
                    if not poll_supabase:
                        return
                    
                    while True:
                        time.sleep(3)
                        # Check if we still have generating plans
                        try:
                            user_response = poll_supabase.auth.get_user()
                            if user_response and user_response.user:
                                user_id = user_response.user.id
                                response = poll_supabase.table("plans").select("*").eq("user_id", user_id).order("created_at", desc=True).execute()
                                
                                # Check if any plans are still generating
                                still_generating = False
                                updated_plans = []
                                if response.data:
                                    for plan_data in response.data:
                                        data = plan_data.get("data", {})
                                        status = data.get("status", "completed")
                                        itinerary = data.get("itinerary", [])
                                        is_gen = status == "generating" or (not itinerary or len(itinerary) == 0)
                                        if is_gen:
                                            still_generating = True
                                        
                                        updated_plans.append({
                                            "id": plan_data.get("id"),
                                            "title": plan_data.get("title", "Untitled Plan"),
                                            "description": plan_data.get("description", ""),
                                            "image_url": plan_data.get("image_url"),
                                            "is_generating": is_gen,
                                            "data": data
                                        })
                                
                                # Refresh the view
                                display_plans(updated_plans)
                                
                                # Stop polling if no plans are generating
                                if not still_generating:
                                    break
                        except Exception as e:
                            print(f"Error in polling: {e}")
                            break
                
                poll_thread = threading.Thread(target=poll_for_updates, daemon=True)
                poll_thread.start()
            
        except Exception as e:
            print(f"Error fetching plans: {e}")
            import traceback
            traceback.print_exc()
            show_error(f"Error loading plans: {str(e)}")
    
    def display_plans(plans):
        """Display plans in the grid."""
        loading_indicator.visible = False
        
        if not plans or len(plans) == 0:
            empty_status_dialog.visible = True
            if status_container_ref.current:
                status_container_ref.current.content = empty_status_dialog
                status_container_ref.current.visible = True
            plans_grid.controls = []
        else:
            empty_status_dialog.visible = False
            if status_container_ref.current:
                status_container_ref.current.visible = False
            plans_grid.controls = [
                build_plan_card(plan, on_card_click=on_open_plan if not plan.get("is_generating") else None)
                for plan in plans
            ]
        
        page.update()
    
    def show_no_plans():
        """Show empty state."""
        loading_indicator.visible = False
        empty_status_dialog.visible = True
        if status_container_ref.current:
            status_container_ref.current.content = empty_status_dialog
            status_container_ref.current.visible = True
        plans_grid.controls = []
        page.update()
    
    def show_error(message):
        """Show error message."""
        loading_indicator.visible = False
        empty_status_dialog.visible = False
        error_dialog = create_error_message(message)
        if status_container_ref.current:
            status_container_ref.current.content = error_dialog
            status_container_ref.current.visible = True
        plans_grid.controls = []
        page.update()
    
    # Fetch plans in background
    def fetch_async():
        fetch_plans()
    
    thread = threading.Thread(target=fetch_async, daemon=True)
    thread.start()
    
    # Return both the content and a refresh function
    def refresh_plans():
        """Refresh the plans view by fetching plans again."""
        def refresh_async():
            fetch_plans()
        refresh_thread = threading.Thread(target=refresh_async, daemon=True)
        refresh_thread.start()
    
    return content, refresh_plans
