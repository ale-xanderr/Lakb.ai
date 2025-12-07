import flet as ft
from .components.plan_card import build_plan_card
from .components.loading_indicator import create_loading_indicator
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
    
    loading_text = ft.Text("Loading plans...", color="onSurfaceVariant")
    empty_text = ft.Text("No plans yet. Create your first trip plan!", color="onSurfaceVariant", text_align=ft.TextAlign.CENTER)
    
    # Main content
    content = ft.SafeArea(
        content=ft.Container(
            padding=10,
            alignment=ft.alignment.top_left,
            expand=True,
            content=ft.Column(
                [
                    ft.Text("My Plans", size=30, weight=ft.FontWeight.BOLD),
                    ft.Text("Manage your generated plans.", color="secondary"),
                    ft.Container(height=20),
                    ft.Container(
                        content=ft.Column(
                            [
                                loading_text,
                                plans_grid
                            ],
                            expand=True,
                        ),
                        expand=True,
                    )
                ],
                expand=True,
            )
        ),
        expand=True,
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
        loading_text.visible = False
        empty_text.visible = False
        
        if not plans or len(plans) == 0:
            empty_text.visible = True
            plans_grid.controls = [empty_text]
        else:
            plans_grid.controls = [
                build_plan_card(plan, on_card_click=on_open_plan if not plan.get("is_generating") else None)
                for plan in plans
            ]
        
        page.update()
    
    def show_no_plans():
        """Show empty state."""
        loading_text.visible = False
        empty_text.visible = True
        plans_grid.controls = [empty_text]
        page.update()
    
    def show_error(message):
        """Show error message."""
        loading_text.visible = False
        error_text = ft.Text(message, color="error", text_align=ft.TextAlign.CENTER)
        plans_grid.controls = [error_text]
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
