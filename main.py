import flet as ft
import os
import threading
try:
    import static_ffmpeg
    # Auto-install/add ffmpeg to path
    static_ffmpeg.add_paths()
except ImportError:
    print("static_ffmpeg not found or failed to load. Ensure ffmpeg is in system PATH if needed.")
except Exception as e:
     print(f"Error loading static_ffmpeg: {e}")

from core_downloader import get_video_info, download_stream
from ui_components import SafeContainer, ResponsiveGrid, VideoCard, DownloadOptionRow, ProgressCard

def app_main(page: ft.Page):
    # App Configuration
    page.title = "YouTube Downloader"
    page.theme_mode = ft.ThemeMode.DARK
    page.padding = 0 
    
    # State References
    current_video_info = None
    
    # Global Components
    status_text = ft.Text("")
    progress_card = ProgressCard()
    
    # --- Tab 1: Downloader ---
    
    url_input = ft.TextField(
        hint_text="Paste video or playlist link...", 
        expand=True,
        border_color=ft.Colors.PRIMARY,
        prefix_icon=ft.Icons.LINK
    )
    
    results_area = ResponsiveGrid([], page)

    def on_progress(d):
        if d['status'] == 'downloading':
            p = d.get('_percent_str', '0%').replace('%','')
            try:
                percent = float(p) / 100
                # Extract MB info if available
                # yt-dlp keys: downloaded_bytes, total_bytes, total_bytes_estimate
                downloaded = d.get('downloaded_bytes', 0)
                total = d.get('total_bytes') or d.get('total_bytes_estimate', 0)
                speed = d.get('_speed_str', 'N/A')
                
                def fmt_mb(b): return f"{b/1024/1024:.1f} MB"
                
                stats_str = f"{fmt_mb(downloaded)} / {fmt_mb(total)}" if total > 0 else f"{fmt_mb(downloaded)}"
                
                progress_card.update_progress(percent, stats_str.split('/')[0], stats_str.split('/')[-1] if '/' in stats_str else '?', speed)
                
            except Exception as e:
                print(f"Progress Error: {e}")
            page.update()
        elif d['status'] == 'finished':
            progress_card.update_progress(1.0, "Done", "Done", "0 B/s")
            
            # Show Completion Popup
            def close_popup(e):
                success_dialog.open = False
                progress_card.reset()
                status_text.value = "Download Complete!"
                page.update()
                
            success_dialog = ft.AlertDialog(
                title=ft.Text("Success"),
                content=ft.Text("Download finished successfully!"),
                actions=[ft.TextButton("Okay", on_click=close_popup)]
            )
            page.overlay.append(success_dialog)
            success_dialog.open = True
            page.update()

    def download_wrapper(format_id, ext):
        if not current_video_info: return
        
        status_text.value = "Starting download..."
        progress_card.reset() # Reset
        progress_card.visible = True
        page.update()
        
        output_dir = "downloads" # TODO: Make configurable via Settings
        if not os.path.exists(output_dir): os.makedirs(output_dir)

        def _target():
            url = current_video_info['original_url']
            success, msg = download_stream(url, format_id, output_dir, on_progress)
            
            if not success:
                status_text.value = msg
                status_text.color = ft.Colors.ERROR
                page.update()

        threading.Thread(target=_target, daemon=True).start()

    def build_formats_list(formats, dialog_ref=None):
        # 1. Processing Logic
        # Audio Candidates
        audio_candidates = [f for f in formats if f.get('type') == 'audio']
        audio_candidates.sort(key=lambda x: (x.get('abr', 0), x.get('filesize_raw', 0)), reverse=True)
        
        final_audio = []
        seen_abr = set()
        
        # Add MP3 conversion options
        final_audio.append({
            'custom': True, 'quality': "High Quality MP3 (320kbps)", 'ext': 'mp3', 
            'size': '~', # Unknown size before conversion
            'id': 'audio_mp3_320', 'type': 'mp3'
        })
        final_audio.append({
            'custom': True, 'quality': "Standard MP3 (192kbps)", 'ext': 'mp3', 
            'size': audio_candidates[0].get('filesize_str', '~') if audio_candidates else 'N/A',
            'id': 'audio_mp3_best', 'type': 'mp3'
        })
        
        # Add distinct original bitrates
        for f in audio_candidates:
            abr = f.get('abr', 0)
            if abr == 0: continue
            
            # Group bitrates closely (e.g. 128 vs 130)
            abr_group = round(abr, -1) 
            if abr_group not in seen_abr:
                seen_abr.add(abr_group)
                final_audio.append(f)

        # Video Candidates
        video_candidates = [f for f in formats if 'video' in f.get('type', '')]
        video_candidates.sort(key=lambda x: (x.get('height', 0), x.get('filesize_raw', 0)), reverse=True)

        seen_heights = set()
        final_videos = []
        for f in video_candidates:
            h = f.get('height', 0)
            if h == 0: continue
            if h not in seen_heights:
                seen_heights.add(h)
                final_videos.append(f)

        # 2. HELPER: Generate UI Rows
        def make_rows(items, is_video):
            rows = []
            for item in items:
                if item.get('custom'):
                    # Special Custom Rows (like MP3)
                    rows.append(DownloadOptionRow(
                        quality=item['quality'], size_str=item['size'], ext=item['ext'],
                        on_click=lambda e, i=item['id']: download_wrapper(i, item['type'])
                    ))
                    continue
                    
                size = item.get('filesize_str', 'N/A')
                ext = item['ext']
                
                if is_video:
                    res = item['height']
                    label = f"{res}p"
                    if res >= 2160: label = f"4K ({res}p)"
                    elif res >= 1440: label = f"2K ({res}p)"
                    elif res >= 1080: label = f"HD ({res}p)"
                    
                    fid = item['format_id']
                    if 'video' in item.get('type', ''): fid = f"{fid}+bestaudio/best"
                    
                    rows.append(DownloadOptionRow(
                        quality=f"{label} Video", size_str=size, ext=ext,
                        on_click=lambda e, i=fid: download_wrapper(i, 'mp4')
                    ))
                else:
                    # Audio
                    abr = int(item.get('abr', 0))
                    label = f"{abr} kbps"
                    
                    rows.append(DownloadOptionRow(
                        quality=f"Audio ({label})", size_str=size, ext=ext,
                        on_click=lambda e, i=item['format_id'], x=ext: download_wrapper(i, x) # Force orig ext
                    ))
            return rows

        # 3. Build Columns
        audio_col = ft.Column([
            ft.Text("Audio Formats", weight=ft.FontWeight.BOLD),
            ft.Divider(height=5, color=ft.Colors.GREY_800),
        ] + make_rows(final_audio, False), spacing=5, width=350)

        video_col = ft.Column([
            ft.Text("Video Formats", weight=ft.FontWeight.BOLD),
            ft.Divider(height=5, color=ft.Colors.GREY_800),
        ] + make_rows(final_videos, True), spacing=5, width=350)

        # 4. Return Split Layout (Simple Row)
        return ft.Container(
            content=ft.Row(
                [audio_col, video_col],
                wrap=True,
                alignment=ft.MainAxisAlignment.START,
                vertical_alignment=ft.CrossAxisAlignment.START,
                spacing=20
            ),
            padding=5
        )

    def search_click(e):
        nonlocal current_video_info
        url = url_input.value
        if not url: return

        status_text.value = "Fetching Info..."
        status_text.color = ft.Colors.WHITE
        results_area.set_items([])
        page.update()
        
        info = get_video_info(url)
        
        if 'error' in info:
            status_text.value = f"Error: {info['error']}"
            status_text.color = ft.Colors.ERROR
        elif info['type'] == 'playlist':
            status_text.value = f"Found Playlist: {info['title']}"
            # Placeholder for Playlist UI
            results_area.set_items([
                ft.Container(content=ft.Text("Playlist Download Coming Soon", size=20), padding=20)
            ])
        else:
            current_video_info = info
            status_text.value = "Video Found"
            
            # Build Formats Control
            formats_ui = build_formats_list(info.get('formats', []))
            
            card = VideoCard(
                title=info['title'],
                thumbnail_url=info['thumbnail'],
                duration=info.get('duration', '??:??'),
                formats_control=formats_ui
            )
            results_area.set_items([card])
            
        page.update()

    # --- Tab 2: Settings ---
    settings_content = ft.Column([
        ft.Text("Settings", size=24, weight=ft.FontWeight.BOLD),
        ft.Divider(),
        ft.TextField(label="Download Location", value=os.path.abspath("downloads"), read_only=True, suffix_icon=ft.Icons.FOLDER),
        ft.Container(height=20),
        ft.Text("About", size=20, weight=ft.FontWeight.BOLD),
        ft.Text("Version: 2.0.0"),
        ft.Text("Powered by yt-dlp & Flet"),
        ft.Container(height=20),
        ft.ExpansionTile(
            title=ft.Text("FAQ / Help"),
            controls=[
                ft.ListTile(title=ft.Text("Where are files saved?"), subtitle=ft.Text("In the 'downloads' folder inside the app directory.")),
                ft.ListTile(title=ft.Text("Why is it slow?"), subtitle=ft.Text("High quality video merging (4K/8K) takes CPU power."))
            ]
        )
    ], scroll=ft.ScrollMode.AUTO)

    # --- Layout Assembly ---
    
    # --- Layout Assembly ---
    
    downloader_view = ft.Container(content=ft.Column([
        ft.Row([url_input, ft.IconButton(ft.Icons.SEARCH, on_click=search_click, icon_color=ft.Colors.PRIMARY)]),
        status_text,
        progress_card,
        ft.Divider(),
        results_area
    ], scroll=ft.ScrollMode.ADAPTIVE), padding=10)
    
    settings_view = ft.Container(content=settings_content, padding=10)

    # Main Body
    body = ft.Container(content=downloader_view, expand=True)

    # --- Navigation Logic ---
    def toggle_settings(e):
        if body.content == downloader_view:
            body.content = settings_view
            page.appbar.title = ft.Text("Settings")
            page.appbar.actions[0].icon = ft.Icons.CLOSE
        else:
            body.content = downloader_view
            page.appbar.title = ft.Text("YouTube Downloader")
            page.appbar.actions[0].icon = ft.Icons.SETTINGS
        page.update()

    def open_coffee(e):
        page.launch_url("https://buymeacoffee.com/Niraj_NV")

    # AppBar with Settings
    page.appbar = ft.AppBar(
        title=ft.Text("YouTube Downloader"),
        center_title=True,
        bgcolor=ft.Colors.GREY_900,
        actions=[
            ft.IconButton(ft.Icons.LOCAL_CAFE, on_click=open_coffee, tooltip="Buy me a coffee", icon_color=ft.Colors.ORANGE_300),
            ft.IconButton(ft.Icons.SETTINGS, on_click=toggle_settings)
        ]
    )
    
    # Remove Navigation Bar
    # page.navigation_bar = ... (Removed)
    
    page.add(SafeContainer(body, page))

    # Show Coffee Dialog on Load
    def close_coffee(e):
        coffee_dialog.open = False
        page.update()

    coffee_dialog = ft.AlertDialog(
        title=ft.Text("Support the Developer"),
        content=ft.Text("If you find this app useful, please consider buying me a coffee!"),
        actions=[
            ft.TextButton("Maybe Later", on_click=close_coffee),
            ft.FilledButton("Support", on_click=open_coffee, icon=ft.Icons.LOCAL_CAFE, style=ft.ButtonStyle(color=ft.Colors.BLACK, bgcolor=ft.Colors.ORANGE_300))
        ],
    )
    page.overlay.append(coffee_dialog)
    coffee_dialog.open = True
    page.update()

def main(page: ft.Page):
    try:
        app_main(page)
    except Exception as e:
        page.clean()
        page.add(
            ft.Column([
                ft.Icon(ft.Icons.ERROR_OUTLINE, color=ft.Colors.RED, size=50),
                ft.Text("App Startup Failed", size=24, color=ft.Colors.RED, weight=ft.FontWeight.BOLD),
                ft.Text(f"Error: {e}", size=16),
                ft.Text("This screen prevents the app from crashing silently."),
            ], alignment=ft.MainAxisAlignment.CENTER)
        )
        page.update()

if __name__ == "__main__":
    # Ensure assets are bundled
    ft.app(target=main, view=ft.AppView.WEB_BROWSER, port=8550, assets_dir="assets")
