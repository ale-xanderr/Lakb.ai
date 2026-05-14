import flet as ft


def create_navigation_bar(
    selected_index: int = 0,
    on_change=None,
) -> ft.NavigationBar:
    """
    Builds and returns a Flet NavigationBar control.
    The control can be attached to a page using `page.navigation_bar = create_navigation_bar()`.

    Args:
        selected_index: Index of initially selected destination.
        on_change: Optional callback fired when the selected destination changes.
                   It receives a `ControlEvent` where `e.control.selected_index` is the new index.
    """

    return ft.NavigationBar(
        bgcolor="surface",  # Use theme surface color for visibility
        indicator_color="primary",
        label_behavior=ft.NavigationBarLabelBehavior.ALWAYS_SHOW,
        animation_duration=400,  # Smooth 400ms animation when switching tabs
        selected_index=selected_index,
        destinations=[
            ft.NavigationBarDestination(
                icon=ft.Icons.HOME_OUTLINED,
                selected_icon=ft.Icons.HOME,
                label="Home",
            ),
            ft.NavigationBarDestination(
                icon=ft.Icons.TRAVEL_EXPLORE_OUTLINED,
                selected_icon=ft.Icons.TRAVEL_EXPLORE,
                label="Discover",
            ),
            ft.NavigationBarDestination(
                icon=ft.Icons.LOCAL_ACTIVITY_OUTLINED,
                selected_icon=ft.Icons.LOCAL_ACTIVITY,
                label="Plans",
            ),
            ft.NavigationBarDestination(
                icon=ft.Icons.FAVORITE_BORDER,
                selected_icon=ft.Icons.FAVORITE,
                label="Favorites",
            ),
        ],
        on_change=on_change,
    )

