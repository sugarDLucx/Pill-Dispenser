from gpiozero import OutputDevice
import time

print("Testing Relay Logic.")
relay = OutputDevice(26, active_high=True, initial_value=False)

print("Relay is set to LOW (0V).")
print("Is the cooler ON or OFF?")
time.sleep(5)

relay.on()
print("Relay is set to HIGH (3.3V).")
print("Is the cooler ON or OFF?")
time.sleep(5)
print("Done.")
