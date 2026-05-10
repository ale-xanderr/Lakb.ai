import flet as ft
import math
from typing import Callable, Dict, Any

class SwipeCard(ft.Container):
    """
    A Tinder-like swipeable card component.
    """
    def __init__(
        self,
        place: Dict[str, Any],
        on_swipe_left: Callable[[Dict[str, Any]], None],
        on_swipe_right: Callable[[Dict[str, Any]], None],
        on_click: Callable[[Dict[str, Any]], None] = None,
        width: int = 300,
        height: int = 400
    ):
        super().__init__()
        self.place = place
        self.on_swipe_left = on_swipe_left
        self.on_swipe_right = on_swipe_right
        self.on_click = on_click
        
        self.card_width = width
        self.card_height = height
        
        # State variables for dragging
        self.offset_x = 0
        self.offset_y = 0
        
        self._build_card()

    def _build_card(self):
        photo_url = "https://picsum.photos/400/500?random=" + str(hash(self.place.get("name", "")) % 1000)
        if self.place.get("photos") and len(self.place["photos"]) > 0:
            # We'd ideally use APIService to get the actual photo URL, 
            # but for the component we'll assume it's passed or use placeholder
            pass
        if self.place.get("image_url"):
            photo_url = self.place.get("image_url")
            
        name = self.place.get("name", "Unknown Place")
        address = self.place.get("formatted_address") or self.place.get("address", "")
        rating = self.place.get("rating", "N/A")
        
        # UI overlays for Like/Nope indicators
        self.like_overlay = ft.Container(
            content=ft.Text("LIKE", size=32, weight=ft.FontWeight.BOLD, color="green"),
            border=ft.border.all(4, "green"),
            border_radius=8,
            padding=8,
            rotate=-0.2,
            opacity=0,
            left=20,
            top=40
        )
        
        self.nope_overlay = ft.Container(
            content=ft.Text("NOPE", size=32, weight=ft.FontWeight.BOLD, color="red"),
            border=ft.border.all(4, "red"),
            border_radius=8,
            padding=8,
            rotate=0.2,
            opacity=0,
            right=20,
            top=40
        )

        self.card_content = ft.Stack(
            width=self.card_width,
            height=self.card_height,
            controls=[
                ft.Container(
                    width=self.card_width,
                    height=self.card_height,
                    border_radius=16,
                    clip_behavior=ft.ClipBehavior.HARD_EDGE,
                    content=ft.Image(src=photo_url, fit=ft.ImageFit.COVER)
                ),
                # Gradient overlay for text readability
                ft.Container(
                    width=self.card_width,
                    height=self.card_height,
                    border_radius=16,
                    gradient=ft.LinearGradient(
                        begin=ft.alignment.top_center,
                        end=ft.alignment.bottom_center,
                        colors=[ft.Colors.TRANSPARENT, ft.Colors.BLACK87],
                        stops=[0.5, 1.0]
                    )
                ),
                self.like_overlay,
                self.nope_overlay,
                # Place info
                ft.Container(
                    bottom=20,
                    left=20,
                    right=20,
                    content=ft.Column(
                        spacing=4,
                        controls=[
                            ft.Text(name, size=24, weight=ft.FontWeight.BOLD, color="white"),
                            ft.Row([
                                ft.Icon(ft.Icons.STAR, color="amber", size=16),
                                ft.Text(f"{rating}", size=14, color="white"),
                            ]),
                            ft.Text(address, size=12, color="white70", max_lines=2, overflow=ft.TextOverflow.ELLIPSIS),
                        ]
                    )
                )
            ]
        )

        self.gesture = ft.GestureDetector(
            on_pan_start=self._on_pan_start,
            on_pan_update=self._on_pan_update,
            on_pan_end=self._on_pan_end,
            on_tap=lambda e: self.on_click(self.place) if self.on_click else None,
            content=self.card_content
        )
        
        self.content = self.gesture
        self.animate_offset = ft.Animation(300, ft.AnimationCurve.EASE_OUT)
        self.animate_rotation = ft.Animation(300, ft.AnimationCurve.EASE_OUT)
        
        # Initial styling
        self.offset = ft.Offset(0, 0)
        self.rotate = 0

    def _on_pan_start(self, e: ft.DragStartEvent):
        # Remove animation during drag for immediate feedback
        self.animate_offset = None
        self.animate_rotation = None
        self.update()

    def _on_pan_update(self, e: ft.DragUpdateEvent):
        self.offset_x += e.delta_x
        self.offset_y += e.delta_y
        
        # Calculate rotation based on horizontal offset
        rotation = (self.offset_x / self.card_width) * 0.2
        
        # Apply transformation
        self.offset = ft.Offset(self.offset_x / self.card_width, self.offset_y / self.card_height)
        self.rotate = rotation
        
        # Adjust overlay opacities
        if self.offset_x > 0:
            self.like_overlay.opacity = min(1.0, self.offset_x / 100)
            self.nope_overlay.opacity = 0
        else:
            self.nope_overlay.opacity = min(1.0, abs(self.offset_x) / 100)
            self.like_overlay.opacity = 0
            
        self.update()

    def _on_pan_end(self, e: ft.DragEndEvent):
        # Restore animations
        self.animate_offset = ft.Animation(300, ft.AnimationCurve.EASE_OUT)
        self.animate_rotation = ft.Animation(300, ft.AnimationCurve.EASE_OUT)
        
        threshold = self.card_width * 0.4
        
        if self.offset_x > threshold:
            # Swiped Right (Like)
            self.offset = ft.Offset(1.5, self.offset_y / self.card_height)
            self.opacity = 0
            self.update()
            if self.on_swipe_right:
                self.on_swipe_right(self.place)
        elif self.offset_x < -threshold:
            # Swiped Left (Dislike)
            self.offset = ft.Offset(-1.5, self.offset_y / self.card_height)
            self.opacity = 0
            self.update()
            if self.on_swipe_left:
                self.on_swipe_left(self.place)
        else:
            # Snap back to center
            self.offset_x = 0
            self.offset_y = 0
            self.offset = ft.Offset(0, 0)
            self.rotate = 0
            self.like_overlay.opacity = 0
            self.nope_overlay.opacity = 0
            self.update()

    def swipe_right_animated(self):
        self.animate_offset = ft.Animation(300, ft.AnimationCurve.EASE_OUT)
        self.animate_rotation = ft.Animation(300, ft.AnimationCurve.EASE_OUT)
        self.offset = ft.Offset(1.5, 0)
        self.rotate = 0.2
        self.like_overlay.opacity = 1
        self.opacity = 0
        self.update()
        import threading, time
        def call_callback():
            time.sleep(0.3)
            if self.on_swipe_right:
                self.on_swipe_right(self.place)
        threading.Thread(target=call_callback, daemon=True).start()

    def swipe_left_animated(self):
        self.animate_offset = ft.Animation(300, ft.AnimationCurve.EASE_OUT)
        self.animate_rotation = ft.Animation(300, ft.AnimationCurve.EASE_OUT)
        self.offset = ft.Offset(-1.5, 0)
        self.rotate = -0.2
        self.nope_overlay.opacity = 1
        self.opacity = 0
        self.update()
        import threading, time
        def call_callback():
            time.sleep(0.3)
            if self.on_swipe_left:
                self.on_swipe_left(self.place)
        threading.Thread(target=call_callback, daemon=True).start()
