import time
import threading
from datetime import datetime, timedelta
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
from backend.audio_engine import play_audio

# --- Hardware Setup ---
BUTTON_PIN = 17
RELAY_PIN = 27
DHT_PIN = 4
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
    servos = {i: servo.Servo(pca.channels[i]) for i in range(10)}
except Exception as e:
    print(f"Error initializing PCA9685: {e}")

dht_device = None
try:
    dht_device = adafruit_dht.DHT11(getattr(board, f'D{DHT_PIN}')) if board else adafruit_dht.DHT11(None)
except Exception as e:
    print(f"Error initializing DHT11: {e}")

# --- Global State Machine ---
is_dispense_window_active = False
active_compartment_id = None
dispense_start_time = None
current_temperature = 0

def send_sms(phone_number: str, message: str):
    if not phone_number:
        return
    try:
        ser = serial.Serial(SIM_UART_PORT, SIM_BAUDRATE, timeout=1)
        ser.write(b"AT+CMGF=1\r")
        time.sleep(0.5)
        ser.write(f'AT+CMGS="{phone_number}"\r'.encode())
        time.sleep(0.5)
        ser.write(message.encode() + b"\r")
        time.sleep(0.5)
        ser.write(bytes([26])) # CTRL+Z
        time.sleep(2)
        ser.close()
        print(f"SMS sent to {phone_number}")
    except Exception as e:
        print(f"Error sending SMS to {phone_number}: {e}")

def parse_sms_command(sender: str, message: str):
    message = message.strip().lower()
    parts = message.split()
    if not parts:
        return

    db = SessionLocal()
    settings = db.query(SystemSettings).first()
    if not settings:
        settings = SystemSettings()
        db.add(settings)
        db.commit()

    # Basic authorization: If user or caretakers exist, require sender to be one. 
    # For initial setup, we might allow it, but we assume the user can always set.
    
    cmd = parts[0]
    try:
        if cmd == "user" and len(parts) >= 2:
            settings.user_mobile = parts[1]
            db.commit()
            print(f"User mobile set to {parts[1]}")
        elif cmd == "addcare" and len(parts) >= 2:
            current = settings.caretakers if settings.caretakers else ""
            if parts[1] not in current:
                settings.caretakers = f"{current},{parts[1]}" if current else parts[1]
                db.commit()
                print(f"Caretaker added: {parts[1]}")
        elif cmd == "add" and len(parts) >= 5:
            # add [Compartment ID 1-10] [Medicine Name] [Frequency] [Time]...
            comp_id = int(parts[1])
            med_name = parts[2]
            freq = parts[3]
            times = ",".join(parts[4:])
            
            sch = db.query(MedicationSchedule).filter(MedicationSchedule.compartment_id == comp_id).first()
            if not sch:
                sch = MedicationSchedule(compartment_id=comp_id)
                db.add(sch)
            sch.medicine_name = med_name
            sch.frequency = freq
            sch.time_slots = times
            sch.start_date = datetime.now().date()
            sch.end_date = datetime.now().date() + timedelta(days=365)
            db.commit()
            print(f"Schedule added for comp {comp_id}")
        elif cmd == "edit" and len(parts) >= 5:
            # edit [Compartment ID 1-10] [Medicine Name] [Frequency] [Time]...
            comp_id = int(parts[1])
            sch = db.query(MedicationSchedule).filter(MedicationSchedule.compartment_id == comp_id).first()
            if sch:
                sch.medicine_name = parts[2]
                sch.frequency = parts[3]
                sch.time_slots = ",".join(parts[4:])
                db.commit()
                print(f"Schedule edited for comp {comp_id}")
        elif cmd == "remove" and len(parts) >= 2:
            med_name = parts[1]
            schs = db.query(MedicationSchedule).filter(MedicationSchedule.medicine_name.ilike(med_name)).all()
            for s in schs:
                db.delete(s)
            db.commit()
            print(f"Removed schedules for {med_name}")
    except Exception as e:
        print(f"Error parsing SMS command '{message}': {e}")
    finally:
        db.close()

