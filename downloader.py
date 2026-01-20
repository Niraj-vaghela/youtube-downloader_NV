import os
import yt_dlp

def download_audio(youtube_url, output_dir="downloads"):
    """Downloads audio from YouTube URL and returns the path to the file."""
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    ydl_opts = {
        'format': 'bestaudio/best',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
        'outtmpl': os.path.join(output_dir, 'source_audio.%(ext)s'),
        'quiet': True,
        'overwrites': True,
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info_dict = ydl.extract_info(youtube_url, download=True)
        file_path = ydl.prepare_filename(info_dict)
        # Fix extension check because post-processor changes it
        base, _ = os.path.splitext(file_path)
        final_path = base + ".mp3"
        
    try:
        print(f"Downloaded: {final_path}")
    except Exception:
        # Fallback for Windows consoles that can't handle unicode
        safe_name = final_path.encode('ascii', 'ignore').decode('ascii')
        print(f"Downloaded: {safe_name}")
    return final_path
