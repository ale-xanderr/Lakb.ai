import flet as ft

# Import the existing view entry points
from views.home_view import main as home_main
from views.login_view import main as login_main
from views.splash import main as splash_main


def main(page: ft.Page):
    """
    Central app entry for Lakb.ai.

    For now, this simply delegates to one of the existing views.
    To switch the initial screen, change which function is called below.
    """

    # Show SPLASH screen:
    splash_main(page)

    # If you want to start on the LOGIN screen instead, comment the line
    # above and uncomment this:
    # login_main(page)


if __name__ == "__main__":
    ft.app(target=main)