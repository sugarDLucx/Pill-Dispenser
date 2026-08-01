import time
import threading
from datetime import datetime, timedelta
import serial
import RPi.GPIO as GPIO

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
BUTTON_PIN = 21
RELAY_PIN = 26
DHT_PIN = 19
SIM_UART_PORT = "/dev/ttyS0"
SIM_BAUDRATE = 9600

# Initialize Hardware Variables
class OpenDrainRelay:
    def __init__(self, pin):
        self.pin = pin
        GPIO.setmode(GPIO.BCM)
        GPIO.setwarnings(False)
        self.off() # Start in OFF state (floating)
        
    def on(self):
        GPIO.setup(self.pin, GPIO.OUT)
        GPIO.output(self.pin, GPIO.LOW)
        
    def off(self):
        GPIO.setup(self.pin, GPIO.IN)

med_button = None
cooling_relay = None
try:
    med_button = Button(BUTTON_PIN)
    cooling_relay = OpenDrainRelay(RELAY_PIN)
except Exception as e:
    print(f"Error initializing GPIO: {e}")

servos = {}
try:
    i2c = busio.I2C(board.SCL, board.SDA) if board else None
    pca = PCA9685(i2c) if i2c else PCA9685(None)
    pca.frequency = 50
    # Map Slot ID (1-10) to PCA9685 Channels
    # Default is Slot 1 -> Channel 15, Slot 10 -> Channel 6
    servo_mapping = {i: 16 - i for i in range(1, 11)}
    
    servos = {i: servo.Servo(pca.channels[servo_mapping[i]]) for i in range(1, 11)}
except Exception as e:
    print(f"Error initializing PCA9685: {e}")

dht_device = None
try:
    dht_device = adafruit_dht.DHT11(getattr(board, f'D{DHT_PIN}')) if board else adafruit_dht.DHT11(None)
except Exception as e:
    print(f"Error initializing DHT11: {e}")

# --- Global State Machine ---
is_dispense_window_active = False
active_compartment_ids = []
dispense_start_time = None
current_temperature = 0
current_humidity = 0
cooling_active = False
cooling_mode = "auto" # 'auto', 'on', 'off'

cli_last_response = []

def send_sms(phone_number: str, message: str):
    if not phone_number:
        return
        
    if phone_number == "CLI":
        global cli_last_response
        cli_last_response.append(message)
        print(f"\n[CLI Response]: {message}\n")
        return

    # SMS length limit is 160 characters. Chunk by 150 to be safe.
    chunks = [message[i:i+150] for i in range(0, len(message), 150)]
    
    for i, chunk in enumerate(chunks):
        try:
            # If multipart, add a small page indicator like (1/2) if we want, but slicing is fine
            if len(chunks) > 1:
                prefix = f"({i+1}/{len(chunks)}) "
                # adjust chunk if prefix makes it too long, but for simplicity we'll just prepend
                chunk_data = (prefix + chunk)[:160]
            else:
                chunk_data = chunk

            ser = serial.Serial(SIM_UART_PORT, SIM_BAUDRATE, timeout=1)
            ser.write(b"AT+CMGF=1\r")
            time.sleep(0.5)
            ser.write(f'AT+CMGS="{phone_number}"\r'.encode())
            time.sleep(0.5)
            ser.write(chunk_data.encode() + b"\r")
            time.sleep(0.5)
            ser.write(bytes([26])) # CTRL+Z
            time.sleep(3)
            ser.close()
            print(f"SMS chunk sent to {phone_number}")
            time.sleep(1) # Pause before sending next chunk
        except Exception as e:
            print(f"Error sending SMS to {phone_number}: {e}")

