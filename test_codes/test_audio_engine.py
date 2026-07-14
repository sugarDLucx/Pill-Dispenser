import sys
import os

# Add the root directory to the python path so we can import the backend module
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.audio_engine import play_medication_audio

if __name__ == "__main__":
    print("Testing the actual deployment audio engine...")
    print("This will attempt to play: intro.wav -> TTS('It is time to take your Aspirin') -> outro.wav")
    
    # Test the audio engine with a dummy medicine name
    success = play_medication_audio("Aspirin")
    
    if success:
        print("\nTest completed successfully! Did you hear the audio?")
    else:
        print("\nAudio engine test failed. Check the error messages above.")
