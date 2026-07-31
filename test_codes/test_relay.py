import time
from gpiozero import DigitalOutputDevice

RELAY_PIN = 26

try:
    print(f"Initializing Relay on GPIO {RELAY_PIN} as raw digital output...")
    # Using DigitalOutputDevice avoids active_high abstractions so we know exactly what voltage is sent.
    relay = DigitalOutputDevice(RELAY_PIN)
    
    print("\n[Test 1] Sending 3.3V (HIGH) to the signal pin...")
    relay.on() 
    time.sleep(3)
    
    print("\n[Test 2] Pulling signal pin to 0V (LOW/GND)...")
    relay.off()
    time.sleep(3)

    print("\nTest Complete! Did the relay click during Test 1 or Test 2?")
    relay.close()
except Exception as e:
    print(f"Failed to test relay: {e}")
