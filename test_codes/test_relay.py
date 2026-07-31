import time
from gpiozero import OutputDevice

# Relay is on GPIO 27. 
# Most relay modules are active LOW, meaning pulling the pin to Ground (LOW) turns it ON.
RELAY_PIN = 27

try:
    print(f"Initializing Relay on GPIO {RELAY_PIN}...")
    # active_high=False means .on() pulls it LOW (turns relay ON), .off() pulls it HIGH (turns relay OFF)
    relay = OutputDevice(RELAY_PIN, active_high=False)
    
    print("Testing Relay...")
    for i in range(3):
        print(f"[{i+1}/3] Turning ON (You should hear a click)...")
        relay.on()
        time.sleep(2)
        
        print(f"[{i+1}/3] Turning OFF...")
        relay.off()
        time.sleep(2)

    print("Test Complete!")
except Exception as e:
    print(f"Failed to test relay: {e}")
