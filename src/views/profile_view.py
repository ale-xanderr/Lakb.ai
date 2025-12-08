import flet as ft
from services.auth_service import AuthService
from services.profile_service import ProfileService


def build_profile_edit_view(page: ft.Page) -> ft.Control:
    """
    Builds the Edit Profile View content.
    Allows users to update their profile information (name, email, password, avatar).
    
    Args:
        page: The Flet page instance.
        
    Returns:
        ft.Control: The main content control for the view.
    """
    
    # Initialize services
    auth_service = AuthService()
    profile_service = ProfileService()
    
    # Get current user
    user = auth_service.get_user()
    if not user:
        # If no user, redirect to login
        page.go("/")
        return ft.Container()
    
    # UserResponse structure: user.user contains the actual User object
    user_data = user.user
    user_id = user_data.id
    
    # Fetch profile data from Supabase
    profile = profile_service.ensure_profile_exists(
        user_id, 
        user_data.email, 
        user_data.user_metadata
    )
    
    # Extract data
    first_name_val = profile.get('first_name', '')
    last_name_val = profile.get('last_name', '')
    email_val = profile.get('email', user_data.email)
    avatar_url = profile.get('avatar_url', None)
    
    # State for tracking changes
    selected_image_path = {"value": None}
    is_saving = {"value": False}

    def go_back(e):
        page.go("/settings")

    def show_snackbar(message: str, is_error: bool = False):
        page.snack_bar = ft.SnackBar(
            ft.Text(message),
            bgcolor=ft.Colors.ERROR if is_error else ft.Colors.GREEN,
        )
        page.snack_bar.open = True
        page.update()

    def save_changes(e):
        if is_saving["value"]:
            return  # Prevent multiple saves
        
        is_saving["value"] = True
        save_button.content = ft.Row(
            alignment=ft.MainAxisAlignment.CENTER,
            controls=[
                ft.ProgressRing(width=20, height=20, stroke_width=3, color="white"),
                ft.Text("Saving...", size=16, weight=ft.FontWeight.BOLD, color="#FFFFFF"),
            ],
        )
        save_button.update()
        
        try:
            # Get values from text fields
            new_first_name = first_name_field.value.strip()
            new_last_name = last_name_field.value.strip()
            new_email = email_field.value.strip()
            new_password = password_field.value.strip() if password_field.value else None
            
            # Validate required fields
            if not new_first_name:
                show_snackbar("First name is required", is_error=True)
                is_saving["value"] = False
                reset_save_button()
                return
            
            if not new_email:
                show_snackbar("Email is required", is_error=True)
                is_saving["value"] = False
                reset_save_button()
                return
            
            # Update profile data
            success = profile_service.update_user_profile(
                user_id,
                first_name=new_first_name,
                last_name=new_last_name,
                email=new_email
            )
            
            if not success:
                show_snackbar("Failed to update profile", is_error=True)
                is_saving["value"] = False
                reset_save_button()
                return
            
            # Update password if provided and not the placeholder
            if new_password and new_password != "********":
                if len(new_password) < 6:
                    show_snackbar("Password must be at least 6 characters", is_error=True)
                    is_saving["value"] = False
                    reset_save_button()
                    return
                
                password_success, password_msg = profile_service.update_password(new_password)
                if not password_success:
                    show_snackbar(f"Profile updated but password failed: {password_msg}", is_error=True)
                    is_saving["value"] = False
                    reset_save_button()
                    return
            
            # Upload profile image if selected
            if selected_image_path["value"]:
                image_url = profile_service.upload_profile_image(user_id, selected_image_path["value"])
                if image_url:
                    # Update avatar display
                    avatar_image.foreground_image_src = image_url
                    avatar_image.content = None
                    avatar_image.update()
                else:
                    show_snackbar("Profile updated but image upload failed", is_error=True)
            
            show_snackbar("Changes saved successfully!")
            
            # Reset password field to placeholder
            password_field.value = "********"
            password_field.update()
            
        except Exception as e:
            print(f"Error saving profile: {e}")
            show_snackbar(f"Error: {str(e)}", is_error=True)
        finally:
            is_saving["value"] = False
            reset_save_button()

    def reset_save_button():
        save_button.content = ft.Text(
            "Save Changes",
            size=16,
            weight=ft.FontWeight.BOLD,
            color="#FFFFFF",
        )
        save_button.update()

    # Header
    header = ft.Container(
        padding=ft.padding.only(left=16, right=16, top=20, bottom=12),
        content=ft.Row(
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
            controls=[
                ft.IconButton(
                    icon=ft.Icons.ARROW_BACK_IOS_NEW,
                    icon_size=18,
                    icon_color="onBackground",
                    style=ft.ButtonStyle(
                        shape={
                            ft.ControlState.DEFAULT: ft.RoundedRectangleBorder(radius=9999)
                        },
                        padding=8,
                    ),
                    on_click=go_back,
                ),
                ft.Text(
                    "Edit Profile",
                    size=20,
                    weight=ft.FontWeight.BOLD,
                    color="onBackground",
                ),
            ],
        ),
    )

    # Form Fields
    def build_text_field(label, value, password=False, can_reveal_password=False):
        field = ft.TextField(
            value=value,
            password=password,
            can_reveal_password=can_reveal_password,
            border_radius=12,
            bgcolor="surface",
            border_color="transparent",
            text_style=ft.TextStyle(color="onSurface"),
            content_padding=ft.padding.symmetric(horizontal=16, vertical=14),
        )
        return ft.Column(
            spacing=6,
            controls=[
                ft.Text(label, size=14, weight=ft.FontWeight.W_500, color="onSurface"),
                field,
            ],
        ), field

    # File Picker for image upload
    def on_file_picked(e: ft.FilePickerResultEvent):
        if e.files and len(e.files) > 0:
            file_path = e.files[0].path
            selected_image_path["value"] = file_path
            
            # Update the avatar preview with the selected file
            avatar_image.foreground_image_src = file_path
            avatar_image.content = None  # Remove the text initial
            avatar_image.update()
            
            show_snackbar(f"Selected: {e.files[0].name}. Click 'Save Changes' to upload.")

    file_picker = ft.FilePicker(on_result=on_file_picked)
    page.overlay.append(file_picker)

    def pick_image(e):
        file_picker.pick_files(
            allow_multiple=False,
            file_type=ft.FilePickerFileType.IMAGE,
            allowed_extensions=["jpg", "jpeg", "png", "webp"]
        )

    # Avatar with Edit Icon
    # Use first letter of first name
    initial = first_name_val[0].upper() if first_name_val else "U"
    
    avatar_image = ft.CircleAvatar(
        radius=50,
        bgcolor="#46bd8d",
        foreground_image_src=avatar_url if avatar_url else None,
        content=ft.Text(
            initial,
            color="#FFFFFF",
            weight=ft.FontWeight.BOLD,
            size=40,
        ) if not avatar_url else None,
    )

    profile_picture_section = ft.Container(
        alignment=ft.alignment.center,
        margin=ft.margin.only(bottom=20),
        on_click=pick_image,
        content=ft.Stack(
            controls=[
                avatar_image,
                ft.Container(
                    right=0,
                    bottom=0,
                    width=30,
                    height=30,
                    bgcolor="surface",
                    border_radius=15,
                    alignment=ft.alignment.center,
                    content=ft.Icon(
                        ft.Icons.EDIT,
                        size=16,
                        color="primary",
                    ),
                ),
            ],
            width=100,
            height=100,
        ),
    )

    # Create text fields
    first_name_container, first_name_field = build_text_field("First Name", first_name_val)
    last_name_container, last_name_field = build_text_field("Last Name", last_name_val)
    email_container, email_field = build_text_field("Email Address", email_val)
    password_container, password_field = build_text_field("Password", "********", password=True, can_reveal_password=True)

    form_content = ft.Column(
        spacing=20,
        controls=[
            profile_picture_section,
            first_name_container,
            last_name_container,
            email_container,
            password_container,
            ft.Text(
                "Leave password as is to keep current password, or enter a new one to change it.",
                size=12,
                color="#9AA4AF",
                italic=True,
            ),
        ],
    )

    # Save Button
    save_button = ft.Container(
        width=float("inf"),
        height=50,
        border_radius=25,
        bgcolor="primary",
        on_click=save_changes,
        alignment=ft.alignment.center,
        content=ft.Text(
            "Save Changes",
            size=16,
            weight=ft.FontWeight.BOLD,
            color="#FFFFFF",
        ),
    )

    content_column = ft.Column(
        expand=True,
        spacing=0,
        controls=[
            header,
            ft.Container(
                expand=True,
                padding=ft.padding.all(24),
                content=ft.Column(
                    expand=True,
                    scroll=ft.ScrollMode.AUTO,
                    controls=[
                        form_content,
                        ft.Container(height=20),  # Spacer
                        save_button,
                        ft.Container(height=20),  # Bottom padding for safe area
                    ],
                ),
            ),
        ],
    )

    return ft.SafeArea(
        expand=True,
        content=ft.Container(
            bgcolor="background",
            expand=True,
            content=content_column,
        ),
    )
