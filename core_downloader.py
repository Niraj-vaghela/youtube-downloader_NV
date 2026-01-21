import yt_dlp
import os

def format_size(bytes_val):
    if not bytes_val: return "N/A"
    for unit in ['B', 'KB', 'MB', 'GB']:
        if bytes_val < 1024:
            return f"{bytes_val:.1f} {unit}"
        bytes_val /= 1024
    return f"{bytes_val:.1f} TB"

def get_video_info(url):
    # ... (rest of docstring and ydl_opts)
    ydl_opts = {
        'quiet': True,
        'extract_flat': 'in_playlist', 
    }
    
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            
            if 'entries' in info:
                # Playlist logic
                return {
                    'type': 'playlist',
                    'title': info.get('title', 'Unknown Playlist'),
                    'thumbnail': None, 
                    'count': len(info['entries']),
                    'entries': info['entries']
                }
            else:
                # Single video
                formats = []
                for f in info.get('formats', []):
                    size_bytes = f.get('filesize') or f.get('filesize_approx')
                    size_str = format_size(size_bytes) if size_bytes else "Unknown Size"
                    
                    # Extract height safely
                    h = f.get('height')
                    if not isinstance(h, int): continue # Skip non-video/weird streams
                    
                    # Base Format Dict
                    fmt = {
                        'format_id': f['format_id'],
                        'ext': f['ext'],
                        'height': h,
                        'note': f.get('format_note', ''),
                        'filesize_str': size_str,
                        'filesize_raw': size_bytes or 0
                    }

                    if f.get('vcodec') != 'none' and f.get('acodec') != 'none':
                         fmt['type'] = 'video+audio'
                         fmt['note'] = 'Standard'
                         formats.append(fmt)
                    elif f.get('vcodec') != 'none':
                         fmt['type'] = 'video'
                         fmt['note'] = 'Video Only'
                         formats.append(fmt)
                    elif f.get('acodec') != 'none':
                        # Audio items usually have None height, so logic above skips them.
                        # We need separate logic or check.
                        pass 
                
                # Audio Pass
                for f in info.get('formats', []):
                    if f.get('vcodec') == 'none' and f.get('acodec') != 'none':
                         size_bytes = f.get('filesize') or f.get('filesize_approx')
                         formats.append({
                             'format_id': f['format_id'],
                             'ext': f['ext'],
                             'abr': f.get('abr', 0),
                             'note': f.get('format_note', 'Audio Only'),
                             'filesize_str': format_size(size_bytes) if size_bytes else "Unknown Size",
                             'type': 'audio'
                        })
                
                return {
                    'type': 'video',
                    'title': info.get('title', 'Unknown Title'),
                    'thumbnail': info.get('thumbnail'),
                    'duration': info.get('duration_string'),
                    'formats': formats,
                    'original_url': url
                }
    except Exception as e:
        return {'error': str(e)}

def download_stream(url, format_id, output_folder, progress_hook=None):
    """
    Downloads a specific format. 
    If format_id is 'best_audio', it converts to MP3.
    """
    
    ydl_opts = {
        'outtmpl': os.path.join(output_folder, '%(title)s.%(ext)s'),
        'progress_hooks': [progress_hook] if progress_hook else [],
        'quiet': True,
        'overwrites': True
    }

    if format_id == 'audio_mp3_best':
        ydl_opts.update({
            'format': 'bestaudio/best',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }],
        })
    elif format_id == 'audio_mp3_320':
        ydl_opts.update({
            'format': 'bestaudio/best',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '320',
            }],
        })
    elif format_id:
        ydl_opts['format'] = format_id
        # If it's pure video, we might want to merge audio? 
        # For simplicity in this iteration, we trust what user selected or provide 'bestvideo+bestaudio' if ffmpeg present.
        if '+' in format_id: # e.g. custom combined string
            pass

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
        return True, "Download Successful"
    except yt_dlp.utils.DownloadError as e:
        err_msg = str(e)
        if "ffmpeg" in err_msg.lower():
             return False, "Error: FFmpeg not found. Cannot merge video/audio or convert to MP3."
        return False, f"Download Error: {err_msg}"
    except Exception as e:
        print(f"Download Error: {e}")
        return False, f"Unexpected Error: {str(e)}"
