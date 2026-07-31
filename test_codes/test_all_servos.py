import time
import board
import busio
from adafruit_pca9685 import PCA9685
from adafruit_motor import servo

def test_servos():
    print("Initializing I2C bus and PCA9685...")
    try:
        i2c = busio.I2C(board.SCL, board.SDA)
        pca = PCA9685(i2c)
        pca.frequency = 50
    except Exception as e:
        print(f"Failed to initialize PCA9685: {e}")
        return

    # In our project, Compartments 1-10 are mapped to PCA Channels 15 down to 6
    # Slot 1 -> Channel 15
    # Slot 10 -> Channel 6
    servos = {i: servo.Servo(pca.channels[16 - i]) for i in range(1, 11)}

    print("\n--- Starting Servo Sequence Test ---")
    print("Each servo will rotate to 148 degrees, pause, and return to 180 degrees.")

    try:
        for slot_id in range(1, 11):
            s = servos[slot_id]
            print(f"Testing Slot {slot_id} (PCA Channel {16 - slot_id})...")
            
            # Rotate to 148 degrees
            s.angle = 148
            time.sleep(1.0)
            
            # Return to 180 degrees
            s.angle = 180
            time.sleep(0.5)
            
            # Release PWM signal to prevent jittering while resting
            s.angle = None
            
        print("\nAll servos tested successfully!")
        
    except KeyboardInterrupt:
        print("\nTest cancelled by user.")
    except Exception as e:
        print(f"\nError during servo rotation: {e}")
    finally:
        pca.deinit()

if __name__ == "__main__":
    test_servos()
