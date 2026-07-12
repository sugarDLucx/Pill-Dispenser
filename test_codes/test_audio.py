import os
import time
import pygame
import subprocess

PIPER_BINARY = os.path.join(os.path.dirname(os.path.dirname(__file__)), "backend", "piper", "piper")
MODEL_FILE = os.path.join(os.path.dirname(os.path.dirname(__file__)), "backend", "piper", "en_US-lessac-low.onnx")
AUDIO_DIR = os.path.join(os.path.dirname(__file__), "test_audio_output")
TEST_WAV = os.path.join(AUDIO_DIR, "test_audio.wav")

def ensure_audio_dir():
    if not os.path.exists(AUDIO_DIR):
        os.makedirs(AUDIO_DIR)

def test_tts_generation():
    print("Testing TTS generation with Piper...")
    if not os.path.exists(PIPER_BINARY):
        print(f"Warning: Piper binary not found at {PIPER_BINARY}.")
        print("Skipping TTS generation test.")
        return False
        
    text = "This is a test of the audio system."
    command = f"echo '{text}' | {PIPER_BINARY} --model {MODEL_FILE} --output_file {TEST_WAV}"
    try:
        subprocess.run(command, shell=True, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        print(f"TTS generated successfully at {TEST_WAV}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"Piper TTS generation failed: {e}")
        return False

def test_audio_playback():
    print("Testing audio playback with pygame...")
    if not os.path.exists(TEST_WAV):
        print(f"Test audio file {TEST_WAV} not found. Playback skipped.")
        return
        
    try:
        if not pygame.mixer.get_init():
            pygame.mixer.init(frequency=22050)
            
        sound = pygame.mixer.Sound(TEST_WAV)
        channel = pygame.mixer.find_channel()
        if channel:
            print("Playing sound...")
            channel.play(sound)
            while channel.get_busy():
                pygame.time.wait(100)
            print("Playback finished successfully.")
        else:
            print("No audio channel available.")
    except pygame.error as e:
        print(f"Pygame audio not available or playback failed: {e}")

if __name__ == "__main__":
    print("Starting Audio test...")
    ensure_audio_dir()
    
    generated = test_tts_generation()
    
    # Optional: If you don't have piper installed on dev machine, 
    # we can just test pygame init if TTS fails.
    if generated or os.path.exists(TEST_WAV):
        test_audio_playback()
    else:
        print("No audio file to play. Make sure Piper is configured correctly.")
        
    print("Audio test completed.")
