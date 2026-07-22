import os
import pygame
import time

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
        if not pygame.mixer.get_init():
            pygame.mixer.init(frequency=24000) # Standard TTS frequency
    except pygame.error as e:
        print(f"Pygame audio not available (likely missing audio device): {e}")
        return
        
    try:
        sound = pygame.mixer.Sound(filepath)
        channel = pygame.mixer.find_channel()
        if channel:
            channel.play(sound)
            # Wait for the sound to finish playing
            while channel.get_busy():
                pygame.time.wait(100)
    except Exception as e:
        print(f"Error playing audio {filename}: {e}")

if __name__ == "__main__":
    ensure_audio_dir()
    play_audio("scheduled_time.mp3")
