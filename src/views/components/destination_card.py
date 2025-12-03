"""
Destination details screen component.

This page is inspired by the provided UI inspiration and wireframe:
- Large hero image on top
- Destination title, location and basic info
- Tabs for "Overview", "Details", "Ratings"
- Long text area / body content
- Section for "Related Tourist Spots"

The entry point is the function :func:`build_destination_page` which returns
the full layout as a Flet control.  It is designed to be used like this:

    from components.destination_card import build_destination_page

    page.clean()
    page.add(build_destination_page(page, place_data))
"""

import flet as ft


"""
Destination details screen component.

This page is inspired by the provided UI inspiration and wireframe:
- Large hero image on top
- Destination title, location and basic info
- Tabs for "Overview", "Details", "Ratings"
- Long text area / body content
- Section for "Related Tourist Spots"

The entry point is the function :func:`build_destination_page` which returns
the full layout as a Flet control.  It is designed to be used like this:

    from components.destination_card import build_destination_page

    page.clean()
    page.add(build_destination_page(page, place_data))
"""

import flet as ft


def _build_top_images(place: dict) -> ft.Control:
    """Hero image + secondary stacked image on the right."""
    main_image_url = place.get("image_url") or "https://picsum.photos/seed/deerfarm/800/600"

    main_image = ft.Container(
        expand=True,
        clip_behavior=ft.ClipBehavior.HARD_EDGE,
        border_radius=ft.border_radius.all(24),
        bgcolor="surface",
        content=ft.Image(src=main_image_url, fit=ft.ImageFit.COVER),
    )

    side_image = ft.Container(
        width=90,
        clip_behavior=ft.ClipBehavior.HARD_EDGE,
        border_radius=ft.border_radius.all(24),
        bgcolor="surface",
        content=ft.Image(src="https://picsum.photos/seed/side1/300/400", fit=ft.ImageFit.COVER),
    )

    return ft.Container(
        padding=ft.padding.symmetric(horizontal=24, vertical=16),
        content=ft.Row(
            spacing=12,
            controls=[
                # Use a container with expand=True instead of ft.Expanded
                ft.Container(expand=True, content=main_image),
                side_image,
            ],
        ),
    )


def _build_header_info(place: dict) -> ft.Control:
    """Destination title, location and quick stats (open, temp, etc.)."""
    title = place.get("title", "Deer Farm")
    address = place.get("address", "Hanawan, Ocampo, Camarines Sur")

    return ft.Container(
        padding=ft.padding.symmetric(horizontal=24),
        content=ft.Column(
            spacing=8,
            controls=[
                ft.Text(title, size=24, weight=ft.FontWeight.BOLD, color="onBackground"),
                ft.Row(
                    spacing=8,
                    vertical_alignment=ft.CrossAxisAlignment.CENTER,
                    controls=[
                        ft.Icon(ft.Icons.LOCATION_ON_OUTLINED, size=16, color="primary"),
                        ft.Text(address, size=12, color="onSurfaceVariant"),
                    ],
                ),
                ft.Row(
                    spacing=16,
                    controls=[
                        ft.Column(
                            spacing=2,
                            controls=[
                                ft.Text("Open", size=11, color="onSurfaceVariant"),
                                ft.Text("24 Hours", size=12, weight=ft.FontWeight.W_600, color="onBackground"),
                            ],
                        ),
                        ft.Column(
                            spacing=2,
                            controls=[
                                ft.Text("Temp", size=11, color="onSurfaceVariant"),
                                ft.Text("29°C", size=12, weight=ft.FontWeight.W_600, color="onBackground"),
                            ],
                        ),
                        ft.Column(
                            spacing=2,
                            controls=[
                                ft.Text("Price", size=11, color="onSurfaceVariant"),
                                ft.Text(place.get("price", "₱ —"), size=12, weight=ft.FontWeight.W_600, color="onBackground"),
                            ],
                        ),
                    ],
                ),
            ],
        ),
    )


def _build_tabs() -> ft.Control:
    """Overview / Details / Ratings tabs."""

    tabs = ft.Tabs(
        selected_index=0,
        indicator_color="primary",
        label_color="onBackground",
        unselected_label_color="onSurfaceVariant",
        divider_color="transparent",
        tabs=[
            ft.Tab(text="Overview"),
            ft.Tab(text="Details"),
            ft.Tab(text="Ratings"),
        ],
    )

    return ft.Container(
        padding=ft.padding.only(left=24, right=24, top=12),
        content=tabs,
    )


