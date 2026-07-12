import time
from gpiozero import Button

BUTTON_PIN = 17

def test_button():
    try:
        button = Button(BUTTON_PIN)
        print(f"Testing Button on GPIO {BUTTON_PIN}.")
        print("Please press the button...")
        
        # Wait for button press
        button.wait_for_press(timeout=10.0)
        
        if button.is_pressed:
            print("Button press detected successfully!")
        else:
            print("No button press detected within 10 seconds.")
            
    except Exception as e:
        print(f"Error testing button: {e}")

if __name__ == "__main__":
    print("Starting Button test...")
    test_button()
    print("Button test completed.")
