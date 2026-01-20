from core_downloader import download_stream
import os
import static_ffmpeg
import time

# Ensure ffmpeg is ready
static_ffmpeg.add_paths()

URL = "https://www.youtube.com/watch?v=o8V8MR70Ums"
OUTPUT_DIR = "automated_downloads"

if not os.path.exists(OUTPUT_DIR):
    os.makedirs(OUTPUT_DIR)

def run_test(name, format_id, expected_ext):
    print(f"\n[TEST] {name}...")
    start_time = time.time()
    
    # Define a simple progress hook
    def progress_hook(d):
        if d['status'] == 'finished':
            print(f"  - Download finished. Processing...")

    success, msg = download_stream(URL, format_id, OUTPUT_DIR, progress_hook)
    
    if not success:
        print(f"  [FAIL] Download failed: {msg}")
        return False
        
    # Verify File Exists
    # yt-dlp naming can be tricky, so we look for files with matching extension in the folder
    # created recently
    print(f"  - Download reported success. Checking files...")
    files = [f for f in os.listdir(OUTPUT_DIR) if f.endswith(expected_ext)]
    if not files:
        print(f"  [FAIL] No {expected_ext} file found in {OUTPUT_DIR}")
        return False
        
    print(f"  [PASS] Found: {files[-1]}")
    return True

def main():
    print("=== STARTING AUTOMATED TESTS ===")
    
    # Test 1: Audio (Best MP3)
    # This requires FFmpeg conversion
    audio_pass = run_test("Audio Download (MP3)", "audio_mp3_best", ".mp3")
    
    # Test 2: Video (Best MP4)
    # This requires FFmpeg merge usually
    video_pass = run_test("Video Download (MP4)", "best", ".mp4")
    
    print("\n=== SUMMARY ===")
    print(f"Audio Test: {'PASS' if audio_pass else 'FAIL'}")
    print(f"Video Test: {'PASS' if video_pass else 'FAIL'}")

if __name__ == "__main__":
    main()