def parse_sms_command(sender: str, message: str):
    global cooling_mode, cooling_active
    message = message.strip()
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
    
    cmd = parts[0].lower()
    
    def reply_users():
        db.refresh(settings)
        u = settings.user_mobile or "None"
        c = settings.caretakers or "None"
        send_sms(sender, f"User: {u}\nCare: {c}")

    def reply_schedules():
        schs = db.query(MedicationSchedule).order_by(MedicationSchedule.compartment_id).all()
        if not schs:
            send_sms(sender, "No pills scheduled.")
            return
        lines = []
        for s in schs:
            times = []
            if s.time_slots:
                for t in s.time_slots.split(","):
                    t = t.strip()
                    if t:
                        try:
                            h, m = t.split(":")
                            hour = int(h)
                            ampm = "PM" if hour >= 12 else "AM"
                            hour = hour % 12
                            hour = hour if hour else 12
                            times.append(f"{hour:02d}:{m}{ampm}")
                        except ValueError:
                            times.append(t)
            times_str = ",".join(times)
            lines.append(f"{s.compartment_id}:{s.medicine_name}({times_str})")
        msg = "\n".join(lines)
        send_sms(sender, f"Pills:\n{msg}")

    try:
        if cmd == "user" and len(parts) >= 2:
            settings.user_mobile = parts[1]
            db.commit()
            reply_users()
        elif cmd == "addcare" and len(parts) >= 2:
            current = settings.caretakers if settings.caretakers else ""
            if parts[1] not in current:
                settings.caretakers = f"{current},{parts[1]}" if current else parts[1]
                db.commit()
            reply_users()
        elif cmd == "removecare" and len(parts) >= 2:
            target = parts[1]
            if settings.caretakers:
                cares = [c.strip() for c in settings.caretakers.split(",") if c.strip() and c.strip() != target]
                settings.caretakers = ",".join(cares)
                db.commit()
            reply_users()
        elif cmd == "add" and len(parts) >= 5:
            # add [Compartment ID 1-10] [Medicine Name] [Frequency] [Time]...
            comp_id = int(parts[1])
            med_name = parts[2]
            freq = parts[3]
            raw_times = " ".join(parts[4:]).upper()
            raw_times = raw_times.replace(" AM", "AM").replace(" PM", "PM")
            time_list = [t.strip() for t in raw_times.split(",") if t.strip()]
            parsed_times = []
            for t in time_list:
                try:
                    if "AM" in t or "PM" in t:
                        parsed_times.append(datetime.strptime(t, "%I:%M%p").strftime("%H:%M"))
                    else:
                        parsed_times.append(datetime.strptime(t, "%H:%M").strftime("%H:%M"))
                except ValueError:
                    parsed_times.append(t)
            times = ",".join(parsed_times)
            
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
            reply_schedules()
        elif cmd == "remove" and len(parts) >= 2:
            med_name = parts[1]
            schs = db.query(MedicationSchedule).filter(MedicationSchedule.medicine_name.ilike(med_name)).all()
            for s in schs:
                db.delete(s)
            db.commit()
            reply_schedules()
        elif cmd == "list":
            db.refresh(settings)
            u = settings.user_mobile or "None"
            c = settings.caretakers or "None"
            schs = db.query(MedicationSchedule).order_by(MedicationSchedule.compartment_id).all()
            
            lines = []
            for s in schs:
                times = []
                if s.time_slots:
                    for t in s.time_slots.split(","):
                        t = t.strip()
                        if t:
                            try:
                                h, m = t.split(":")
                                hour = int(h)
                                ampm = "PM" if hour >= 12 else "AM"
                                hour = hour % 12
                                hour = hour if hour else 12
                                times.append(f"{hour:02d}:{m}{ampm}")
                            except ValueError:
                                times.append(t)
                times_str = ",".join(times)
                lines.append(f"{s.compartment_id}:{s.medicine_name}({times_str})")
            msg = "\n".join(lines) if lines else "None"
            
            final_msg = f"User:{u}\nCare:{c}\nPills:\n{msg}"
            send_sms(sender, final_msg)
        elif cmd == "cool" and len(parts) >= 2:
            subcmd = parts[1].lower()
            if subcmd == "off":
                cooling_mode = "off"
                cooling_active = False
                if cooling_relay: cooling_relay.off()
                send_sms(sender, "Cooling forced OFF")
            elif subcmd == "on":
                cooling_mode = "on"
                cooling_active = True
                if cooling_relay: cooling_relay.on()
                send_sms(sender, "Cooling forced ON")
            elif subcmd == "auto":
                cooling_mode = "auto"
                send_sms(sender, "Cooling set to AUTO")
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
            ser.write(b'AT+CMGL="ALL"\r')
            time.sleep(1)
            
            lines = ser.readlines()
            
            i = 0
            while i < len(lines):
                line = lines[i].decode('utf-8', errors='ignore').strip()
                if line.startswith("+CMGL:"):
                    parts = line.split(",")
                    if len(parts) >= 3:
                        sender = parts[2].strip('"')
                        # Next line is the message
                        if i + 1 < len(lines):
                            message = lines[i+1].decode('utf-8', errors='ignore').strip()
                            print(f"Received SMS from {sender}: {message}")
                            
                            # Delete it from SIM memory immediately
                            index = parts[0].replace("+CMGL:", "").strip()
                            ser.write(f"AT+CMGD={index}\r".encode())
                            time.sleep(0.5)
                            
                            # Close port before processing so send_sms can acquire it
                            ser.close()
                            
                            parse_sms_command(sender, message)
                            
                            # Re-open for the remainder of the loop if multiple messages exist
                            ser = serial.Serial(SIM_UART_PORT, SIM_BAUDRATE, timeout=1)
                i += 1
                
            if ser.is_open:
                ser.close()
                
        except Exception as e:
            print(f"Error in sms_monitoring_loop: {e}")
            try:
                if 'ser' in locals() and ser.is_open:
                    ser.close()
            except:
                pass
            
        time.sleep(5)

last_cooler_run_time = None

