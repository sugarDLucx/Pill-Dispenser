import os
import subprocess
import pygame
import time

PIPER_BINARY = os.path.join(os.path.dirname(__file__), "piper", "piper")
MODEL_FILE = os.path.join(os.path.dirname(__file__), "piper", "en_US-lessac-low.onnx")
AUDIO_DIR = os.path.join(os.path.dirname(__file__), "audio")

INTRO_WAV = os.path.join(AUDIO_DIR, "intro.wav")
OUTRO_WAV = os.path.join(AUDIO_DIR, "outro.wav")

def ensure_audio_dir():
    if not os.path.exists(AUDIO_DIR):
        os.makedirs(AUDIO_DIR)

def generate_tts(text: str, output_path: str):
    """Generate TTS using Piper CLI."""
    if not os.path.exists(PIPER_BINARY):
        print(f"Warning: Piper binary not found at {PIPER_BINARY}. Mocking TTS.")
        # If piper is missing, we create a dummy file to avoid crashing
        with open(output_path, "wb") as f:
            f.write(b"") 
        return

    command = f"echo '{text}' | {PIPER_BINARY} --model {MODEL_FILE} --output_file {output_path}"
    try:
        subprocess.run(command, shell=True, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    except subprocess.CalledProcessError as e:
        print(f"Piper TTS generation failed: {e}")

def initialize_static_audio():
    ensure_audio_dir()
    if not os.path.exists(INTRO_WAV):
        generate_tts("Hello. It is time to take your medication. Your ", INTRO_WAV)
    if not os.path.exists(OUTRO_WAV):
        generate_tts(" has been dispensed into the container. Please take it now.", OUTRO_WAV)

def play_announcement(medicine_name: str):
    ensure_audio_dir()
    medicine_wav = os.path.join(AUDIO_DIR, f"{medicine_name.replace(' ', '_')}.wav")
    
    # Generate the medicine name dynamic audio if needed or always to be sure
    generate_tts(medicine_name, medicine_wav)
    
    # Initialize pygame mixer
    try:
        if not pygame.mixer.get_init():
            pygame.mixer.init(frequency=22050) # default piper frequency
    except pygame.error as e:
        print(f"Pygame audio not available (likely missing audio device): {e}")
        return

    # To queue seamlessly, we play the first, queue the second, then wait and queue the third
    # Actually, a simple approach is to wait for each to finish or use pygame channels
    try:
        sound1 = pygame.mixer.Sound(INTRO_WAV)
        sound2 = pygame.mixer.Sound(medicine_wav)
        sound3 = pygame.mixer.Sound(OUTRO_WAV)

        channel = pygame.mixer.find_channel()
        if not channel:
            return

        channel.play(sound1)
        while channel.get_queue():
            pygame.time.wait(10)
        channel.queue(sound2)
        
        # Wait until sound1 is done, then queue sound 3
        while channel.get_sound() == sound1:
            pygame.time.wait(10)
        channel.queue(sound3)

    except FileNotFoundError as e:
        print(f"Audio file missing: {e}")
    except pygame.error as e:
        # Might occur if files are empty/invalid dummy files on Windows without Piper
        print(f"Pygame error loading sounds: {e}")

if __name__ == "__main__":
    initialize_static_audio()
    play_announcement("Losartan")
