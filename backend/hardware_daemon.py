import time
import threading
from datetime import datetime
import serial

try:
    from gpiozero import Button, OutputDevice
except ImportError:
    print("Warning: gpiozero not found. Mocking Button and Relay.")
    class Button:
        def __init__(self, pin): self.pin = pin; self.is_pressed = False
    class OutputDevice:
        def __init__(self, pin): self.pin = pin; self.value = 0
        def on(self): self.value = 1
        def off(self): self.value = 0

try:
    import board
    import busio
    from adafruit_pca9685 import PCA9685
    from adafruit_motor import servo
except ImportError:
    print("Warning: adafruit libraries not found. Mocking I2C Servos.")
    board = None
    class PCA9685:
        def __init__(self, i2c): self.frequency = 50; self.channels = [None]*16
    class _MockServo:
        def __init__(self): self.angle = 0
    class servo:
        Servo = lambda channel: _MockServo()

try:
    import adafruit_dht
except ImportError:
    print("Warning: adafruit_dht not found. Mocking DHT11.")
    class adafruit_dht:
        DHT11 = lambda pin: type("MockDHT", (), {"temperature": 24, "measure": lambda: None, "exit": lambda: None})()

from backend.database import SessionLocal
from backend.models import MedicationSchedule, SystemSettings
from backend.audio_engine import play_announcement

# --- Hardware Setup ---
# Pins are placeholders
BUTTON_PIN = 17
RELAY_PIN = 27
DHT_PIN = 4 # board.D4 if using board
SIM_UART_PORT = "/dev/ttyS0"
SIM_BAUDRATE = 9600

# Initialize Hardware Variables
med_button = None
cooling_relay = None
try:
    med_button = Button(BUTTON_PIN)
    cooling_relay = OutputDevice(RELAY_PIN)
except Exception as e:
    print(f"Error initializing GPIO: {e}")

servos = {}
try:
    i2c = busio.I2C(board.SCL, board.SDA) if board else None
    pca = PCA9685(i2c) if i2c else PCA9685(None)
    pca.frequency = 50
    # Setup 10 servos
    servos = {i: servo.Servo(pca.channels[i]) for i in range(10)}
except Exception as e:
    print(f"Error initializing PCA9685: {e}")

dht_device = None
try:
    dht_device = adafruit_dht.DHT11(getattr(board, f'D{DHT_PIN}')) if board else adafruit_dht.DHT11(None)
except Exception as e:
    print(f"Error initializing DHT11: {e}")

# --- Global State ---
active_timer = None
alarm_active = False
current_temperature = 0

def send_sms(message: str):
    db = SessionLocal()
    settings = db.query(SystemSettings).first()
    db.close()
    if not settings:
        print("No settings found, skipping SMS.")
        return

    numbers = [settings.caretaker_primary_mobile, settings.caretaker_secondary_mobile]
    try:
        ser = serial.Serial(SIM_UART_PORT, SIM_BAUDRATE, timeout=1)
        for number in numbers:
            if not number: continue
            ser.write(b"AT+CMGF=1\r")
            time.sleep(0.5)
            ser.write(f'AT+CMGS="{number}"\r'.encode())
            time.sleep(0.5)
            ser.write(message.encode() + b"\r")
            time.sleep(0.5)
            ser.write(bytes([26])) # CTRL+Z
            time.sleep(2)
        ser.close()
    except Exception as e:
        print(f"Error sending SMS: {e}")

def alarm_timeout_handler():
    global alarm_active
    if alarm_active:
        print("Alarm timeout! Pill not taken. Sending SMS...")
        send_sms("ALERT: The patient has not taken their scheduled medication.")
        alarm_active = False

def dispense_pill(compartment_id: int, medicine_name: str):
    global alarm_active, active_timer
    print(f"Dispensing {medicine_name} from compartment {compartment_id}")
    
    # Rotate servo
    try:
        s = servos.get(compartment_id - 1)
        if s:
            s.angle = 90
            time.sleep(1)
            s.angle = 0
    except Exception as e:
        print(f"Servo error: {e}")
        
    # Play Audio
    play_announcement(medicine_name)
    
    # Start 5-min timer (300 seconds)
    alarm_active = True
    if active_timer:
        active_timer.cancel()
    active_timer = threading.Timer(300.0, alarm_timeout_handler)
    active_timer.start()

def mark_medicine_taken():
    global alarm_active, active_timer
    if alarm_active:
        print("Medicine taken. Cancelling alarm.")
        alarm_active = False
        if active_timer:
            active_timer.cancel()
            active_timer = None

def temp_monitoring_loop():
    global current_temperature
    while True:
        try:
            if hasattr(dht_device, 'temperature'):
                temp = dht_device.temperature
                if temp is not None:
                    current_temperature = temp
                    if temp > 25:
                        if cooling_relay: cooling_relay.on()
                    else:
                        if cooling_relay: cooling_relay.off()
        except RuntimeError as error:
            # Errors happen fairly often, DHT's are hard to read, just keep going
            pass
        except Exception as e:
            pass
        time.sleep(5)

def main_loop():
    print("Starting hardware daemon main loop...")
    threading.Thread(target=temp_monitoring_loop, daemon=True).start()
    
    while True:
        now = datetime.now()
        current_time_str = now.strftime("%H:%M")
        current_date = now.date()

        # Check Button
        if getattr(med_button, 'is_pressed', False):
            mark_medicine_taken()

        # Check DB
        db = SessionLocal()
        schedules = db.query(MedicationSchedule).filter(
            MedicationSchedule.start_date <= current_date,
            MedicationSchedule.end_date >= current_date
        ).all()

        for schedule in schedules:
            times = schedule.time_slots.split(",")
            if current_time_str in times:
                # We need to ensure we only trigger once for this minute
                # A simple way is to check if we just triggered this one
                # For robustness, you'd store 'last_dispensed_time' in DB
                if now.second < 5: # Trigger only in first 5 seconds of the minute
                    dispense_pill(schedule.compartment_id, schedule.medicine_name)

        db.close()
        time.sleep(1)

if __name__ == "__main__":
    main_loop()
