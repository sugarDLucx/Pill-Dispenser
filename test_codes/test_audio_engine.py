import sys
import os

# Add the root directory to the python path so we can import the backend module
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.audio_engine import play_announcement

if __name__ == "__main__":
    print("Testing the actual deployment audio engine...")
    print("This will attempt to play: intro.wav -> TTS('Aspirin') -> outro.wav")
    
    # Test the audio engine with a dummy medicine name
    play_announcement("Aspirin")
    
    print("\nTest completed successfully! Did you hear the audio?")
