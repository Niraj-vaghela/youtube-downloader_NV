from core_downloader import get_video_info, download_stream
import os
import static_ffmpeg
static_ffmpeg.add_paths()

url = "https://www.youtube.com/watch?v=tgxyr1A4ob8"
print(f"Testing Download for: {url}")

# 1. Get Info first (needed for some logic, though download_stream takes url directly)
# info = get_video_info(url) 

# 2. Try to download Best Audio (requires ffmpeg)
print("Attempting 'audio_mp3_best' download...")
success, msg = download_stream(url, 'audio_mp3_best', 'downloads')

print(f"Result: Success={success}")
print(f"Message: {msg}")

if not success and "ffmpeg" in msg.lower():
    print("VERIFIED: Correctly detected missing ffmpeg.")
else:
    print("WARNING: Unexpected result.")
