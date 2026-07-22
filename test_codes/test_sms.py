import serial
import time
import sys

# Replace with the port and baud rate that succeeded in test_sim800l.py
PORT = '/dev/serial0'
BAUD = 9600

def send_at_command(ser, command, wait_time=1, expected="OK"):
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

def test_send_sms():
    if len(sys.argv) < 2:
        print("Usage: python test_sms.py <your_phone_number>")
        print("Example: python test_sms.py +639123456789")
        sys.exit(1)
        
    phone_number = sys.argv[1]
    
    print(f"Attempting to send a test SMS to {phone_number} using {PORT} @ {BAUD} baud...")
    
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
            print("[ERROR] Failed to communicate with SIM800L. Did it pass test_sim800l.py?")
            ser.close()
            sys.exit(1)
            
        # 2. Check Network
        print("\n[*] Checking Network Registration...")
        send_at_command(ser, "AT+CREG?", 1)
        
        # 3. Set SMS to Text Mode
        print("\n[*] Setting SMS to Text Mode...")
        if not send_at_command(ser, "AT+CMGF=1", 1):
            print("[ERROR] Failed to set text mode. SIM might not be ready.")
            ser.close()
            sys.exit(1)
            
        # 4. Send the SMS
        print(f"\n[*] Sending SMS to {phone_number}...")
        ser.write(f'AT+CMGS="{phone_number}"\r\n'.encode('ascii'))
        time.sleep(1)
        
        # Wait for the '>' prompt
        response = ""
        if ser.in_waiting:
            response = ser.read(ser.in_waiting).decode('ascii', errors='ignore')
            
        if '>' in response:
            print("Prompt received. Sending message body...")
            message = "Hello from Smart Pill Dispenser! Hardware test successful."
            ser.write((message + chr(26)).encode('ascii')) # chr(26) is CTRL+Z
            
            print("Message sent! Waiting for confirmation (this can take up to 10 seconds)...")
            time.sleep(5)
            if ser.in_waiting:
                final_response = ser.read(ser.in_waiting).decode('ascii', errors='ignore').strip()
                print(f"Final Response: {final_response}")
                if "CMGS" in final_response or "OK" in final_response:
                    print("\n[SUCCESS] SMS sent successfully!")
                else:
                    print("\n[WARNING] Did not receive clear success confirmation.")
            else:
                print("\n[WARNING] No final confirmation received, but message might have sent.")
        else:
            print(f"[ERROR] Did not receive '>' prompt. Module replied with: {response}")

        ser.close()
        
    except Exception as e:
        print(f"\n[ERROR] {e}")

if __name__ == '__main__':
    test_send_sms()
