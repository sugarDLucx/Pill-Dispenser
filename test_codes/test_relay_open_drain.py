import RPi.GPIO as GPIO
import time

RELAY_PIN = 26
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

print("Testing Open Drain Relay Logic.")

# Float the pin (Input mode) -> Should turn OFF
print("Setting pin to INPUT (Floating). Cooler should be OFF.")
GPIO.setup(RELAY_PIN, GPIO.IN)
time.sleep(5)

# Drive the pin LOW (Output mode) -> Should turn ON
print("Setting pin to OUTPUT LOW (0V). Cooler should be ON.")
GPIO.setup(RELAY_PIN, GPIO.OUT)
GPIO.output(RELAY_PIN, GPIO.LOW)
time.sleep(5)

# Float the pin again -> Should turn OFF
print("Setting pin back to INPUT (Floating). Cooler should be OFF.")
GPIO.setup(RELAY_PIN, GPIO.IN)
time.sleep(5)

print("Done. Did it successfully turn OFF and ON?")
