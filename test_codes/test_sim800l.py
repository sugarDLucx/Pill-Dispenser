import serial
import time

# Configure the serial connection
# '/dev/serial0' is typically the primary UART on a Raspberry Pi
SERIAL_PORT = '/dev/serial0'
BAUD_RATE = 9600

def send_at_command(ser, command, wait_time=1):
    print(f"Sending: {command}")
    ser.write((command + '\r\n').encode('utf-8'))
    time.sleep(wait_time)
    
    if ser.in_waiting > 0:
        response = ser.read(ser.in_waiting).decode('utf-8').strip()
        print(f"Response:\n{response}\n")
        return response
    else:
        print("No response\n")
        return ""

def test_gsm():
    try:
        ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=1)
        time.sleep(1) # Wait for initialization
        
        print("Starting SIM800L GSM test...")
        
        # Check basic communication
        send_at_command(ser, 'AT')
        
        # Check signal quality
        send_at_command(ser, 'AT+CSQ')
        
        # Check network registration
        send_at_command(ser, 'AT+CREG?')
        
        ser.close()
        print("SIM800L test completed.")
    except Exception as e:
        print(f"Error testing SIM800L: {e}")

if __name__ == "__main__":
    test_gsm()
