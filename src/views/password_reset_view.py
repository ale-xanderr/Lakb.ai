import flet as ft
import re
from core.config import configure_page
from services.auth_service import AuthService


def main(page: ft.Page):
    # Device / window configuration (centralized in app_config)
    configure_page(page, title="Reset Password")

    # --- Theme Configuration (Matching login_view.py) ---
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
            outline="#95cbd9",
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
            outline="#265c69",
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
        "Courgette": "/fonts/Courgette-Regular.ttf",
        "Poppins": "/fonts/Poppins-Regular.ttf",
        "PoppinsBold": "/fonts/Poppins-Bold.ttf",
        "Roboto Mono": "/fonts/RobotoMono-Regular.ttf",
    }

    def go_back(e):
        """Navigate back to login view"""
        from .login_view import main as login_main
        page.clean()
        login_main(page)

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

    # --- Custom Input Builder ---
    def create_custom_input(icon_name, label, ref=None, placeholder="", is_password=False):
        input_ref = ref if ref else ft.Ref[ft.TextField]()
        eye_icon_ref = ft.Ref[ft.IconButton]()

        def toggle_password_view(e):
            input_ref.current.password = not input_ref.current.password
            eye_icon_ref.current.icon = (
                ft.Icons.VISIBILITY_OFF if not input_ref.current.password else ft.Icons.VISIBILITY
            )
            input_ref.current.update()
            eye_icon_ref.current.update()

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

    # --- Refs for form fields ---
    reset_token_ref = ft.Ref[ft.TextField]()
    email_ref = ft.Ref[ft.TextField]()
    new_password_ref = ft.Ref[ft.TextField]()
    confirm_password_ref = ft.Ref[ft.TextField]()

    # --- Password Strength Indicators ---
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
                    size=18,
                ),
                ft.Text(
                    label,
                    size=12,
                    color=text_color,
                    weight=ft.FontWeight.W_500 if met else ft.FontWeight.NORMAL,
                ),
            ],
            spacing=8,
        )

    # Create initial strength indicators
    strength_column = ft.Column(
        spacing=8,
        controls=[
            build_strength_indicator("Contains a number", False, strength_indicators["number"]),
            build_strength_indicator("Contains a symbol", False, strength_indicators["symbol"]),
            build_strength_indicator("Contains a lowercase letter", False, strength_indicators["lowercase"]),
            build_strength_indicator("Contains an uppercase letter", False, strength_indicators["uppercase"]),
            build_strength_indicator("Length is at least 8 characters", False, strength_indicators["length"]),
        ],
    )

    def update_password_strength(e):
        """Update password strength indicators"""
        if not new_password_ref.current:
            return
        password = new_password_ref.current.value or ""
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
        
        # Update reset button state
        update_reset_button_state()

    def update_reset_button_state(e=None):
        """Enable/disable reset button based on form validation"""
        if not (new_password_ref.current and confirm_password_ref.current and 
                reset_token_ref.current and email_ref.current):
            # If refs aren't ready, keep button disabled
            reset_button.disabled = True
            if reset_button.style:
                reset_button.style.bgcolor = ft.Colors.with_opacity(0.5, "primary")
            reset_button.update()
            return
            
        password = new_password_ref.current.value or ""
        confirm_password = confirm_password_ref.current.value or ""
        token = reset_token_ref.current.value or ""
        email = email_ref.current.value or ""
        
        strength = check_password_strength(password)
        passwords_match = password == confirm_password and password != ""
        all_fields_filled = token.strip() != "" and email.strip() != "" and password != "" and confirm_password != ""
        
        can_reset = strength["all_met"] and passwords_match and all_fields_filled
        
        reset_button.disabled = not can_reset
        # Update button style based on state
        if reset_button.style:
            if can_reset:
                reset_button.style.bgcolor = "primary"
                reset_button.style.color = "white"
            else:
                reset_button.style.bgcolor = ft.Colors.with_opacity(0.5, "primary")
                reset_button.style.color = ft.Colors.with_opacity(0.7, "white")
        reset_button.update()

    def handle_reset_password(e):
        """Handle password reset submission"""
        if not (reset_token_ref.current and email_ref.current and 
                new_password_ref.current and confirm_password_ref.current):
            return
            
        token = reset_token_ref.current.value
        email = email_ref.current.value
        new_password = new_password_ref.current.value
        confirm_password = confirm_password_ref.current.value
        
        # Validate fields
        if not token or not email or not new_password or not confirm_password:
            page.open(ft.SnackBar(
                ft.Text("Please fill in all fields"),
                bgcolor="#FF4B4B",
                duration=3000
            ))
            page.update()
            return
        
        # Validate password match
        if new_password != confirm_password:
            page.open(ft.SnackBar(
                ft.Text("Passwords do not match"),
                bgcolor="#FF4B4B",
                duration=3000
            ))
            page.update()
            return
        
        # Validate password strength
        strength = check_password_strength(new_password)
        if not strength["all_met"]:
            page.open(ft.SnackBar(
                ft.Text("Password does not meet all requirements"),
                bgcolor="#FF4B4B",
                duration=3000
            ))
            page.update()
            return
        
        # Disable button during processing
        reset_button.disabled = True
        reset_button.text = ""
        # Create loading content
        loading_content = ft.Row(
            controls=[
                ft.ProgressRing(width=16, height=16, stroke_width=2, color="white"),
                ft.Container(width=8),
                ft.Text("Resetting...", color="#FFFFFF", size=16, weight=ft.FontWeight.BOLD),
            ],
            alignment=ft.MainAxisAlignment.CENTER,
            tight=True,
        )
        reset_button.content = loading_content
        reset_button.update()
        
        # Attempt password reset
        try:
            auth = AuthService()
            auth.verify_reset_token_and_update_password(email, token, new_password)
            
            # Show success dialog
            def show_success_dialog():
                dialog = ft.AlertDialog(
                    modal=True,
                    title=ft.Row(
                        controls=[
                            ft.Icon(ft.Icons.CHECK_CIRCLE, color="primary", size=24),
                            ft.Container(width=8),
                            ft.Text(
                                "Password Reset Successful",
                                size=18,
                                weight=ft.FontWeight.BOLD,
                            ),
                        ],
                        spacing=0,
                        tight=True,
                        wrap=False,
                    ),
                    content=ft.Column(
                        controls=[
                            ft.Text(
                                "Your password has been successfully reset.",
                                size=14,
                                color="onSurface",
                            ),
                            ft.Container(height=8),
                            ft.Text(
                                "You can now proceed to login with your new password.",
                                size=14,
                                color="onSurface",
                            ),
                        ],
                        tight=True,
                        spacing=0,
                        width=280,
                    ),
                    actions=[
                        ft.ElevatedButton(
                            "Proceed to Login",
                            on_click=lambda e: (page.close(dialog), go_back(None)),
                            style=ft.ButtonStyle(
                                color="white",
                                bgcolor="primary",
                                padding=ft.padding.symmetric(horizontal=24, vertical=12),
                            ),
                        ),
                    ],
                    actions_alignment=ft.MainAxisAlignment.END,
                )
                page.open(dialog)
            
            show_success_dialog()
            page.update()
            
        except Exception as ex:
            print(f"Password reset error: {ex}")
            error_msg = str(ex) if ex else "Unknown error"
            page.open(ft.SnackBar(
                ft.Text(f"Password reset failed: {error_msg}"),
                bgcolor="#FF4B4B",
                duration=5000
            ))
            page.update()
            
            # Re-enable button
            reset_button.disabled = False
            reset_button.text = "Reset Password"
            reset_button.content = None  # Reset to default content
            reset_button.update()
            # Re-check button state
            update_reset_button_state()

    # --- Header with Back Button ---
    header = ft.Container(
        padding=ft.padding.symmetric(horizontal=24, vertical=16),
        content=ft.Row(
            controls=[
                ft.IconButton(
                    icon=ft.Icons.ARROW_BACK,
                    icon_color="onBackground",
                    on_click=go_back,
                    tooltip="Back",
                ),
                ft.Text(
                    "Reset Password",
                    size=24,
                    weight=ft.FontWeight.BOLD,
                    color="onBackground",
                ),
            ],
            spacing=12,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
        ),
    )

    # --- Main Content ---
    title_section = ft.Container(
        padding=ft.padding.symmetric(horizontal=24),
        content=ft.Column(
            spacing=8,
            controls=[
                ft.Text(
                    "Create New Password",
                    size=28,
                    weight=ft.FontWeight.BOLD,
                    color="onBackground",
                ),
                ft.Text(
                    "Enter the reset token from your email and set a new password",
                    size=14,
                    color=ft.Colors.with_opacity(0.7, "onBackground"),
                ),
            ],
        ),
    )

    # Form fields
    token_input = create_custom_input(ft.Icons.VERIFIED_USER, "Reset Token", ref=reset_token_ref)
    email_input = create_custom_input(ft.Icons.EMAIL_OUTLINED, "Email Address", ref=email_ref)
    new_password_input = create_custom_input(
        ft.Icons.LOCK_OUTLINE,
        "New Password",
        ref=new_password_ref,
        is_password=True
    )
    confirm_password_input = create_custom_input(
        ft.Icons.LOCK_OUTLINE,
        "Confirm Password",
        ref=confirm_password_ref,
        is_password=True
    )

    # Add on_change handlers for form fields
    def on_password_change(e):
        update_password_strength(e)
        update_reset_button_state()

    new_password_ref.current.on_change = on_password_change
    confirm_password_ref.current.on_change = update_reset_button_state
    reset_token_ref.current.on_change = update_reset_button_state
    email_ref.current.on_change = update_reset_button_state

    form_section = ft.Container(
        padding=ft.padding.symmetric(horizontal=24, vertical=20),
        content=ft.Column(
            controls=[
                token_input,
                email_input,
                new_password_input,
                confirm_password_input,
            ],
        ),
    )

    # Password strength section
    strength_section = ft.Container(
        padding=ft.padding.symmetric(horizontal=24, vertical=10),
        content=ft.Column(
            spacing=12,
            controls=[
                ft.Text(
                    "Password Requirements",
                    size=14,
                    weight=ft.FontWeight.W_600,
                    color="onSurface",
                ),
                strength_column,
            ],
        ),
    )

    # Reset button - using ElevatedButton for proper disabled state
    reset_button = ft.ElevatedButton(
        "Reset Password",
        on_click=handle_reset_password,
        disabled=True,
        style=ft.ButtonStyle(
            color="white",
            bgcolor="primary",
            padding=ft.padding.symmetric(horizontal=40, vertical=16),
            text_style=ft.TextStyle(
                size=16,
                weight=ft.FontWeight.BOLD,
            ),
            shape=ft.RoundedRectangleBorder(radius=14),
            elevation=5,
        ),
        width=float("inf"),
        height=50,
    )
    
    # Wrap button in container for margin and styling
    reset_button_container = ft.Container(
        margin=ft.margin.symmetric(horizontal=24, vertical=20),
        content=reset_button,
    )

    # Main layout
    layout = ft.SafeArea(
        expand=True,
        content=ft.Column(
            expand=True,
            scroll=ft.ScrollMode.AUTO,
            controls=[
                header,
                title_section,
                form_section,
                strength_section,
                reset_button_container,
                ft.Container(height=20),  # Bottom spacer
            ],
            spacing=0,
        ),
    )

    page.add(layout)
    
    # Initial button state update after page is set up
    # Use a small delay to ensure refs are ready
    import threading
    import time
    def initial_update():
        time.sleep(0.1)  # Small delay to ensure refs are populated
        update_reset_button_state()
    
    thread = threading.Thread(target=initial_update, daemon=True)
    thread.start()


if __name__ == "__main__":
    ft.app(target=main)
