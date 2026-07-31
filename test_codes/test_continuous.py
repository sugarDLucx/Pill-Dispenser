import time
import board
import busio
from adafruit_pca9685 import PCA9685
from adafruit_motor import servo

def test_continuous():
    print("Initializing I2C bus and PCA9685...")
    try:
        i2c = busio.I2C(board.SCL, board.SDA)
        pca = PCA9685(i2c)
        pca.frequency = 50
    except Exception as e:
        print(f"Failed to initialize PCA9685: {e}")
        return

    # Slot 6 is mapped to PCA Channel 8 (16 - 8 based on your swapped mapping)
    print("\n--- Testing Servo 6 as a CONTINUOUS ROTATION Servo ---")
    s = servo.ContinuousServo(pca.channels[8])

    try:
        print("Spinning FORWARD for 1 second...")
        s.throttle = 1.0  # Full speed forward
        time.sleep(1.0)
        
        print("STOPPING for 1 second...")
        s.throttle = 0.0  # Stop
        time.sleep(1.0)
        
        print("Spinning BACKWARD for 1 second...")
        s.throttle = -1.0  # Full speed backward
        time.sleep(1.0)
        
        print("STOPPING.")
        s.throttle = 0.0
        
    except Exception as e:
        print(f"Error: {e}")
    finally:
        # Release the PCA9685
        pca.deinit()

if __name__ == "__main__":
    test_continuous()
