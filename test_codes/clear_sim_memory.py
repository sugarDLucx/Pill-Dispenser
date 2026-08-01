import serial
import time

SIM_UART_PORT = "/dev/serial0"
SIM_BAUDRATE = 9600

def clear_sim_memory():
    print("Opening connection to SIM800L...")
    try:
        ser = serial.Serial(SIM_UART_PORT, SIM_BAUDRATE, timeout=2)
        
        # Ensure text mode
        ser.write(b"AT+CMGF=1\r")
        time.sleep(0.5)
        response = ser.read(ser.in_waiting or 100).decode(errors='ignore')
        print(f"AT+CMGF=1 Response: {response.strip()}")
        
        # Delete ALL messages
        print("Sending command to delete ALL SMS messages from SIM memory...")
        ser.write(b"AT+CMGD=1,4\r")
        time.sleep(2)
        
        response = ser.read(ser.in_waiting or 100).decode(errors='ignore')
        if "OK" in response:
            print("Successfully cleared all messages from SIM memory!")
        else:
            print(f"Unexpected response: {response.strip()}")
            
        ser.close()
    except Exception as e:
        print(f"Failed to clear SIM memory: {e}")

if __name__ == "__main__":
    # Wait a tiny bit just in case the backend is currently reading
    time.sleep(1)
    clear_sim_memory()
