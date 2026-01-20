from core_downloader import get_video_info
import json

url = "https://www.youtube.com/watch?v=tgxyr1A4ob8"
print(f"Testing URL: {url}")

info = get_video_info(url)
if 'error' in info:
    print(f"ERROR: {info['error']}")
else:
    print(f"SUCCESS: Type={info.get('type')}, Title={info.get('title')}")
    print(f"Formats found: {len(info.get('formats', []))}")
    # Print first few formats to verify
    for f in info.get('formats', [])[:5]:
        print(f)
