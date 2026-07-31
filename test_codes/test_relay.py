import time
from gpiozero import OutputDevice

# Relay is on GPIO 17. 
# Most relay modules are active LOW, meaning pulling the pin to Ground (LOW) turns it ON.
RELAY_PIN = 17

try:
    print(f"Initializing Relay on GPIO {RELAY_PIN} as ACTIVE HIGH...")
    relay = OutputDevice(RELAY_PIN, active_high=True)
    
    print("Testing Active-High Logic...")
    for i in range(2):
        print("Sending HIGH (3.3V)...")
        relay.on()
        time.sleep(2)
        print("Sending LOW (0V)...")
        relay.off()
        time.sleep(2)
        
    relay.close() # Free the pin
    
    print(f"\nInitializing Relay on GPIO {RELAY_PIN} as ACTIVE LOW...")
    relay = OutputDevice(RELAY_PIN, active_high=False)
    
    print("Testing Active-Low Logic...")
    for i in range(2):
        print("Sending LOW (0V)...")
        relay.on()
        time.sleep(2)
        print("Sending HIGH (3.3V)...")
        relay.off()
        time.sleep(2)

    print("\nTest Complete!")
    relay.close()
except Exception as e:
    print(f"Failed to test relay: {e}")
