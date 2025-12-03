import flet as ft
from .app_config import configure_page


def main(page: ft.Page):
    # Device / window configuration (centralized in app_config)
    configure_page(page, title="Login/Register UI")

    # --- Color Palette (from provided CSS) ---
    PALETTE_LIGHT = {
        "text": "#091a13",
        "background": "#fafdfc",
        "primary": "#46bd8d",
        "secondary": "#95cbd9",
        "accent": "#76a2ce",
    }

    PALETTE_DARK = {
        "text": "#e4f6ef",
        "background": "#010403",
        "primary": "#42b889",
        "secondary": "#265c69",
        "accent": "#315c87",
    }

    # Use Flet theme mode (defaults to light if not explicitly set)
    is_dark_mode = page.theme_mode == ft.ThemeMode.DARK
    palette = PALETTE_DARK if is_dark_mode else PALETTE_LIGHT

    COLOR_TEXT = palette["text"]
    COLOR_BACKGROUND = palette["background"]
    COLOR_PRIMARY = palette["primary"]
    COLOR_SECONDARY = palette["secondary"]
    COLOR_ACCENT = palette["accent"]

    # Surfaces & inputs
    COLOR_SURFACE = "#FFFFFF" if not is_dark_mode else "#020608"
    COLOR_INPUT_BORDER = COLOR_SECONDARY
    COLOR_INPUT_BG = COLOR_SURFACE

    # Apply background
    page.bgcolor = COLOR_BACKGROUND

    def dummy_function(e):
        # Placeholder for buttons that don't do anything yet
        pass

    def go_to_home(e):
        """
        Temporary navigation handler:
        After login/register, clear the login page and show the home view.
        """
        from .home_view import main as home_main

        page.clean()
        home_main(page)

    # --- UPDATED INPUT BUILDER WITH PASSWORD TOGGLE ---
    def create_custom_input(icon_name, label, placeholder, is_password=False, expand=False):
        # Refs for interactivity
        input_ref = ft.Ref[ft.TextField]()
        eye_icon_ref = ft.Ref[ft.IconButton]()

        def toggle_password_view(e):
            # Toggle password property
            input_ref.current.password = not input_ref.current.password
            # Toggle icon (Visibility vs Visibility Off)
            eye_icon_ref.current.icon = (
                ft.Icons.VISIBILITY_OFF if not input_ref.current.password else ft.Icons.VISIBILITY
            )
            # Update controls
            input_ref.current.update()
            eye_icon_ref.current.update()

        # Define Suffix Widget
        suffix_control = ft.Container()
        if is_password:
            suffix_control = ft.IconButton(
                ref=eye_icon_ref,
                icon=ft.Icons.VISIBILITY,
                icon_color=COLOR_SECONDARY,
                icon_size=20,
                on_click=toggle_password_view,
                style=ft.ButtonStyle(
                    padding=0,
                    overlay_color=ft.Colors.TRANSPARENT,
                ),
            )

        return ft.Container(
            border=ft.border.all(1, COLOR_INPUT_BORDER),
            border_radius=10,
            bgcolor=COLOR_INPUT_BG,
            padding=ft.padding.symmetric(horizontal=14, vertical=3),
            margin=ft.margin.only(bottom=12),
            expand=expand,
            content=ft.Row(
                controls=[
                    ft.Icon(icon_name, color=COLOR_PRIMARY, size=20),
                    ft.Container(width=8),
                    ft.Column(
                        spacing=1,
                        alignment=ft.MainAxisAlignment.CENTER,
                        expand=True,
                        controls=[
                            ft.Text(label, size=9, color=COLOR_SECONDARY),
                            ft.TextField(
                                ref=input_ref,
                                value=placeholder,
                                password=is_password,
                                border=ft.InputBorder.NONE,
                                content_padding=ft.padding.only(bottom=3),
                                text_style=ft.TextStyle(
                                    size=13,
                                    weight=ft.FontWeight.W_600,
                                    color=COLOR_TEXT,
                                ),
                                height=40,
                                can_reveal_password=False,
                            ),
                        ],
                    ),
                    suffix_control,
                ],
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
            ),
        )

    # Social Media Button Builder
    def create_social_button(text, icon_src=None, icon_color=None, is_image=False):
        content_icon = None
        if is_image:
            content_icon = ft.Image(src=icon_src, width=24, height=24)
        else:
            content_icon = ft.Icon(icon_src, color=icon_color, size=24)

        return ft.Container(
            expand=True,
            padding=15,
            border=ft.border.all(1, COLOR_SECONDARY),
            border_radius=30,
            on_click=dummy_function,
            content=ft.Row(
                alignment=ft.MainAxisAlignment.CENTER,
                controls=[
                    content_icon,
                    ft.Text(text, color=COLOR_TEXT, weight=ft.FontWeight.BOLD),
                ],
            ),
        )

    # --- State Management ---
    form_content_ref = ft.Ref[ft.Column]()
    login_tab_ref = ft.Ref[ft.Container]()
    register_tab_ref = ft.Ref[ft.Container]()
    action_button_text_ref = ft.Ref[ft.Text]()
    divider_text_ref = ft.Ref[ft.Text]()
    form_container_ref = ft.Ref[ft.Container]()

    def toggle_view(e):
        is_login = e.control.data == "login"

        # UI Style Updates
        login_tab_ref.current.bgcolor = None
        login_tab_ref.current.shadow = None
        login_tab_ref.current.border = ft.border.all(1, COLOR_PRIMARY)
        login_tab_ref.current.content.color = COLOR_TEXT
        register_tab_ref.current.bgcolor = None
        register_tab_ref.current.shadow = None
        register_tab_ref.current.border = ft.border.all(1, COLOR_PRIMARY)
        register_tab_ref.current.content.color = COLOR_TEXT

        active_tab = login_tab_ref.current if is_login else register_tab_ref.current
        active_tab.bgcolor = COLOR_PRIMARY
        active_tab.shadow = ft.BoxShadow(
            blur_radius=5,
            color=ft.Colors.with_opacity(0.1, COLOR_TEXT),
        )
        active_tab.border = None
        active_tab.content.color = COLOR_SURFACE

        # Small slide animation for form container (no fade)
        if form_container_ref.current is not None:
            # Start slightly off-screen to left/right depending on direction
            form_container_ref.current.offset = ft.Offset(
                -0.15 if is_login else 0.15, 0
            )
            form_container_ref.current.update()

        # Form Content Updates
        form_controls = []
        if not is_login: # REGISTER
            form_controls.append(
                ft.Row(
                    controls=[
                        create_custom_input(ft.Icons.PERSON_OUTLINE, "First Name", "Micah", expand=True),
                        ft.Container(width=10),
                        create_custom_input(ft.Icons.PERSON_OUTLINE, "Last Name", "Ahmad", expand=True),
                    ]
                )
            )
        
        form_controls.append(
            create_custom_input(ft.Icons.EMAIL_OUTLINED, "Email Address", "micahmad@potarastudio.com")
        )
        # Re-create password field so it gets its own fresh state/refs
        form_controls.append(
            create_custom_input(ft.Icons.LOCK_OUTLINE, "Password", "mic4hmad#", is_password=True)
        )

        form_content_ref.current.controls = form_controls
        action_button_text_ref.current.value = "Login" if is_login else "Register"
        divider_text_ref.current.value = "Or login with" if is_login else "Or register with"

        # Animate form back to center
        if form_container_ref.current is not None:
            form_container_ref.current.offset = ft.Offset(0, 0)

        page.update()

    # --- Layout ---
    header_section = ft.Container(
        gradient=ft.LinearGradient(
            begin=ft.Alignment(-1, -1),
            end=ft.Alignment(1, 1),
            colors=[COLOR_ACCENT, COLOR_SECONDARY],
        ),
        padding=ft.padding.only(left=24, right=24, top=30, bottom=60),
        content=ft.Column(
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            controls=[
                ft.Text(
                    "Lakb.ai",
                    size=50,
                    weight=ft.FontWeight.BOLD,
                    color=COLOR_TEXT,
                    text_align=ft.TextAlign.CENTER,
                ),
                ft.Container(height=16),
                ft.Container(
                    alignment=ft.alignment.top_left,
                    content=ft.Column(
                        spacing=6,
                        horizontal_alignment=ft.CrossAxisAlignment.START,
                        controls=[
                            ft.Text(
                                "Set up your Lakb.ai account",
                                size=20,  # text size 2 (approx. h2)
                                weight=ft.FontWeight.BOLD,
                                color=COLOR_TEXT,
                            ),
                            ft.Text(
                                "Sign up to enjoy the best itenerary experience!",
                                size=13,
                                color=COLOR_TEXT,
                            ),
                        ],
                    ),
                ),
            ],
        ),
    )

    tab_switch = ft.Container(
        bgcolor=COLOR_SECONDARY if not is_dark_mode else COLOR_ACCENT,
        border_radius=30,
        padding=5,
        content=ft.Row(
            controls=[
                ft.Container(
                    ref=login_tab_ref,
                    data="login",
                    expand=True,
                    bgcolor=COLOR_PRIMARY,
                    padding=10,
                    border_radius=25,
                    shadow=ft.BoxShadow(blur_radius=5, color=ft.Colors.with_opacity(0.1, "black")),
                    alignment=ft.alignment.center,
                    content=ft.Text(
                        "Login",
                        color=COLOR_SURFACE,
                        weight=ft.FontWeight.BOLD,
                    ),
                    on_click=toggle_view,
                ),
                ft.Container(
                    ref=register_tab_ref,
                    data="register",
                    expand=True,
                    padding=10,
                    border_radius=25,
                    border=ft.border.all(1, COLOR_PRIMARY),
                    alignment=ft.alignment.center,
                    content=ft.Text(
                        "Register",
                        color=COLOR_TEXT,
                        weight=ft.FontWeight.BOLD,
                    ),
                    on_click=toggle_view,
                ),
            ]
        ),
    )

    dynamic_form = ft.Column(
        ref=form_content_ref,
        controls=[
            create_custom_input(ft.Icons.EMAIL_OUTLINED, "Email Address", "micahmad@potarastudio.com"),
            create_custom_input(ft.Icons.LOCK_OUTLINE, "Password", "mic4hmad#", is_password=True),
        ],
    )

    # Wrapper with slide animation for form & related content
    form_container = ft.Container(
        ref=form_container_ref,
        animate=ft.Animation(250, ft.AnimationCurve.EASE_IN_OUT),
        offset=ft.Offset(0, 0),
        content=dynamic_form,
    )

    main_content = ft.Column(
        controls=[
            tab_switch,
            ft.Container(height=20),
            form_container,
            ft.Row(
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                controls=[
                    ft.Row(
                        controls=[
                            ft.Checkbox(
                                value=False,
                                fill_color=COLOR_PRIMARY,
                            ),
                            ft.Text(
                                "Remember me",
                                size=12,
                                color=COLOR_TEXT,
                                weight=ft.FontWeight.W_500,
                            ),
                        ]
                    ),
                    ft.TextButton(
                        "Forgot Password?",
                        style=ft.ButtonStyle(color=COLOR_PRIMARY),
                        on_click=dummy_function,
                    ),
                ]
            ),
            ft.Container(height=10),
            ft.Container(
                width=float("inf"),
                padding=15,
                bgcolor=COLOR_PRIMARY,
                border_radius=30,
                alignment=ft.alignment.center,
                on_click=go_to_home,
                content=ft.Text(
                    ref=action_button_text_ref,
                    value="Login",
                    color=COLOR_SURFACE,
                    size=16,
                    weight=ft.FontWeight.BOLD,
                ),
            ),
            ft.Container(height=20),
            ft.Row(
                alignment=ft.MainAxisAlignment.CENTER,
                controls=[
                    ft.Container(height=1, expand=True, bgcolor=COLOR_SECONDARY),
                    ft.Text(
                        ref=divider_text_ref,
                        value="Or login with",
                        color=COLOR_SECONDARY,
                        size=12,
                    ),
                    ft.Container(height=1, expand=True, bgcolor=COLOR_SECONDARY),
                ]
            ),
            ft.Container(height=20),
            ft.Row(
                controls=[
                    create_social_button("Google", icon_src="https://upload.wikimedia.org/wikipedia/commons/5/53/Google_%22G%22_Logo.svg", is_image=True),
                    ft.Container(width=15),
                    create_social_button("Facebook", icon_src=ft.Icons.FACEBOOK, icon_color="#1877F2", is_image=False)
                ]
            )
        ]
    )

    white_sheet = ft.Container(
        bgcolor=COLOR_SURFACE,
        expand=True,
        border_radius=ft.border_radius.only(top_left=30, top_right=30),
        padding=ft.padding.all(25),
        content=ft.Column(
            scroll=ft.ScrollMode.AUTO,
            expand=True,
            controls=[main_content],
        ),
    )

    layout = ft.SafeArea(
        expand=True,
        content=ft.Column(
            spacing=0,
            expand=True,
            controls=[header_section, white_sheet]
        )
    )

    page.add(layout)


if __name__ == "__main__":
    ft.app(target=main)