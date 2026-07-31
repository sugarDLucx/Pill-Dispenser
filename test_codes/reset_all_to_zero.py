import time
import board
import busio
from adafruit_pca9685 import PCA9685
from adafruit_motor import servo

def reset_servos():
    print("Initializing I2C bus and PCA9685...")
    try:
        i2c = busio.I2C(board.SCL, board.SDA)
        pca = PCA9685(i2c)
        pca.frequency = 50
    except Exception as e:
        print(f"Failed to initialize PCA9685: {e}")
        return

    servos = {i: servo.Servo(pca.channels[16 - i]) for i in range(1, 11)}

    print("\n--- Resetting all servos to 180 degrees ---")

    try:
        for slot_id in range(1, 11):
            s = servos[slot_id]
            print(f"Resetting Slot {slot_id} to 180 degrees...")
            s.angle = 180
            time.sleep(0.5) # Give it half a second to move
            s.angle = None  # Turn off holding current
            
        print("\nAll servos successfully reset to 180 degrees!")
        
    except KeyboardInterrupt:
        print("\nTest cancelled by user.")
    except Exception as e:
        print(f"\nError during servo rotation: {e}")
    finally:
        pca.deinit()

if __name__ == "__main__":
    reset_servos()
