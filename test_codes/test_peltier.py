import time
import RPi.GPIO as GPIO

# Define the GPIO pin connected to the relay for the Peltier module
# Example: GPIO 17
RELAY_PIN = 17 

def test_peltier():
    # Use BCM GPIO numbering
    GPIO.setmode(GPIO.BCM)
    GPIO.setwarnings(False)
    
    # Set the relay pin as an output pin
    GPIO.setup(RELAY_PIN, GPIO.OUT)
    
    try:
        print("Starting TEC-12706 Peltier test...")
        print("Turning ON the Peltier module (via Relay)...")
        # Depending on your relay module, HIGH might be ON or OFF. 
        # Typically, for Active-Low relays, LOW turns it ON.
        # Assuming Active-High for this test:
        GPIO.output(RELAY_PIN, GPIO.HIGH) 
        
        # Keep it on for 5 seconds to feel the temperature difference
        time.sleep(5) 
        
        print("Turning OFF the Peltier module...")
        GPIO.output(RELAY_PIN, GPIO.LOW)
        print("Peltier relay test completed successfully.")
        
    except KeyboardInterrupt:
        print("\nTest interrupted by user.")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        # Clean up GPIO state
        GPIO.cleanup()

if __name__ == "__main__":
    test_peltier()