def temp_monitoring_loop():
    global current_temperature, current_humidity, cooling_active, cooling_mode, last_cooler_run_time
    cooler_on_duration = 120 # 2 minutes
    cooler_cooldown_interval = 1800 # 30 minutes
    
    while True:
        try:
            try:
                if hasattr(dht_device, 'temperature'):
                    temp = dht_device.temperature
                    hum = dht_device.humidity
                    if temp is not None: current_temperature = temp
                    if hum is not None: current_humidity = hum
            except Exception as dht_err:
                pass
                
            now = datetime.now()
            
            if cooling_mode == "on":
                if not cooling_active:
                    cooling_active = True
                    last_cooler_run_time = now
                    if cooling_relay: cooling_relay.on()
            elif cooling_mode == "off":
                if cooling_active:
                    cooling_active = False
                    if cooling_relay: cooling_relay.off()
            else:
                # Auto mode logic
                if cooling_active:
                    # If it is currently running, check if 2 minutes have passed
                    if last_cooler_run_time and (now - last_cooler_run_time).total_seconds() >= cooler_on_duration:
                        cooling_active = False
                        if cooling_relay: cooling_relay.off()
                    elif last_cooler_run_time is None:
                        # Fallback if it somehow got stuck running without a start time
                        last_cooler_run_time = now
                else:
                    # If it is off, check if 30 minutes have passed since the start of the last run
                    can_run = False
                    if last_cooler_run_time is None:
                        can_run = True
                    else:
                        if (now - last_cooler_run_time).total_seconds() >= cooler_cooldown_interval:
                            can_run = True
                            
                    if can_run and current_temperature > 32.0:
                        cooling_active = True
                        last_cooler_run_time = now
                        if cooling_relay: cooling_relay.on()
        except Exception as e:
            print(f"Error in temp_monitoring_loop: {e}")
                    
        time.sleep(5)

def mark_medicine_taken():
    global is_dispense_window_active, active_compartment_ids, dispense_start_time
    
    if not is_dispense_window_active:
        print("Button pressed but outside dispense window. Ignoring.")
        return

    print("Dispensing pills...")
    play_audio("dispensing.wav")
    
    # Rotate servo
    try:
        for comp_id in active_compartment_ids:
            s = servos.get(comp_id)
            if s:
                if comp_id == 10:
                    s.angle = 60
                    time.sleep(1)
                    s.angle = 110
                elif comp_id == 4:
                    s.angle = 65
                    time.sleep(1)
                    s.angle = 110
                else:
                    s.angle = 70
                    time.sleep(1)
                    s.angle = 110
                    
                time.sleep(0.5) # Wait for servo to physically travel back
                s.angle = None  # Release the servo to stop jittering
    except Exception as e:
        print(f"Servo error: {e}")

    # Reset State
    is_dispense_window_active = False
    active_compartment_ids = []
    dispense_start_time = None
    
    play_audio("done_dispensing.wav")
    time.sleep(3)
    play_audio("satisfied.wav")

def handle_missed_medication(schedules):
    global is_dispense_window_active, active_compartment_ids, dispense_start_time
    is_dispense_window_active = False
    active_compartment_ids = []
    dispense_start_time = None

    play_audio("missed_alert.wav")

    db = SessionLocal()
    settings = db.query(SystemSettings).first()
    db.close()
    
    if not schedules:
        return
        
    names = ", ".join([s.medicine_name for s in schedules])
    slots = ", ".join([str(s.compartment_id) for s in schedules])

    alert_msg = f"ALERT: Patient missed scheduled medication. Slots: {slots}, Meds: {names}."
    user_msg = "Reminder: You missed your scheduled medication. Please take it immediately."

    if settings.user_mobile:
        send_sms(settings.user_mobile, user_msg)
    
    if settings.caretakers:
        for number in settings.caretakers.split(","):
            number = number.strip()
            if number:
                send_sms(number, alert_msg)

def main_loop():
    global is_dispense_window_active, active_compartment_ids, dispense_start_time
    print("Starting hardware daemon main loop...")
    
    try:
        from sync_time import run_sync_loop
        threading.Thread(target=run_sync_loop, daemon=True).start()
    except Exception as e:
        print(f"Failed to start time sync thread: {e}")
        
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
                schedules = db.query(MedicationSchedule).filter(MedicationSchedule.compartment_id.in_(active_compartment_ids)).all()
                db.close()
                handle_missed_medication(schedules)
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
            matching_schedules = []
            for schedule in schedules:
                if not schedule.time_slots: continue
                times = [t.strip() for t in schedule.time_slots.split(",")]
                if current_time_str in times:
                    matching_schedules.append(schedule)
                    
            if matching_schedules:
                print(f"Scheduled time reached for {[s.medicine_name for s in matching_schedules]}")
                is_dispense_window_active = True
                active_compartment_ids = [s.compartment_id for s in matching_schedules]
                dispense_start_time = now
                last_dispensed_minute = current_time_str
                
                play_audio("scheduled_time.wav")
                
                # Notify user
                settings = db.query(SystemSettings).first()
                if settings and settings.user_mobile:
                    names = ", ".join([s.medicine_name for s in matching_schedules])
                    send_sms(settings.user_mobile, f"It is time to take your medication: {names}")
            db.close()
            
        time.sleep(0.5)

if __name__ == "__main__":
    main_loop()
