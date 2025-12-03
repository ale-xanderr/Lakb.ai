import flet as ft

def build_profile_edit_view(page: ft.Page) -> ft.Control:
    """
    Build the Edit Profile screen content.
    Allows updating First Name, Last Name, Email, and Password.
    """

    def go_back(e):
        page.go("/settings")

    def save_changes(e):
        # Placeholder for save logic
        page.snack_bar = ft.SnackBar(ft.Text("Changes saved successfully!"))
        page.snack_bar.open = True
        page.update()
        # Optionally go back after saving
        # page.go("/settings")

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
        return ft.Column(
            spacing=6,
            controls=[
                ft.Text(label, size=14, weight=ft.FontWeight.W_500, color="onSurface"),
                ft.TextField(
                    value=value,
                    password=password,
                    can_reveal_password=can_reveal_password,
                    border_radius=12,
                    bgcolor="surface",
                    border_color="transparent",
                    text_style=ft.TextStyle(color="onSurface"),
                    content_padding=ft.padding.symmetric(horizontal=16, vertical=14),
                ),
            ],
        )

    # File Picker for image upload
    def on_file_picked(e: ft.FilePickerResultEvent):
        if e.files and len(e.files) > 0:
            # Update the avatar with the selected file
            # Note: In a real app, you'd upload this to a server.
            # Here we just show the local path.
            file_path = e.files[0].path
            avatar_image.src = file_path
            avatar_image.content = None # Remove the "J" text if image is set
            avatar_image.update()
            page.snack_bar = ft.SnackBar(ft.Text(f"Selected: {e.files[0].name}"))
            page.snack_bar.open = True
            page.update()

    file_picker = ft.FilePicker(on_result=on_file_picked)
    page.overlay.append(file_picker)

    def pick_image(e):
        file_picker.pick_files(allow_multiple=False, file_type=ft.FilePickerFileType.IMAGE)

    # Avatar with Edit Icon
    avatar_image = ft.CircleAvatar(
        radius=50,
        bgcolor="#46bd8d",
        content=ft.Text(
            "J",
            color="#FFFFFF",
            weight=ft.FontWeight.BOLD,
            size=40,
        ),
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

    form_content = ft.Column(
        spacing=20,
        controls=[
            profile_picture_section,
            build_text_field("First Name", "Juan"),
            build_text_field("Last Name", "Dela Cruz"),
            build_text_field("Email Address", "juandelacruz@gmail.com"),
            build_text_field("Password", "password123", password=True, can_reveal_password=True),
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
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    controls=[
                        form_content,
                        ft.Container(height=20), # Spacer
                        save_button,
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
