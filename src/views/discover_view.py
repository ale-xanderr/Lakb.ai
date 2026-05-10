import flet as ft
from services.interaction_service import InteractionService
from services.favorites_service import FavoritesService
from services.api_service import APIService
from .components.swipe_card import SwipeCard
import random

def build_discover_view(page: ft.Page, api_service: APIService) -> tuple[ft.Control, callable]:
    """
    Builds the Discover view with Tinder-like swiping for places.
    """
    # Reuse shared services if available
    if hasattr(page, "_shared_services"):
        interaction_service = page._shared_services.get("interaction_service", InteractionService())
        favorites_service = page._shared_services.get("favorites_service", FavoritesService())
    else:
        interaction_service = InteractionService()
        favorites_service = FavoritesService()
    
    # State
    places = []
    current_index = 0
    
    # UI Refs
    stack_ref = ft.Ref[ft.Stack]()
    loading_ref = ft.Ref[ft.Container]()
    empty_ref = ft.Ref[ft.Container]()

    def load_places():
        loading_ref.current.visible = True
        empty_ref.current.visible = False
        if stack_ref.current:
            stack_ref.current.controls.clear()
        page.update()
        
        # 1. Fetch preferences to influence search and filter
        visited_place_ids = set()
        swiped_place_ids = set()
        favorite_places = []
        liked_places = []
        
        try:
            # Get visited to completely exclude
            for vp in interaction_service.get_visited_places():
                if "place_id" in vp:
                    visited_place_ids.add(vp["place_id"])
                    
            # Get all swipes to avoid showing same cards again
            for sp in interaction_service.get_swipes():
                if "place_id" in sp:
                    swiped_place_ids.add(sp["place_id"])
                    
            # Get likes and favorites for recommendations
            liked_places = interaction_service.get_liked_places()
            favorite_places = favorites_service.get_favorites()
        except Exception as e:
            print(f"Error fetching preferences for Discover: {e}")

        # 2. Determine search query based on preferences
        search_query = "tourist attractions"
        
        if favorite_places or liked_places:
            # Combine and pick a random place to base recommendations on
            combined_prefs = favorite_places + [p.get("place_data", {}) for p in liked_places]
            if combined_prefs:
                base_place = random.choice(combined_prefs)
                base_name = base_place.get("name", "")
                if base_name:
                    # e.g., "Places like Mount Mayon" or "Attractions near Mount Mayon"
                    search_query = f"attractions near {base_name}"
        else:
            # Cycle through generic categories if no preferences
            categories = ["tourist attractions", "hidden gems", "nature parks", "historical sites", "beaches"]
            search_query = random.choice(categories)

        print(f"DEBUG: Discover searching for: {search_query}")
        result = api_service.search_places(query=search_query)
        
        nonlocal places, current_index
        if result and "results" in result:
            raw_places = result["results"]
            
            # Filter out places the user has already visited or swiped on
            places = [
                p for p in raw_places 
                if (p.get("place_id") or p.get("id")) not in visited_place_ids 
                and (p.get("place_id") or p.get("id")) not in swiped_place_ids
            ]
            
            # If everything was filtered out, we might need to search again, 
            # but for now we'll just show empty state if places is empty
            print(f"DEBUG: Discover found {len(raw_places)} places, filtered to {len(places)}")
            
            current_index = len(places) - 1
            render_cards()
        else:
            loading_ref.current.visible = False
            empty_ref.current.visible = True
            page.update()

    def handle_swipe_left(place):
        interaction_service.record_swipe(place, "dislike")
        next_card()

    def handle_swipe_right(place):
        interaction_service.record_swipe(place, "like")
        next_card()

    def handle_card_click(place):
        title = place.get("name") or place.get("title", "Unknown")
        address = place.get("formatted_address") or place.get("address", "")
        place_id = place.get("place_id") or place.get("id")
        
        image_url = place.get("image_url")
        if not image_url and "photos" in place and len(place["photos"]) > 0:
            photo_ref = place["photos"][0].get("photo_reference")
            if photo_ref:
                image_url = api_service.get_photo_url(photo_ref)
        
        adapted_data = {
            "title": title,
            "address": address,
            "image_url": image_url,
            "description": "Description not available from Search API",
            "price": "N/A",
            "rating": place.get("rating", 0),
            "id": place_id,
            "is_favorite": favorites_service.is_favorite(place_id)
        }
        
        if hasattr(page, "_navigation_controller"):
            page._navigation_controller.navigate_destination(adapted_data)

    def btn_swipe_left(e):
        if stack_ref.current and len(stack_ref.current.controls) > 0:
            top_container = stack_ref.current.controls[-1]
            top_card = top_container.content
            top_card.swipe_left_animated()
            
    def btn_swipe_right(e):
        if stack_ref.current and len(stack_ref.current.controls) > 0:
            top_container = stack_ref.current.controls[-1]
            top_card = top_container.content
            top_card.swipe_right_animated()

    def update_card_stack():
        if not stack_ref.current: return
        remaining = len(stack_ref.current.controls)
        for i, container in enumerate(stack_ref.current.controls):
            dist = remaining - 1 - i
            container.scale = max(0.8, 1.0 - (dist * 0.05))
            container.offset = ft.Offset(0, (dist * 20) / 400) # Card height 400 approx
            container.animate_scale = ft.Animation(300, ft.AnimationCurve.EASE_OUT)
            container.animate_offset = ft.Animation(300, ft.AnimationCurve.EASE_OUT)
            container.visible = dist < 3

    def next_card():
        nonlocal current_index
        if stack_ref.current and len(stack_ref.current.controls) > 0:
            stack_ref.current.controls.pop()
            current_index -= 1
            
            update_card_stack()
            
            if current_index < 0:
                empty_ref.current.visible = True
                buttons_row.visible = False
            page.update()

    def render_cards():
        loading_ref.current.visible = False
        if not stack_ref.current:
            return
            
        stack_ref.current.controls.clear()
        
        if len(places) == 0:
            empty_ref.current.visible = True
            buttons_row.visible = False
            page.update()
            return
            
        buttons_row.visible = True
            
        # Add cards to stack (first in array goes to bottom of stack)
        for i, place in enumerate(places):
            dist = len(places) - 1 - i
            card = SwipeCard(
                place=place,
                on_swipe_left=handle_swipe_left,
                on_swipe_right=handle_swipe_right,
                on_click=handle_card_click
            )
            # Center the card in the stack
            container = ft.Container(
                content=card,
                alignment=ft.alignment.center,
                expand=True,
                scale=max(0.8, 1.0 - (dist * 0.05)),
                offset=ft.Offset(0, (dist * 20) / 400),
                visible=dist < 3
            )
            stack_ref.current.controls.append(container)
            
        page.update()

    buttons_row = ft.Row(
        alignment=ft.MainAxisAlignment.CENTER,
        spacing=40,
        visible=False,
        controls=[
            ft.FloatingActionButton(
                content=ft.Icon(ft.Icons.CLOSE, color="red", size=32),
                bgcolor="surfaceVariant",
                on_click=btn_swipe_left
            ),
            ft.FloatingActionButton(
                content=ft.Icon(ft.Icons.FAVORITE, color="green", size=32),
                bgcolor="surfaceVariant",
                on_click=btn_swipe_right
            )
        ]
    )

    content = ft.Container(
        expand=True,
        padding=24,
        content=ft.Column(
            expand=True,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            controls=[
                ft.Text("Discover", size=32, weight=ft.FontWeight.BOLD, color="onBackground"),
                ft.Text("Swipe right if you like it, left if you don't.", size=14, color="onSurfaceVariant"),
                ft.Container(height=12),
                ft.Container(
                    expand=True,
                    alignment=ft.alignment.center,
                    content=ft.Stack(
                        ref=stack_ref,
                        expand=True,
                        controls=[]
                    )
                ),
                buttons_row,
                ft.Container(
                    ref=loading_ref,
                    visible=True,
                    content=ft.Column(
                        alignment=ft.MainAxisAlignment.CENTER,
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                        controls=[
                            ft.ProgressRing(),
                            ft.Text("Finding places for you...")
                        ]
                    )
                ),
                ft.Container(
                    ref=empty_ref,
                    visible=False,
                    content=ft.Column(
                        alignment=ft.MainAxisAlignment.CENTER,
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                        controls=[
                            ft.Icon(ft.Icons.CHECK_CIRCLE_OUTLINE, size=64, color="primary"),
                            ft.Text("You've seen everything!", size=18, weight=ft.FontWeight.BOLD),
                            ft.ElevatedButton("Find More", on_click=lambda _: load_places())
                        ]
                    )
                )
            ]
        )
    )

    return content, load_places