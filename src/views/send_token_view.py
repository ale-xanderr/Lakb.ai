import flet as ft
from core.config import configure_page
from services.auth_service import AuthService


def main(page: ft.Page):
    # Device / window configuration (centralized in app_config)
    configure_page(page, title="Request Password Reset")

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

    def go_to_password_reset(e):
        """Navigate to password reset view"""
        from .password_reset_view import main as password_reset_main
        page.clean()
        password_reset_main(page)

    # --- Custom Input Builder ---
    def create_custom_input(icon_name, label, ref=None, placeholder=""):
        input_ref = ref if ref else ft.Ref[ft.TextField]()

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
                                border=ft.InputBorder.NONE,
                                content_padding=ft.padding.only(bottom=2),
                                text_style=ft.TextStyle(
                                    size=14,
                                    weight=ft.FontWeight.W_600,
                                    color="onSurface",
                                ),
                                height=35,
                                hint_text=f"Enter {label.lower()}",
                                hint_style=ft.TextStyle(color=ft.Colors.with_opacity(0.5, "secondary"), size=14)
                            ),
                        ],
                    ),
                ],
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
            ),
        )

    # --- Refs for form fields ---
    email_ref = ft.Ref[ft.TextField]()

    def update_send_button_state():
        """Enable/disable send button based on email input"""
        email = email_ref.current.value or "" if email_ref.current else ""
        has_email = email.strip() != ""
        
        send_button.disabled = not has_email
        send_button.bgcolor = "primary" if has_email else ft.Colors.with_opacity(0.5, "primary")
        send_button.update()

    def show_success_dialog():
        """Show dialog confirming email was sent"""
        dialog = ft.AlertDialog(
            modal=True,
            title=ft.Text("Check Your Email"),
            content=ft.Column(
                tight=True,
                controls=[
                    ft.Text(
                        "We've sent a password reset token to your email address.",
                        size=14,
                        color="onSurface",
                    ),
                    ft.Container(height=12),
                    ft.Text(
                        "Please check your inbox and follow the instructions to reset your password.",
                        size=14,
                        color="onSurface",
                    ),
                ],
            ),
            actions=[
                ft.TextButton(
                    "OK",
                    on_click=lambda e: page.close(dialog),
                ),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )
        page.open(dialog)

    def handle_send_token(e):
        """Handle send reset token request"""
        if not email_ref.current:
            return
            
        email = email_ref.current.value or ""
        
        # Validate email
        if not email or email.strip() == "":
            page.open(ft.SnackBar(
                ft.Text("Please enter your email address"),
                bgcolor="#FF4B4B",
                duration=3000
            ))
            page.update()
            return
        
        # Basic email validation
        import re
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(email_pattern, email.strip()):
            page.open(ft.SnackBar(
                ft.Text("Please enter a valid email address"),
                bgcolor="#FF4B4B",
                duration=3000
            ))
            page.update()
            return
        
        # Disable button during processing
        send_button.disabled = True
        send_button.content = ft.Row(
            controls=[
                ft.ProgressRing(width=16, height=16, stroke_width=2),
                ft.Container(width=8),
                ft.Text("Sending...", color="#FFFFFF", size=16, weight=ft.FontWeight.BOLD),
            ],
            alignment=ft.MainAxisAlignment.CENTER,
        )
        send_button.update()
        
        # Attempt to send reset token
        try:
            auth = AuthService()
            auth.reset_password_for_email(email.strip())
            
            # Success - show dialog
            show_success_dialog()
            
            # Re-enable button
            send_button.disabled = False
            send_button.content = ft.Text(
                "Send Reset Token",
                color="#FFFFFF",
                size=16,
                weight=ft.FontWeight.BOLD,
            )
            send_button.update()
            
        except Exception as ex:
            print(f"Send token error: {ex}")
            error_msg = str(ex) if ex else "Unknown error"
            
            # Show error message
            page.open(ft.SnackBar(
                ft.Text(f"Failed to send reset token: {error_msg}"),
                bgcolor="#FF4B4B",
                duration=5000
            ))
            page.update()
            
            # Re-enable button
            send_button.disabled = False
            send_button.content = ft.Text(
                "Send Reset Token",
                color="#FFFFFF",
                size=16,
                weight=ft.FontWeight.BOLD,
            )
            send_button.update()

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
                    "Forgot Password",
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
                    "Reset Your Password",
                    size=28,
                    weight=ft.FontWeight.BOLD,
                    color="onBackground",
                ),
                ft.Text(
                    "Enter your email address and we'll send you a reset token",
                    size=14,
                    color=ft.Colors.with_opacity(0.7, "onBackground"),
                ),
            ],
        ),
    )

    # Form fields
    email_input = create_custom_input(ft.Icons.EMAIL_OUTLINED, "Email Address", ref=email_ref)

    # Add on_change handler for email field
    email_ref.current.on_change = lambda e: update_send_button_state()

    form_section = ft.Container(
        padding=ft.padding.symmetric(horizontal=24, vertical=20),
        content=ft.Column(
            controls=[
                email_input,
            ],
        ),
    )

    # Send button
    send_button = ft.Container(
        margin=ft.margin.symmetric(horizontal=24, vertical=20),
        width=float("inf"),
        height=50,
        bgcolor=ft.Colors.with_opacity(0.5, "primary"),
        border_radius=14,
        alignment=ft.alignment.center,
        on_click=handle_send_token,
        disabled=True,
        shadow=ft.BoxShadow(
            blur_radius=15,
            color=ft.Colors.with_opacity(0.4, "primary"),
            offset=ft.Offset(0, 5)
        ),
        content=ft.Text(
            "Send Reset Token",
            color="#FFFFFF",
            size=16,
            weight=ft.FontWeight.BOLD,
        ),
    )

    # Already have token button
    already_have_token_button = ft.Container(
        padding=ft.padding.symmetric(horizontal=24, vertical=10),
        content=ft.TextButton(
            "Already have a reset token?",
            style=ft.ButtonStyle(color="primary"),
            on_click=go_to_password_reset,
        ),
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
                send_button,
                already_have_token_button,
                ft.Container(height=20),  # Bottom spacer
            ],
            spacing=0,
        ),
    )

    page.add(layout)


if __name__ == "__main__":
    ft.app(target=main)
