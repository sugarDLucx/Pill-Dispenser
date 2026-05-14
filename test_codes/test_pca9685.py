import time
from adafruit_servokit import ServoKit

# Set channels to the number of servo channels on your kit.
# PCA9685 supports 16 channels
kit = ServoKit(channels=16)

def test_servo(channel):
    print(f"Testing servo on channel {channel}")
    # Move to 0 degrees
    kit.servo[channel].angle = 0
    time.sleep(1)
    
    # Move to 90 degrees
    kit.servo[channel].angle = 90
    time.sleep(1)
    
    # Move to 180 degrees
    kit.servo[channel].angle = 180
    time.sleep(1)
    
    # Move back to 0 degrees
    kit.servo[channel].angle = 0

if __name__ == "__main__":
    try:
        print("Starting PCA9685 Servo test...")
        # Test the first servo on channel 0
        test_servo(0)
        print("PCA9685 test completed successfully.")
    except Exception as e:
        print(f"Error testing PCA9685: {e}")