def sms_monitoring_loop():
    while True:
        try:
            ser = serial.Serial(SIM_UART_PORT, SIM_BAUDRATE, timeout=1)
            ser.write(b"AT+CMGF=1\r")
            time.sleep(0.5)
            ser.write(b'AT+CMGL="REC UNREAD"\r')
            time.sleep(1)
            response = ser.read(ser.in_waiting).decode(errors='ignore')
            ser.close()

            # Naive parsing of AT+CMGL response
            # +CMGL: 1,"REC UNREAD","+1234567890",,"26/07/22,12:00:00+32"
            # message text
            lines = response.split('\n')
            current_sender = None
            for line in lines:
                line = line.strip()
                if line.startswith("+CMGL:"):
                    parts = line.split(",")
                    if len(parts) >= 3:
                        current_sender = parts[2].strip('"')
                elif current_sender and line and not line.startswith("OK"):
                    parse_sms_command(current_sender, line)
                    current_sender = None

        except Exception as e:
            # Serial might be unavailable
            pass
        time.sleep(10)

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
        except RuntimeError:
            pass
        time.sleep(5)

def mark_medicine_taken():
    global is_dispense_window_active, active_compartment_id, dispense_start_time
    
    if not is_dispense_window_active:
        print("Button pressed but outside dispense window. Ignoring.")
        return

    print("Dispensing pills...")
    play_audio("dispensing.mp3")
    
    # Rotate servo
    try:
        if active_compartment_id:
            s = servos.get(active_compartment_id - 1)
            if s:
                s.angle = 90
                time.sleep(1)
                s.angle = 0
    except Exception as e:
        print(f"Servo error: {e}")

    # Reset State
    is_dispense_window_active = False
    active_compartment_id = None
    dispense_start_time = None
    
    play_audio("done_dispensing.mp3")
    time.sleep(3)
    play_audio("satisfied.mp3")

def handle_missed_medication(schedule):
    global is_dispense_window_active, active_compartment_id, dispense_start_time
    is_dispense_window_active = False
    active_compartment_id = None
    dispense_start_time = None

    play_audio("missed_alert.mp3")

    db = SessionLocal()
    settings = db.query(SystemSettings).first()
    db.close()
    
    if not settings:
        return

    alert_msg = f"ALERT: Patient missed scheduled medication. Slot: {schedule.compartment_id}, Med: {schedule.medicine_name}, Freq: {schedule.frequency}."
    user_msg = "Reminder: You missed your scheduled medication. Please take it immediately."

    if settings.user_mobile:
        send_sms(settings.user_mobile, user_msg)
    
    if settings.caretakers:
        for number in settings.caretakers.split(","):
            number = number.strip()
            if number:
                send_sms(number, alert_msg)

def main_loop():
    global is_dispense_window_active, active_compartment_id, dispense_start_time
    print("Starting hardware daemon main loop...")
    threading.Thread(target=temp_monitoring_loop, daemon=True).start()
    threading.Thread(target=sms_monitoring_loop, daemon=True).start()
    
    last_dispensed_minute = None

    while True:
        now = datetime.now()
        
        # Check Button Physical press
        if getattr(med_button, 'is_pressed', False):
            mark_medicine_taken()
            
        # State Machine Window
        if is_dispense_window_active:
            if dispense_start_time and (now - dispense_start_time).total_seconds() > 300:
                print("5 minute timer expired!")
                # Get the schedule to include in alert
                db = SessionLocal()
                schedule = db.query(MedicationSchedule).filter(MedicationSchedule.compartment_id == active_compartment_id).first()
                db.close()
                handle_missed_medication(schedule)
            time.sleep(0.1)
            continue

        # Check DB for scheduled times
        current_time_str = now.strftime("%H:%M")
        
        # Only trigger once per minute
        if current_time_str != last_dispensed_minute:
            db = SessionLocal()
            current_date = now.date()
            schedules = db.query(MedicationSchedule).filter(
                MedicationSchedule.start_date <= current_date,
                MedicationSchedule.end_date >= current_date
            ).all()

            triggered = False
            for schedule in schedules:
                if not schedule.time_slots: continue
                times = [t.strip() for t in schedule.time_slots.split(",")]
                if current_time_str in times:
                    print(f"Scheduled time reached for {schedule.medicine_name}")
                    is_dispense_window_active = True
                    active_compartment_id = schedule.compartment_id
                    dispense_start_time = now
                    last_dispensed_minute = current_time_str
                    
                    play_audio("scheduled_time.mp3")
                    
                    # Notify user
                    settings = db.query(SystemSettings).first()
                    if settings and settings.user_mobile:
                        send_sms(settings.user_mobile, f"It is time to take your medication: {schedule.medicine_name}")
                    triggered = True
                    break # only trigger one schedule at an exact minute to avoid conflict
            db.close()
            
        time.sleep(0.5)

if __name__ == "__main__":
    main_loop()
