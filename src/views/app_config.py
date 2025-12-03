import flet as ft

# Centralized app window configuration
APP_WIDTH: int = 412
APP_HEIGHT: int = 917
APP_TITLE: str = "Lakb.ai"
APP_RESIZABLE: bool = False
APP_PADDING: int | float = 0


def configure_page(page: ft.Page, *, title: str | None = None) -> None:
    """Apply common window configuration to the given Flet page.

    Parameters
    ----------
    page:
        The Flet `Page` instance to configure.
    title:
        Optional custom window title; falls back to `APP_TITLE`.
    """

    # Basic properties
    page.title = title or APP_TITLE
    page.padding = APP_PADDING

    # Handle both older top-level window_* properties and the newer
    # `page.window` object, so the config works across runtimes.
    # Desktop/web runtimes
    if getattr(page, "window", None) is not None:
        page.window.width = APP_WIDTH
        page.window.height = APP_HEIGHT
        page.window.resizable = APP_RESIZABLE

    # Backwards/alternative attributes (no-op if not present)
    if hasattr(page, "window_width"):
        page.window_width = APP_WIDTH
    if hasattr(page, "window_height"):
        page.window_height = APP_HEIGHT
    if hasattr(page, "window_resizable"):
        page.window_resizable = APP_RESIZABLE
