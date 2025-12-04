import flet as ft
from .app_config import configure_page


def main(page: ft.Page):
    # Device / window configuration (centralized in app_config)
    configure_page(page, title="Login/Register UI")

    # --- Theme Configuration (Matching home_view.py) ---
    # Light Theme
    page.theme = ft.Theme(
        color_scheme=ft.ColorScheme(
            background="#fafdfc",
            on_background="#091a13",
            primary="#46bd8d",
            secondary="#95cbd9",
            tertiary="#76a2ce",
            surface="#FFFFFF",
            on_surface="#091a13",
            on_surface_variant="#5f6368",
            outline="#95cbd9", # Using secondary color for outlines
        ),
        font_family="Poppins",
        page_transitions=ft.PageTransitionsTheme(
            android=ft.PageTransitionTheme.NONE,
            ios=ft.PageTransitionTheme.NONE,
            macos=ft.PageTransitionTheme.NONE,
            linux=ft.PageTransitionTheme.NONE,
            windows=ft.PageTransitionTheme.NONE,
        ),
    )

    # Dark Theme
    page.dark_theme = ft.Theme(
        color_scheme=ft.ColorScheme(
            background="#010403",
            on_background="#e4f6ef",
            primary="#42b889",
            secondary="#265c69",
            tertiary="#315c87",
            surface="#12161C",
            on_surface="#e4f6ef",
            on_surface_variant="#a0b3af",
            outline="#265c69", # Using secondary color for outlines
        ),
        font_family="Poppins",
        page_transitions=ft.PageTransitionsTheme(
            android=ft.PageTransitionTheme.NONE,
            ios=ft.PageTransitionTheme.NONE,
            macos=ft.PageTransitionTheme.NONE,
            linux=ft.PageTransitionTheme.NONE,
            windows=ft.PageTransitionTheme.NONE,
        ),
    )

    # Set initial background color to follow theme
    page.bgcolor = "background"

    # --- Fonts Setup ---
    page.fonts = {
        "Courgette": "https://github.com/google/fonts/raw/main/ofl/courgette/Courgette-Regular.ttf",
        "Poppins": "https://github.com/google/fonts/raw/main/ofl/poppins/Poppins-Regular.ttf",
        "PoppinsBold": "https://github.com/google/fonts/raw/main/ofl/poppins/Poppins-Bold.ttf",
        "Roboto Mono": "https://github.com/google/fonts/raw/main/apache/robotomono/RobotoMono-Regular.ttf",
    }

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
    def create_custom_input(icon_name, label, placeholder="", is_password=False, expand=False):
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
                icon_color="secondary",
                icon_size=20,
                on_click=toggle_password_view,
                style=ft.ButtonStyle(
                    padding=0,
                    overlay_color=ft.Colors.TRANSPARENT,
                ),
            )

        return ft.Container(
            border=ft.border.all(1, "outline"),
            border_radius=12,
            bgcolor="surface",
            padding=ft.padding.symmetric(horizontal=16, vertical=5),
            margin=ft.margin.only(bottom=16),
            expand=expand,
            content=ft.Row(
                controls=[
                    ft.Icon(icon_name, color="primary", size=22),
                    ft.Container(width=12),
                    ft.Column(
                        spacing=2,
                        alignment=ft.MainAxisAlignment.CENTER,
                        expand=True,
                        controls=[
                            ft.Text(label, size=11, color="secondary", weight=ft.FontWeight.W_500),
                            ft.TextField(
                                ref=input_ref,
                                value=placeholder,
                                password=is_password,
                                border=ft.InputBorder.NONE,
                                content_padding=ft.padding.only(bottom=2),
                                text_style=ft.TextStyle(
                                    size=14,
                                    weight=ft.FontWeight.W_600,
                                    color="onSurface",
                                ),
                                height=35,
                                can_reveal_password=False,
                                hint_text=f"Enter {label.lower()}",
                                hint_style=ft.TextStyle(color=ft.Colors.with_opacity(0.5, "secondary"), size=14)
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
            padding=12,
            border=ft.border.all(1, ft.Colors.with_opacity(0.3, "secondary")),
            border_radius=12,
            on_click=dummy_function,
            content=ft.Row(
                alignment=ft.MainAxisAlignment.CENTER,
                controls=[
                    content_icon,
                    ft.Container(width=8),
                    ft.Text(text, color="onSurface", weight=ft.FontWeight.W_600, size=13),
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
        # Reset both
        for tab in [login_tab_ref.current, register_tab_ref.current]:
            tab.bgcolor = ft.Colors.TRANSPARENT
            tab.content.color = ft.Colors.with_opacity(0.7, "onSurface")
            tab.shadow = None
        
        # Activate selected
        active_tab = login_tab_ref.current if is_login else register_tab_ref.current
        active_tab.bgcolor = "surface"
        active_tab.content.color = "primary"
        active_tab.shadow = ft.BoxShadow(
            blur_radius=10,
            color=ft.Colors.with_opacity(0.1, "#000000"),
            offset=ft.Offset(0, 2)
        )

        active_tab.update()
        if not is_login:
             login_tab_ref.current.update()
        else:
             register_tab_ref.current.update()


        # Small slide animation for form container (no fade)
        if form_container_ref.current is not None:
            # Start slightly off-screen to left/right depending on direction
            form_container_ref.current.offset = ft.Offset(
                -0.05 if is_login else 0.05, 0
            )
            form_container_ref.current.update()

        # Form Content Updates
        form_controls = []
        if not is_login: # REGISTER
            form_controls.append(
                ft.Row(
                    controls=[
                        create_custom_input(ft.Icons.PERSON_OUTLINE, "First Name", "", expand=True),
                        ft.Container(width=10),
                        create_custom_input(ft.Icons.PERSON_OUTLINE, "Last Name", "", expand=True),
                    ]
                )
            )
        
        form_controls.append(
            create_custom_input(ft.Icons.EMAIL_OUTLINED, "Email Address", "")
        )
        # Re-create password field so it gets its own fresh state/refs
        form_controls.append(
            create_custom_input(ft.Icons.LOCK_OUTLINE, "Password", "", is_password=True)
        )

        form_content_ref.current.controls = form_controls
        action_button_text_ref.current.value = "Login" if is_login else "Register"
        divider_text_ref.current.value = "Or login with" if is_login else "Or register with"

        # Animate form back to center
        if form_container_ref.current is not None:
            form_container_ref.current.offset = ft.Offset(0, 0)

        page.update()

    # --- Layout ---
    
    # Redesigned Header - Cleaner, no harsh gradient
    header_section = ft.Container(
        bgcolor="background",
        padding=ft.padding.only(left=24, right=24, top=60, bottom=20),
        content=ft.Column(
            horizontal_alignment=ft.CrossAxisAlignment.START,
            controls=[
                ft.Text(
                    "Lakb.ai",
                    size=32,
                    weight=ft.FontWeight.BOLD,
                    color="primary",
                    font_family="Roboto Mono" 
                ),
                ft.Container(height=10),
                ft.Text(
                    "Welcome Back!",
                    size=28,
                    weight=ft.FontWeight.BOLD,
                    color="onBackground",
                ),
                ft.Text(
                    "Plan your next adventure with ease.",
                    size=16,
                    color=ft.Colors.with_opacity(0.7, "onBackground"),
                ),
            ],
        ),
    )

    # Redesigned Tab Switch - Segmented Control Style
    tab_switch = ft.Container(
        bgcolor=ft.Colors.with_opacity(0.05, "onSurface"),
        border_radius=16,
        padding=4,
        margin=ft.margin.symmetric(horizontal=24),
        content=ft.Row(
            spacing=0,
            controls=[
                ft.Container(
                    ref=login_tab_ref,
                    data="login",
                    expand=True,
                    bgcolor="surface", # Default active
                    padding=10,
                    border_radius=12,
                    shadow=ft.BoxShadow(blur_radius=10, color=ft.Colors.with_opacity(0.1, "#000000"), offset=ft.Offset(0, 2)),
                    alignment=ft.alignment.center,
                    content=ft.Text(
                        "Login",
                        color="primary",
                        weight=ft.FontWeight.BOLD,
                        size=14
                    ),
                    on_click=toggle_view,
                    animate=ft.Animation(200, ft.AnimationCurve.EASE_OUT),
                ),
                ft.Container(
                    ref=register_tab_ref,
                    data="register",
                    expand=True,
                    padding=10,
                    border_radius=12,
                    alignment=ft.alignment.center,
                    content=ft.Text(
                        "Register",
                        color=ft.Colors.with_opacity(0.7, "onSurface"),
                        weight=ft.FontWeight.BOLD,
                        size=14
                    ),
                    on_click=toggle_view,
                    animate=ft.Animation(200, ft.AnimationCurve.EASE_OUT),
                ),
            ]
        ),
    )

    dynamic_form = ft.Column(
        ref=form_content_ref,
        controls=[
            create_custom_input(ft.Icons.EMAIL_OUTLINED, "Email Address", ""),
            create_custom_input(ft.Icons.LOCK_OUTLINE, "Password", "", is_password=True),
        ],
    )

    # Wrapper with slide animation for form & related content
    form_container = ft.Container(
        ref=form_container_ref,
        animate=ft.Animation(300, ft.AnimationCurve.EASE_OUT_BACK),
        offset=ft.Offset(0, 0),
        padding=ft.padding.symmetric(horizontal=24),
        content=dynamic_form,
    )

    main_content = ft.Column(
        controls=[
            tab_switch,
            ft.Container(height=30),
            form_container,
            ft.Container(
                padding=ft.padding.symmetric(horizontal=24),
                content=ft.Row(
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    controls=[
                        ft.Row(
                            controls=[
                                ft.Checkbox(
                                    value=False,
                                    fill_color="primary",
                                ),
                                ft.Text(
                                    "Remember me",
                                    size=13,
                                    color="onSurface",
                                    weight=ft.FontWeight.W_500,
                                ),
                            ]
                        ),
                        ft.TextButton(
                            "Forgot Password?",
                            style=ft.ButtonStyle(color="primary"),
                            on_click=dummy_function,
                        ),
                    ]
                )
            ),
            ft.Container(height=20),
            ft.Container(
                margin=ft.margin.symmetric(horizontal=24),
                width=float("inf"),
                height=50,
                bgcolor="primary",
                border_radius=14,
                alignment=ft.alignment.center,
                on_click=go_to_home,
                shadow=ft.BoxShadow(
                    blur_radius=15,
                    color=ft.Colors.with_opacity(0.4, "primary"),
                    offset=ft.Offset(0, 5)
                ),
                content=ft.Text(
                    ref=action_button_text_ref,
                    value="Login",
                    color="#FFFFFF",
                    size=16,
                    weight=ft.FontWeight.BOLD,
                ),
            ),
            ft.Container(height=30),
            ft.Row(
                alignment=ft.MainAxisAlignment.CENTER,
                controls=[
                    ft.Container(height=1, width=60, bgcolor=ft.Colors.with_opacity(0.2, "secondary")),
                    ft.Text(
                        ref=divider_text_ref,
                        value="Or login with",
                        color=ft.Colors.with_opacity(0.6, "secondary"),
                        size=12,
                        weight=ft.FontWeight.W_500
                    ),
                    ft.Container(height=1, width=60, bgcolor=ft.Colors.with_opacity(0.2, "secondary")),
                ]
            ),
            ft.Container(height=20),
            ft.Container(
                padding=ft.padding.symmetric(horizontal=24),
                content=ft.Row(
                    controls=[
                        create_social_button("Google", icon_src="https://upload.wikimedia.org/wikipedia/commons/5/53/Google_%22G%22_Logo.svg", is_image=True),
                        ft.Container(width=15),
                        create_social_button("Facebook", icon_src=ft.Icons.FACEBOOK, icon_color="#1877F2", is_image=False)
                    ]
                )
            )
        ]
    )

    # Use a scrollable column for the whole page to handle small screens
    layout = ft.SafeArea(
        expand=True,
        content=ft.Column(
            expand=True,
            scroll=ft.ScrollMode.AUTO,
            controls=[
                header_section,
                main_content,
                ft.Container(height=20) # Bottom spacer
            ],
            spacing=0
        )
    )

    page.add(layout)


if __name__ == "__main__":
    ft.app(target=main)