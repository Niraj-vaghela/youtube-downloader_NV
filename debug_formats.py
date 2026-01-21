from core_downloader import get_video_info
import json

url = "https://www.youtube.com/watch?v=LXb3EKWsInQ"
print(f"Fetching info for: {url}")
info = get_video_info(url)

print(f"Formats count: {len(info.get('formats', []))}")
for f in info.get('formats', []):
    if 'video' in f.get('type', ''):
        print(f"Height: {f.get('height')} (Type: {type(f.get('height'))}) | ID: {f['format_id']}")
