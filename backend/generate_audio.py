import os
from gtts import gTTS

AUDIO_DIR = os.path.join(os.path.dirname(__file__), "audio")

def generate_all():
    if not os.path.exists(AUDIO_DIR):
        os.makedirs(AUDIO_DIR)

    files_to_generate = {
        "scheduled_time.mp3": "It is time to take your medication. Please press the green button to dispense your pills.",
        "dispensing.mp3": "Dispensing your medication. Please wait.",
        "done_dispensing.mp3": "Medication dispensed. Please take your pills now.",
        "satisfied.mp3": "I hope you're satisfied with my care.",
        "missed_alert.mp3": "Reminder: You have missed your scheduled medication. An alert has been sent to your caregiver."
    }

    for filename, text in files_to_generate.items():
        filepath = os.path.join(AUDIO_DIR, filename)
        print(f"Generating {filename}...")
        tts = gTTS(text=text, lang='en', slow=False)
        tts.save(filepath)

    print("All audio files generated successfully!")

if __name__ == "__main__":
    generate_all()
