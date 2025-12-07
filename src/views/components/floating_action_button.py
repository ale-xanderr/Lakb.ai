import flet as ft

def create_floating_action_button(on_click=None) -> ft.FloatingActionButton:
    """
    Create a Floating Action Button (FAB).

    Parameters
    ----------
    on_click:
        Callback fired when the FAB is clicked.
    """
    return ft.FloatingActionButton(
        icon=ft.Icons.ADD,
        text="New Plan",
        on_click=on_click,
        shape=ft.RoundedRectangleBorder(radius=16),
    )
