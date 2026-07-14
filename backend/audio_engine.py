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
    # Helper to safely load a sound
    def safe_load_sound(path):
        if not os.path.exists(path) or os.path.getsize(path) < 44:
            return None
        try:
            return pygame.mixer.Sound(path)
        except pygame.error:
            return None

    sound1 = safe_load_sound(INTRO_WAV)
    sound2 = safe_load_sound(medicine_wav)
    sound3 = safe_load_sound(OUTRO_WAV)

    channel = pygame.mixer.find_channel()
    if not channel:
        return

    # Play valid sounds in sequence
    sounds_to_play = [s for s in [sound1, sound2, sound3] if s is not None]
    
    if not sounds_to_play:
        print("No valid audio files to play.")
        return

    # Play first sound
    channel.play(sounds_to_play[0])
    
    # Queue remaining sounds
    for i in range(1, len(sounds_to_play)):
        while channel.get_queue():
            pygame.time.wait(10)
        channel.queue(sounds_to_play[i])
        
        # Wait until the currently playing sound finishes before queuing the next
        while channel.get_sound() == sounds_to_play[i-1]:
            pygame.time.wait(10)

if __name__ == "__main__":
    initialize_static_audio()
    play_announcement("Losartan")
