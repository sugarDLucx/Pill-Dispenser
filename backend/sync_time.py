import serial
import time
import subprocess
from datetime import datetime

SIM_UART_PORT = "/dev/serial0"
SIM_BAUDRATE = 9600

def sync_time():
    print("Opening connection to SIM800L for Time Sync...")
    try:
        ser = serial.Serial(SIM_UART_PORT, SIM_BAUDRATE, timeout=2)
        
        # Ensure automatic time sync is enabled on the module
        ser.write(b"AT+CLTS=1\r")
        time.sleep(0.5)
        
        # Query current clock
        ser.write(b"AT+CCLK?\r")
        time.sleep(1)
        response = ser.read(ser.in_waiting or 100).decode(errors='ignore')
        ser.close()
        
        # Example response: +CCLK: "23/08/01,10:00:00+32"
        for line in response.split('\n'):
            line = line.strip()
            if line.startswith("+CCLK:"):
                # Extract the timestamp inside the quotes
                time_str = line.split('"')[1]
                # '23/08/01,10:00:00+32' -> strip timezone
                dt_str = time_str.split('+')[0].split('-')[0]
                
                if dt_str.startswith("04/01/01"):
                    print("SIM module has not synced with the cellular network yet...")
                    return False
                
                # Parse to datetime
                dt = datetime.strptime(dt_str, "%y/%m/%d,%H:%M:%S")
                
                print(f"Network Time Found: {dt}")
                # Set system time using standard 'date' command formatting
                subprocess.run(["sudo", "date", "-s", dt.strftime("%Y-%m-%d %H:%M:%S")])
                print("System time successfully synchronized to cellular network!")
                return True
                
    except Exception as e:
        print(f"Failed to sync time: {e}")
        
    return False

def run_sync_loop():
    print("Starting Offline Time Sync via Cellular Network...")
    for _ in range(12): # Try for 120 seconds while waiting for network registration
        if sync_time():
            break
        print("Retrying in 10 seconds...")
        time.sleep(10)

if __name__ == "__main__":
    run_sync_loop()
