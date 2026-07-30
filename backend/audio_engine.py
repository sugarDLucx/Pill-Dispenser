import os
import time
import subprocess
import shutil

AUDIO_DIR = os.path.join(os.path.dirname(__file__), "audio")

def ensure_audio_dir():
    if not os.path.exists(AUDIO_DIR):
        os.makedirs(AUDIO_DIR)

def play_audio(filename: str):
    """Play a specific pre-recorded wav file using pygame."""
    filepath = os.path.join(AUDIO_DIR, filename)
    if not os.path.exists(filepath):
        print(f"Audio file not found: {filepath}")
        return

    try:
        # Try to use PipeWire native player first
        if shutil.which("pw-play"):
            subprocess.run(["pw-play", filepath], check=False)
        # Fallback to PulseAudio player
        elif shutil.which("paplay"):
            subprocess.run(["paplay", filepath], check=False)
        # Absolute fallback to ALSA player
        elif shutil.which("aplay"):
            subprocess.run(["aplay", filepath], check=False)
        else:
            print("No audio player (paplay or aplay) found on the system.")
    except Exception as e:
        print(f"Error playing audio {filename}: {e}")

if __name__ == "__main__":
    ensure_audio_dir()
    play_audio("scheduled_time.wav")
