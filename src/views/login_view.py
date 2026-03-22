import flet as ft
import re
from core.config import configure_page
from services.auth_service import AuthService
from state import AuthStateController


def reload_login_view(page: ft.Page):
    """
    Helper function to robustly reload the login view, ensuring all previous state
    (views, controls, event handlers) is cleared.
    """
    print("Reloading login view...")
    try:
        page.views.clear()
        page.controls.clear()
        page.on_route_change = None
        page.on_view_pop = None
        page.clean()
        page.route = "/login"
        page.update()
        main(page)
    except Exception as e:
        print(f"Error reloading login view: {e}")
        # Last resort fallback
        main(page)


def main(page: ft.Page):
    """
    Main entry point for the Login/Register View.
    Handles user authentication, registration, and navigation to other auth-related views.
    
    Args:
        page: The Flet page instance.
    """
    # Device / window configuration (centralized in app_config)
    configure_page(page, title="Login/Register UI")

    # --- Theme Configuration (Matching home_view.py) ---
    # Use centralized theme configuration
    from core.theme import configure_theme
    configure_theme(page)
    
    # Add extra font for login view
    page.fonts["Roboto Mono"] = "/fonts/RobotoMono-Regular.ttf"

    # --- Password Strength Checker ---
    def check_password_strength(password: str) -> dict:
        """Check password strength and return criteria status"""
        has_number = bool(re.search(r'\d', password))
        has_symbol = bool(re.search(r'[!@#$%^&*(),.?":{}|<>]', password))
        has_lowercase = bool(re.search(r'[a-z]', password))
        has_uppercase = bool(re.search(r'[A-Z]', password))
        has_length = len(password) >= 8
        
        return {
            "has_number": has_number,
            "has_symbol": has_symbol,
            "has_lowercase": has_lowercase,
            "has_uppercase": has_uppercase,
            "has_length": has_length,
            "all_met": has_number and has_symbol and has_lowercase and has_uppercase and has_length
        }

    def dummy_function(e):
        # Placeholder for buttons that don't do anything yet
        pass

    def go_to_password_reset(e):
        """Navigate to send token view"""
        from .send_token_view import main as send_token_main
        
        # Clear any view stack or route handlers
        try:
            if hasattr(page, 'views') and isinstance(page.views, list):
                page.views.clear()
        except Exception:
            pass

        try:
            if hasattr(page, 'on_route_change'):
                page.on_route_change = None
        except Exception:
            pass
        
        try:
            if hasattr(page, 'on_view_pop'):
                page.on_view_pop = None
        except Exception:
            pass

        try:
            page.controls.clear()
        except Exception:
            pass
        
        try:
            page.clean()
        except Exception:
            pass
        
        try:
            page.route = "/"
        except Exception:
            pass
        
        try:
            send_token_main(page)
            page.update()
        except Exception as ex:
            print(f"Error launching send token view: {ex}")

    def go_to_home(e):
        """
        After login/register, clear the login page and show the home view.
        """
        from .home_view import main as home_main

        # Clear stale route handler so home_view can install its own cleanly.
        page.on_route_change = None
        page.clean()
        home_main(page)

    # --- UPDATED INPUT BUILDER WITH PASSWORD TOGGLE ---
    def create_custom_input(icon_name, label, ref=None, placeholder="", is_password=False, expand=False):
        # Refs for interactivity
        input_ref = ref if ref else ft.Ref[ft.TextField]()
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

    def handle_auth_action(e):
        # Determine mode
        is_login = action_button_text_ref.current.value == "Login"
        
        email = email_input_ref.current.value
        password = password_input_ref.current.value
        
        if not email or not password:
             page.open(ft.SnackBar(ft.Text("Please enter both email and password")))
             page.update()
             return

        auth = AuthService()
        try:
            if is_login:
                 auth.sign_in_with_password(email, password)
                 # Save session to storage for persistence
                 auth.save_session_to_storage(page)
                 
                 # Handle "Remember me" - save or clear email in client_storage
                 try:
                     if hasattr(page, 'client_storage'):
                         if remember_me_ref.current and remember_me_ref.current.value:
                             page.client_storage.set("remembered_email", email)
                         else:
                             page.client_storage.remove("remembered_email")
                 except Exception as rem_ex:
                     print(f"Error handling remember me: {rem_ex}")
                 
                 # Update auth state controller to clear guest status
                 from state import AuthStateController
                 auth_state_controller = getattr(page, "_auth_state_controller", None)
                 if not auth_state_controller:
                     auth_state_controller = AuthStateController(page)
                     page._auth_state_controller = auth_state_controller
                 
                 # Get user and set authenticated state
                 user = auth.get_user()
                 if user:
                     auth_state_controller.set_authenticated(user)
                 
                 # Navigate to home after successful login
                 go_to_home(e)
            else:
                 # REGISTRATION FLOW
                 first_name = first_name_ref.current.value
                 last_name = last_name_ref.current.value
                 if not first_name or not last_name:
                      page.open(ft.SnackBar(ft.Text("Please enter your name")))
                      page.update()
                      return
                 
                 # Check password strength
                 strength = check_password_strength(password)
                 if not strength["all_met"]:
                      page.open(ft.SnackBar(
                          ft.Text("Password does not meet all security requirements"),
                          bgcolor="#FF4B4B",
                          duration=3000
                      ))
                      page.update()
                      return
                 
                 # Sign up with Supabase - this will send a confirmation email
                 auth.sign_up(email, password, data={"first_name": first_name, "last_name": last_name}, page=page)
                 
                 # Show message to check email for confirmation
                 snackbar = ft.SnackBar(
                     content=ft.Text(
                         "Registration successful! Please check your email to verify your account.",
                         color="white"
                     ),
                     bgcolor="primary",
                     duration=5000,  # Show for 5 seconds
                 )
                 page.open(snackbar)
                 page.update()
                 
                 # DON'T navigate to home - user needs to verify email first
                 # After email verification, they can login normally
            
        except Exception as ex:
            print(f"Auth error: {ex}")
            # Ensure safe string conversion
            error_msg = str(ex) if ex else "Unknown error"
            page.open(ft.SnackBar(ft.Text(f"Authentication failed: {error_msg}")))
            page.update()

    def login_with_google(e):
        try:
            auth = AuthService()
            url = auth.sign_in_with_google(page)
            if not url:
                print("Error: Could not initiate Google Sign-In. Check Supabase credentials.")
                return

            # CRITICAL: Install the OAuth callback handler BEFORE opening the browser.
            #
            # After logout, perform_logout() sets page.on_route_change = None to
            # tear down the home_view router.  That means when Google redirects back
            # with `lakbai://oauth_callback?code=…`, Flet fires the route-change
            # event but nobody is listening — the auth code is silently discarded
            # and the user is left stranded on the login screen.
            #
            # We register a one-shot handler here so the redirect is always caught,
            # no matter how many times the user has logged in/out.
            def _oauth_callback_handler(ev):
                route = page.route or ""
                print(f"DEBUG [oauth_callback_handler]: route = {route}")

                # Only act on OAuth redirect routes.
                is_oauth = (
                    "/api/oauth/redirect" in route
                    or "/oauth_callback" in route
                    or "/auth/callback" in route
                    or "lakbai://" in route
                    or "?code=" in route
                    or "#code=" in route
                    or (route.startswith("/") and "code=" in route)
                )
                if not is_oauth:
                    return  # Not our route — ignore

                # Remove ourselves immediately so we never fire twice.
                page.on_route_change = None

                result = auth.handle_auth_callback(route, page)

                if result["success"]:
                    user = result["user"]

                    # Update / create auth state controller.
                    auth_ctrl = getattr(page, "_auth_state_controller", None)
                    if not auth_ctrl:
                        from state import AuthStateController
                        auth_ctrl = AuthStateController(page)
                        page._auth_state_controller = auth_ctrl
                    auth_ctrl.set_authenticated(user)

                    # Refresh favorites in background.
                    try:
                        from state import ServiceManager
                        sm = ServiceManager()
                        favs = sm.favorites_service
                        import threading
                        threading.Thread(
                            target=lambda: favs.get_favorites(force_refresh=True),
                            daemon=True
                        ).start()
                    except Exception as fav_err:
                        print(f"Warning: Could not refresh favorites: {fav_err}")

                    # Navigate to home.
                    page.clean()
                    page.on_route_change = None  # ensure clean slate for home_view
                    from .home_view import main as home_main
                    home_main(page)

                else:
                    error_msg = result.get("error", "Authentication failed")
                    print(f"OAuth callback error: {error_msg}")
                    try:
                        page.open(ft.SnackBar(
                            ft.Text(f"Sign-in failed: {error_msg}"),
                            duration=4000,
                        ))
                        page.update()
                    except Exception:
                        pass
                    # Re-install ourselves so the user can try again.
                    page.on_route_change = _oauth_callback_handler

            # Register the one-shot handler, then open the browser.
            page.on_route_change = _oauth_callback_handler
            page.launch_url(url)

        except Exception as ex:
            print(f"Login error: {ex}")

    def login_as_guest(e):
        """Handle guest user login - allows navigation without authentication."""
        try:
            # Initialize auth state controller if not already on page
            auth_state_controller = getattr(page, "_auth_state_controller", None)
            if not auth_state_controller:
                auth_state_controller = AuthStateController(page)
                page._auth_state_controller = auth_state_controller
            
            # Set user as guest
            auth_state_controller.set_guest()
            
            # Navigate to home
            go_to_home(e)
        except Exception as ex:
            print(f"Guest login error: {ex}")
            page.open(ft.SnackBar(ft.Text(f"Error: {str(ex)}")))
            page.update()

    # Social Media Button Builder
    def create_social_button(text, icon_src=None, icon_color=None, is_image=False, on_click=dummy_function):
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
            on_click=on_click,
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

    # Refs for form fields
    email_input_ref = ft.Ref[ft.TextField]()
    password_input_ref = ft.Ref[ft.TextField]()
    first_name_ref = ft.Ref[ft.TextField]()
    last_name_ref = ft.Ref[ft.TextField]()
    remember_me_ref = ft.Ref[ft.Checkbox]()

    # --- Load remembered email from client_storage ---
    remembered_email = ""
    remember_me_checked = False
    try:
        if hasattr(page, 'client_storage'):
            stored_email = page.client_storage.get("remembered_email")
            if stored_email:
                remembered_email = stored_email
                remember_me_checked = True
    except Exception as ex:
        print(f"Error loading remembered email: {ex}")
    
    # --- Password Strength Indicators ---
    strength_indicators_visible = ft.Ref[ft.Container]()
    strength_indicators = {
        "number": ft.Ref[ft.Row](),
        "symbol": ft.Ref[ft.Row](),
        "lowercase": ft.Ref[ft.Row](),
        "uppercase": ft.Ref[ft.Row](),
        "length": ft.Ref[ft.Row](),
    }

    def build_strength_indicator(label: str, met: bool, ref: ft.Ref[ft.Row]) -> ft.Row:
        """Build a password strength indicator row"""
        icon_color = "primary" if met else "#9AA4AF"
        text_color = "onSurface" if met else "#9AA4AF"
        
        return ft.Row(
            ref=ref,
            controls=[
                ft.Icon(
                    ft.Icons.CHECK_CIRCLE if met else ft.Icons.CIRCLE_OUTLINED,
                    color=icon_color,
                    size=16,
                ),
                ft.Text(
                    label,
                    size=11,
                    color=text_color,
                    weight=ft.FontWeight.W_500 if met else ft.FontWeight.NORMAL,
                ),
            ],
            spacing=6,
        )

    def update_password_strength(e):
        """Update password strength indicators"""
        if not password_input_ref.current:
            return
        password = password_input_ref.current.value or ""
        strength = check_password_strength(password)
        
        # Update each indicator
        for key, ref in strength_indicators.items():
            met = strength[f"has_{key}"]
            icon_color = "primary" if met else "#9AA4AF"
            text_color = "onSurface" if met else "#9AA4AF"
            
            # Update the row
            row = ref.current
            if row and len(row.controls) >= 2:
                row.controls[0].icon = (
                    ft.Icons.CHECK_CIRCLE if met else ft.Icons.CIRCLE_OUTLINED
                )
                row.controls[0].color = icon_color
                row.controls[1].color = text_color
                row.controls[1].weight = ft.FontWeight.W_500 if met else ft.FontWeight.NORMAL
                row.update()

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
                        create_custom_input(ft.Icons.PERSON_OUTLINE, "First Name", ref=first_name_ref, expand=True),
                        ft.Container(width=10),
                        create_custom_input(ft.Icons.PERSON_OUTLINE, "Last Name", ref=last_name_ref, expand=True),
                    ]
                )
            )
        
        form_controls.append(
            create_custom_input(ft.Icons.EMAIL_OUTLINED, "Email Address", ref=email_input_ref)
        )
        # Re-create password field so it gets its own fresh state/refs
        password_field = create_custom_input(ft.Icons.LOCK_OUTLINE, "Password", ref=password_input_ref, is_password=True)
        form_controls.append(password_field)
        
        # Add password strength indicators for registration
        if not is_login:
            # Add on_change handler to password field for strength checking
            if password_input_ref.current:
                password_input_ref.current.on_change = update_password_strength
            
            strength_container = ft.Container(
                ref=strength_indicators_visible,
                padding=ft.padding.only(left=16, right=16, top=8, bottom=16),
                content=ft.Column(
                    spacing=10,
                    controls=[
                        ft.Text(
                            "Password Requirements",
                            size=13,
                            weight=ft.FontWeight.W_600,
                            color="onSurface",
                        ),
                        ft.Column(
                            spacing=6,
                            controls=[
                                build_strength_indicator("Contains a number", False, strength_indicators["number"]),
                                build_strength_indicator("Contains a symbol", False, strength_indicators["symbol"]),
                                build_strength_indicator("Contains a lowercase letter", False, strength_indicators["lowercase"]),
                                build_strength_indicator("Contains an uppercase letter", False, strength_indicators["uppercase"]),
                                build_strength_indicator("Length is at least 8 characters", False, strength_indicators["length"]),
                            ],
                        ),
                    ],
                ),
            )
            form_controls.append(strength_container)
        else:
            # Hide strength indicators for login
            if strength_indicators_visible.current:
                strength_indicators_visible.current.visible = False

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
            create_custom_input(ft.Icons.EMAIL_OUTLINED, "Email Address", ref=email_input_ref, placeholder=remembered_email),
            create_custom_input(ft.Icons.LOCK_OUTLINE, "Password", ref=password_input_ref, is_password=True),
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
                                    ref=remember_me_ref,
                                    value=remember_me_checked,
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
                            on_click=go_to_password_reset,
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
                on_click=handle_auth_action,
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
                    alignment=ft.MainAxisAlignment.CENTER,
                    spacing=12,
                    controls=[
                        ft.Container(
                            expand=True,
                            padding=ft.padding.symmetric(horizontal=16, vertical=12),
                            border=ft.border.all(1, ft.Colors.with_opacity(0.3, "secondary")),
                            border_radius=12,
                            on_click=login_with_google,
                            content=ft.Row(
                                alignment=ft.MainAxisAlignment.CENTER,
                                spacing=10,
                                controls=[
                                    ft.Container(
                                        width=24,
                                        height=24,
                                        bgcolor="#FFFFFF",
                                        border_radius=4,
                                        padding=2,
                                        content=ft.Image(
                                            src="/icons/google-svgrepo-com.png",
                                            width=20,
                                            height=20,
                                            fit=ft.ImageFit.CONTAIN,
                                            error_content=ft.Icon(ft.Icons.ACCOUNT_CIRCLE, size=20, color="#4285F4")
                                        ),
                                    ),
                                    ft.Text("Google", color="onSurface", weight=ft.FontWeight.W_600, size=14),
                                ],
                            ),
                        ),
                        ft.Container(
                            expand=True,
                            padding=ft.padding.symmetric(horizontal=16, vertical=12),
                            border=ft.border.all(1, ft.Colors.with_opacity(0.3, "secondary")),
                            border_radius=12,
                            on_click=login_as_guest,
                            content=ft.Row(
                                alignment=ft.MainAxisAlignment.CENTER,
                                spacing=10,
                                controls=[
                                    ft.Icon(ft.Icons.PERSON_OUTLINE, size=20, color="primary"),
                                    ft.Text("Guest User", color="onSurface", weight=ft.FontWeight.W_600, size=14),
                                ],
                            ),
                        )
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

    # If the app is using views-based routing (home_view uses page.views), render
    # the login UI as a View so it appears correctly when other code clears/uses
    # the page.views stack. Otherwise, add controls directly.
    try:
        if hasattr(page, 'views') and isinstance(page.views, list):
            from flet import View
            # Clear existing views and add login view
            try:
                page.views.clear()
            except Exception:
                pass
            page.views.append(View('/login', controls=[layout], padding=0, bgcolor='background'))
            try:
                page.update()
            except Exception:
                pass
        else:
            page.add(layout)
    except Exception:
        # Fallback: try to add directly
        try:
            page.add(layout)
        except Exception as e:
            print(f"Failed to render login layout: {e}")


if __name__ == "__main__":
    ft.app(target=main, assets_dir="assets")