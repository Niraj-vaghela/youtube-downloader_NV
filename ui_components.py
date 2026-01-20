import flet as ft

class SafeContainer(ft.Container):
    """
    A container that respects the device's safe area (notches, status bars).
    """
    def __init__(self, content: ft.Control, page: ft.Page):
        super().__init__()
        self.content = content
        self.expand = True
        self.padding = ft.padding.only(top=10, left=10, right=10, bottom=10) 
        
class ResponsiveGrid(ft.Column):
    """
    A layout that behaves as a list on mobile (single column)
    and a grid on tablet/desktop (multiple columns).
    """
    def __init__(self, items: list[ft.Control], page: ft.Page):
        super().__init__()
        self.raw_items = items
        self.page_ref = page
        self.scroll = ft.ScrollMode.ADAPTIVE
        self.expand = True
        self.controls = [] 
        self.update_layout()

    def set_items(self, items: list[ft.Control]):
        self.raw_items = items
        self.update_layout()

    def update_layout(self):
        # Determine strict breakpoints
        # Phone: < 600px
        # Tablet: >= 600px
        width = self.page_ref.width if self.page_ref.width else 400
        
        is_tablet = width >= 600
        
        if is_tablet:
            # Grid Mode
            self.controls = [
                ft.Row(
                    controls=self.raw_items, 
                    wrap=True, 
                    spacing=20, 
                    run_spacing=20,
                    alignment=ft.MainAxisAlignment.START,
                    vertical_alignment=ft.CrossAxisAlignment.START
                )
            ]
        else:
            # List Mode
            self.controls = self.raw_items

class VideoCard(ft.Container):
    """
    A card component to display video info.
    Supports expanding to show format options.
    """
    def __init__(self, title, thumbnail_url, duration, formats_control=None):
        super().__init__()
        self.border_radius = 10
        self.bgcolor = ft.Colors.GREY_900
        self.padding = 10
        self.width = 300 # Fixed width for grid compatibility
        
        # Core Content
        self.main_col = ft.Column([
            ft.Image(src=thumbnail_url, border_radius=10, height=160, fit=ft.ImageFit.COVER if hasattr(ft, 'ImageFit') else "cover"),
            ft.Text(title, weight=ft.FontWeight.BOLD, no_wrap=True, overflow=ft.TextOverflow.ELLIPSIS),
            ft.Text(f"Duration: {duration}", size=12, color=ft.Colors.GREY_400),
        ])
        
        if formats_control:
            self.main_col.controls.append(formats_control)
            
        self.content = self.main_col

class DownloadOptionRow(ft.Container):
    """
    A row displaying Quality | Size | Extension | Download Button
    """
    def __init__(self, quality, size_str, ext, on_click):
        super().__init__()
        self.bgcolor = ft.Colors.GREY_800
        self.padding = 10
        self.border_radius = 5
        self.margin = ft.margin.only(bottom=5)
        
        self.content = ft.Row([
            ft.Column([
                ft.Text(quality, weight=ft.FontWeight.BOLD, size=14),
                ft.Text(f"{size_str} • {ext.upper()}", size=12, color=ft.Colors.GREY_400)
            ], expand=True),
            ft.IconButton(ft.Icons.DOWNLOAD, on_click=on_click, icon_color=ft.Colors.PRIMARY)
        ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN)

class ProgressCard(ft.Container):
    """
    Shows detailed progress: Bar + Text Stats
    """
    def __init__(self):
        super().__init__()
        self.visible = False
        self.bgcolor = ft.Colors.GREY_900
        self.padding = 15
        self.border_radius = 10
        
        self.status_text = ft.Text("Starting...", size=14, weight=ft.FontWeight.BOLD)
        self.details_text = ft.Text("0 MB / 0 MB", size=12, color=ft.Colors.GREY_400)
        self.p_bar = ft.ProgressBar(value=0, color=ft.Colors.PRIMARY, bgcolor=ft.Colors.GREY_800)
        
        self.content = ft.Column([
            self.status_text,
            self.p_bar,
            self.details_text
        ])
        
    def update_progress(self, percent, downloaded_str, total_str, speed_str):
        self.visible = True
        self.p_bar.value = percent
        self.status_text.value = f"Downloading... {int(percent*100)}%"
        self.details_text.value = f"{downloaded_str} / {total_str} ({speed_str})"
        self.update()
        
    def reset(self):
        self.visible = False
        self.p_bar.value = 0
        self.status_text.value = ""
        self.details_text.value = ""
        self.update()
