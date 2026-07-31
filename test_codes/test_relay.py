import time
import RPi.GPIO as GPIO

RELAY_PIN = 17

try:
    print(f"Initializing Relay on GPIO {RELAY_PIN} using RPi.GPIO...")
    GPIO.setwarnings(False)
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(RELAY_PIN, GPIO.OUT)
    
    print("Testing Active-High (3.3V)...")
    for i in range(2):
        print("Sending HIGH (3.3V)...")
        GPIO.output(RELAY_PIN, GPIO.HIGH)
        time.sleep(2)
        print("Sending LOW (0V)...")
        GPIO.output(RELAY_PIN, GPIO.LOW)
        time.sleep(2)

    print("\nTest Complete!")
except Exception as e:
    print(f"Failed to test relay: {e}")
finally:
    GPIO.cleanup()
