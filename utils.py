import os
import ffmpeg

def get_audio_length(file_path):
    """Returns the length of the audio file in seconds using ffmpeg."""
    try:
        probe = ffmpeg.probe(file_path)
        return float(probe['format']['duration'])
    except ffmpeg.Error as e:
        print(f"Error probing audio length: {e.stderr}")
        return 0.0

def save_audio(audio_stream, output_path):
    """Run an ffmpeg stream to save to a file."""
    try:
        if os.path.exists(output_path):
            os.remove(output_path)
        out = ffmpeg.output(audio_stream, output_path)
        out.run(overwrite_output=True, quiet=True)
        print(f"Saved audio to {output_path}")
    except ffmpeg.Error as e:
        print(f"Error saving audio: {e.stderr}")
