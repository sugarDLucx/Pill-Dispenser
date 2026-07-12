import time

try:
    import RPi.GPIO as GPIO
except ImportError:
    print("Warning: RPi.GPIO not found. Mocking for testing on non-RPI device.")
    class MockGPIO:
        BCM = "BCM"
        OUT = "OUT"
        def setmode(self, mode): pass
        def setup(self, pin, mode): pass
        def output(self, pin, state): pass
        def cleanup(self): pass
        class PWM:
            def __init__(self, pin, freq): pass
            def start(self, duty): pass
            def ChangeDutyCycle(self, duty): pass
            def stop(self): pass
    GPIO = MockGPIO()

# Define the GPIO pin connected to the servo
SERVO_PIN = 18

def setup_servo():
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(SERVO_PIN, GPIO.OUT)
    # 50Hz is standard for servos (20ms period)
    pwm = GPIO.PWM(SERVO_PIN, 50)
    # Start with 0 duty cycle so it doesn't immediately jitter
    pwm.start(0)
    return pwm

def set_angle(pwm, angle):
    """
    Moves the servo to the specified angle, waits for it to reach the position,
    and then stops sending the PWM signal to prevent jitter.
    """
    print(f"Moving servo to {angle} degrees...")
    
    # Calculate duty cycle (usually 2 to 12 for 0 to 180 degrees)
    # 2% = 0 deg, 12% = 180 deg. This formula might need slight tuning for specific servos.
    duty = 2.0 + (angle / 18.0)
    
    # Enable output and send duty cycle
    GPIO.output(SERVO_PIN, True)
    pwm.ChangeDutyCycle(duty)
    
    # Pause to allow the servo to achieve the set angle physically
    time.sleep(1.0)
    
    # Stop sending the signal to prevent jittering (RPI software PWM issue)
    GPIO.output(SERVO_PIN, False)
    pwm.ChangeDutyCycle(0)
    
    # Pause at the end to stabilize before next command
    time.sleep(0.5)

def main():
    print("Starting RPI direct Servo test (Jitter-free)...")
    pwm = setup_servo()
    
    try:
        # Move through a few angles
        set_angle(pwm, 0)
        set_angle(pwm, 90)
        set_angle(pwm, 180)
        set_angle(pwm, 90)
        set_angle(pwm, 0)
    except KeyboardInterrupt:
        print("\nTest interrupted by user.")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        print("Cleaning up GPIO...")
        pwm.stop()
        GPIO.cleanup()
        print("Done.")

if __name__ == "__main__":
    main()
