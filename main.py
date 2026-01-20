import flet as ft
import os
import static_ffmpeg
import threading

# Auto-install/add ffmpeg to path
static_ffmpeg.add_paths()

from core_downloader import get_video_info, download_stream
from ui_components import SafeContainer, ResponsiveGrid, VideoCard, DownloadOptionRow, ProgressCard

def main(page: ft.Page):
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
        label="YouTube URL", 
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

    def build_formats_list(formats):
        # Helper to simplify list of common formats
        # Show: Best Audio, Best Video, 1080p, 720p...
        # We'll use our pre-parsed formats from core_downloader
        
        col = ft.Column(spacing=5)
        
        # Header
        col.controls.append(ft.Text("Available Formats:", weight=ft.FontWeight.BOLD, size=16))
        
        # Audio Op
        best_audio = next((f for f in formats if f['type'] == 'audio'), None)
        if best_audio:
            col.controls.append(DownloadOptionRow(
                quality="Best Audio (MP3)",
                size_str=best_audio.get('filesize_str', 'N/A'),
                ext="mp3",
                on_click=lambda _: download_wrapper('audio_mp3_best', 'mp3')
            ))
            
        col.controls.append(ft.Divider(height=10, color=ft.Colors.TRANSPARENT))
        
        # Video Ops
        # Deduplicate by resolution to avoid clustering UI
        seen = set()
        for f in formats:
            if 'video' in f['type']:
                res = f.get('resolution', 0)
                if res == 'unknown': continue
                
                # Check if we already have this resolution
                if res in seen: continue
                seen.add(res)
                
                # Determine correct ID for merging if needed (handled by core_downloader logic usually)
                # But here we just pass the ID we found.
                # If it is 'video only', we rely on yt-dlp 'bestvideo+bestaudio' merge logic OR
                # we force it. For now, let's assume we pass the format_id and core handles merge if needed.
                # Actually core logic for specific ID might need 'format_id+bestaudio' manually stringified.
                
                fid = f['format_id']
                if f['type'] == 'video': # Video only
                    fid = f"{fid}+bestaudio/best"
                    
                label = f"{res}p" if isinstance(res, int) else str(res)
                
                col.controls.append(DownloadOptionRow(
                    quality=f"{label} Video",
                    size_str=f.get('filesize_str', 'N/A'),
                    ext=f['ext'],
                    on_click=lambda e, i=fid: download_wrapper(i, 'mp4')
                ))
                
                if len(seen) >= 4: break # Limit options
                
        return col

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

    def on_nav_change(e):
        idx = e.control.selected_index
        if idx == 0:
            body.content = downloader_view
        elif idx == 1:
            body.content = settings_view
        page.update()

    page.navigation_bar = ft.NavigationBar(
        selected_index=0,
        destinations=[
            ft.NavigationBarDestination(icon=ft.Icons.DOWNLOAD, label="Downloader"),
            ft.NavigationBarDestination(icon=ft.Icons.SETTINGS, label="Settings"),
        ],
        on_change=on_nav_change
    )
    
    page.add(SafeContainer(body, page))

if __name__ == "__main__":
    ft.app(target=main, view=ft.AppView.WEB_BROWSER)
