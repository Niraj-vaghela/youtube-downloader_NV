from core_downloader import get_video_info
import json

# Costa Rica 4K video
url = "https://www.youtube.com/watch?v=LXb3EKWsInQ"
print(f"Fetching info for: {url}")

info = get_video_info(url)
if 'error' in info:
    print(f"Error: {info['error']}")
else:
    print("Found formats:")
    # Print video only formats sorted by resolution
    vid_formats = [f for f in info['formats'] if f['type'] == 'video']
    
    # Sort by resolution (handling types)
    def get_res(x):
        r = x.get('resolution')
        return r if isinstance(r, int) else 0
        
    vid_formats.sort(key=get_res, reverse=True)
    
    for f in vid_formats:
        print(f" - {f['resolution']}p | {f['ext']} | {f.get('filesize_str')} | ID: {f['format_id']}")

    print("\nAudio Formats:")
    aud_formats = [f for f in info['formats'] if f['type'] == 'audio']
    for f in aud_formats:
        print(f" - {f.get('abr')}kbps | {f['ext']} | {f.get('filesize_str')}")
