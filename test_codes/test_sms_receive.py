import serial
import time
import sys

# Replace with the port and baud rate that succeeded in test_sim800l.py
PORT = '/dev/serial0'
BAUD = 9600

def send_at_command(ser, command, wait_time=0.5, expected="OK"):
    print(f"Sending: {command}")
    ser.write((command + '\r\n').encode('ascii'))
    time.sleep(wait_time)
    
    if ser.in_waiting:
        response = ser.read(ser.in_waiting).decode('ascii', errors='ignore').strip()
        print(f"Response: {response}")
        if expected in response:
            return True
        return False
    else:
        print("Response: (No response)")
        return False

def test_receive_sms():
    print("=======================================")
    print("   SIM800L SMS RECEIVE TEST SCRIPT")
    print("=======================================\n")
    print(f"Attempting to listen for SMS on {PORT} @ {BAUD} baud...")
    
    try:
        ser = serial.Serial(PORT, baudrate=BAUD, timeout=1)
        
        # 1. Wake up / Auto-baud
        print("\n[*] Initializing SIM800L...")
        initialized = False
        for _ in range(5):
            if send_at_command(ser, "AT", 0.5):
                initialized = True
                break
                
        if not initialized:
            print("[ERROR] Failed to communicate with SIM800L.")
            ser.close()
            sys.exit(1)
            
        # 2. Check Network Registration (Need to be registered to receive)
        print("\n[*] Checking Network Registration...")
        send_at_command(ser, "AT+CREG?", 1)
        
        # 3. Set SMS to Text Mode
        print("\n[*] Setting SMS to Text Mode...")
        if not send_at_command(ser, "AT+CMGF=1", 1):
            print("[ERROR] Failed to set text mode. SIM might not be ready.")
            ser.close()
            sys.exit(1)
            
        # 4. Route incoming SMS directly to Serial port (instead of saving to SIM memory)
        print("\n[*] Routing incoming SMS directly to terminal...")
        if not send_at_command(ser, "AT+CNMI=1,2,0,0,0", 1):
            print("[WARNING] Failed to set CNMI routing. You might need to read from memory instead.")
        
        print("\n=======================================")
        print(" MODULE READY. WAITING FOR INCOMING SMS...")
        print(" (Send a text message to the SIM card now!)")
        print(" Press Ctrl+C to stop listening.")
        print("=======================================\n")
        
        while True:
            if ser.in_waiting:
                incoming_data = ser.readline().decode('ascii', errors='ignore').strip()
                if incoming_data:
                    # +CMT indicates an incoming text message in the format:
                    # +CMT: "+639123456789","","23/07/22,15:30:00+32"
                    # <Message Body>
                    if incoming_data.startswith("+CMT:"):
                        print("\n[!] NEW SMS RECEIVED [!]")
                        print(f"Header: {incoming_data}")
                        
                        # The next line is the actual message body
                        time.sleep(0.1) 
                        if ser.in_waiting:
                            message_body = ser.read(ser.in_waiting).decode('ascii', errors='ignore').strip()
                            print(f"Message: {message_body}")
                            print("---------------------------------------")
                    else:
                        # Print any other status messages from the module
                        print(f"[SIM800L]: {incoming_data}")
                        
            time.sleep(0.1)
            
    except KeyboardInterrupt:
        print("\n\n[*] Stopped listening for SMS. Closing port.")
        ser.close()
    except Exception as e:
        print(f"\n[ERROR] {e}")

if __name__ == '__main__':
    test_receive_sms()