def _build_body_text(place: dict) -> ft.Control:
    """Main long text body for the Overview section."""
    description = (
        "Deer Farm has been drawing crowds of visitors for its relaxing green "
        "fields and friendly deer. It is a perfect quick escape where guests "
        "can feed and take photos with the animals while enjoying the cool "
        "breeze of the countryside.\n\n"
        "The long stretch of open area makes it ideal for walking, casual "
        "picnics, and golden hour photos."
    )

    return ft.Container(
        padding=ft.padding.symmetric(horizontal=24, vertical=8),
        content=ft.Text(
            description,
            size=13,
            height=1.4,
            color="onSurfaceVariant",
        ),
    )


def _build_photos_strip() -> ft.Control:
    """Horizontal mini photos row similar to the inspiration UI."""

    items = []
    photo_urls = [
        "https://picsum.photos/seed/p1/200/200",
        "https://picsum.photos/seed/p2/200/200",
        "https://picsum.photos/seed/p3/200/200",
        "https://picsum.photos/seed/p4/200/200",
    ]
    for url in photo_urls:
        items.append(
            ft.Container(
                width=72,
                height=72,
                border_radius=16,
                clip_behavior=ft.ClipBehavior.HARD_EDGE,
                bgcolor="#E9ECEF",
                content=ft.Image(src=url, fit=ft.ImageFit.COVER),
            )
        )

    return ft.Container(
        padding=ft.padding.symmetric(horizontal=24, vertical=8),
        content=ft.Column(
            spacing=6,
            controls=[
                ft.Text("Photos", size=14, weight=ft.FontWeight.W_600, color="onBackground"),
                ft.Row(spacing=8, controls=items),
            ],
        ),
    )


def _build_related_spots() -> ft.Control:
    """List of related tourist spots (simple stacked cards)."""
    related = [
        "River Eco Park",
        "Mountain View Deck",
        "Local Coffee Farm",
    ]

    cards = []
    for name in related:
        cards.append(
            ft.Container(
                height=60,
                border_radius=16,
                padding=ft.padding.symmetric(horizontal=16),
                margin=ft.margin.only(bottom=8),
                bgcolor="surface",
                shadow=ft.BoxShadow(blur_radius=8, color=ft.Colors.with_opacity(0.06, ft.Colors.BLACK)),
                content=ft.Row(
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    vertical_alignment=ft.CrossAxisAlignment.CENTER,
                    controls=[
                        ft.Column(
                            spacing=2,
                            alignment=ft.MainAxisAlignment.CENTER,
                            controls=[
                                ft.Text(name, size=13, weight=ft.FontWeight.W_500, color="onBackground"),
                                ft.Text("Tap to explore more", size=11, color="onSurfaceVariant"),
                            ],
                        ),
                        ft.Icon(ft.Icons.ARROW_FORWARD_IOS, size=16, color="#B0B0B0"),
                    ],
                ),
            )
        )

    return ft.Container(
        padding=ft.padding.symmetric(horizontal=24, vertical=8),
        content=ft.Column(
            spacing=8,
            controls=[
                ft.Text("Related Tourist Spots", size=14, weight=ft.FontWeight.W_600, color="onBackground"),
                *cards,
            ],
        ),
    )


def build_destination_page(page: ft.Page, place: dict, on_back=None) -> ft.Control:
    """Build the full destination details page."""

    scroll_content = ft.Column(
        expand=True,
        spacing=0,
        controls=[
            _build_top_images(place),
            _build_header_info(place),
            _build_tabs(),
            _build_body_text(place),
            _build_photos_strip(),
            _build_related_spots(),
            ft.Container(height=24),
        ],
    )

    return ft.SafeArea(
        expand=True,
        content=ft.Column(
            spacing=0,
            expand=True,
            controls=[
                ft.Container(
                    padding=ft.padding.only(left=24, right=24, top=16, bottom=4),
                    content=ft.Row(
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                        controls=[
                            ft.IconButton(
                                icon=ft.Icons.ARROW_BACK,
                                on_click=on_back if on_back else lambda e: page.go("/"),
                                icon_color="onBackground",
                            ),
                            ft.Text("About", size=18, weight=ft.FontWeight.W_600, color="onBackground"),
                            ft.Container(width=40),  # Spacer to balance back button
                        ],
                    ),
                ),
                ft.Container(
                    expand=True,
                    bgcolor="background",
                    content=ft.ListView(
                        expand=True,
                        padding=0,
                        controls=[scroll_content],
                    ),
                ),
            ],
        ),
    )
