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

    # Map Slot ID (1-10) to PCA9685 Channels
    servo_mapping = {i: 16 - i for i in range(1, 11)}
    servo_mapping[7] = 8
    servo_mapping[8] = 9
    
    servos = {i: servo.Servo(pca.channels[servo_mapping[i]]) for i in range(1, 11)}

    print("\n--- Starting Servo Sequence Test ---")
    print("Each servo will rotate to 70 degrees, pause, and return to 110 degrees.")

    try:
        for slot_id in range(1, 11):
            s = servos[slot_id]
            print(f"Testing Slot {slot_id} (PCA Channel {servo_mapping[slot_id]})...")
            
            if slot_id == 6:
                s.angle = 5
                time.sleep(1.0)
                s.angle = 37
            else:
                s.angle = 70
                time.sleep(1.0)
                s.angle = 110
                
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
