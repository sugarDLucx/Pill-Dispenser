import serial
import time
import sys

# Common serial ports on Raspberry Pi
PORTS = ['/dev/serial0', '/dev/ttyAMA0', '/dev/ttyS0']
BAUDRATES = [9600, 115200, 19200, 38400]

def test_sim800l():
    print("=======================================")
    print(" SIM800L UART DIAGNOSTIC TEST SCRIPT")
    print("=======================================\n")
    
    found_response = False
    
    for port in PORTS:
        for baud in BAUDRATES:
            print(f"[*] Testing Port: {port} @ {baud} baud...")
            try:
                ser = serial.Serial(port, baudrate=baud, timeout=1)
                
                # Send AT multiple times to allow SIM800L auto-bauding to sync
                for i in range(5):
                    ser.write(b'AT\r\n')
                    time.sleep(0.5)
                    
                    if ser.in_waiting:
                        response = ser.read(ser.in_waiting).decode('ascii', errors='ignore').strip()
                        if 'OK' in response or 'AT' in response:
                            print(f"\n[SUCCESS] SIM800L responded on {port} at {baud} baud!")
                            print(f"[REPLY]: {response}")
                            
                            # Try to get more info
                            print("\n[*] Checking SIM Status...")
                            ser.write(b'AT+CPIN?\r\n')
                            time.sleep(1)
                            if ser.in_waiting:
                                print(f"[REPLY]: {ser.read(ser.in_waiting).decode('ascii', errors='ignore').strip()}")

                            print("\n[*] Checking Network Registration...")
                            ser.write(b'AT+CREG?\r\n')
                            time.sleep(1)
                            if ser.in_waiting:
                                print(f"[REPLY]: {ser.read(ser.in_waiting).decode('ascii', errors='ignore').strip()}")
                            
                            print("\n[*] Checking Signal Quality...")
                            ser.write(b'AT+CSQ\r\n')
                            time.sleep(1)
                            if ser.in_waiting:
                                print(f"[REPLY]: {ser.read(ser.in_waiting).decode('ascii', errors='ignore').strip()}")
                            
                            ser.close()
                            return
                
                ser.close()
            except PermissionError:
                print(f"[ERROR] Permission denied on {port}. Did you run with 'sudo' or are you in the 'dialout' group?")
                sys.exit(1)
            except serial.SerialException as e:
                # Port might not exist, skip
                pass
            except Exception as e:
                print(f"[ERROR] {e}")
                
    if not found_response:
        print("\n[FAILED] No response received from SIM800L on any port/baud rate combination.")
        print("\nTroubleshooting Checklist:")
        print("1. WIRING (RX/TX SWAPPED): The Pi's TXD (Pin 8) MUST go to the SIM800L's RXD. The Pi's RXD (Pin 10) MUST go to the SIM800L's TXD.")
        print("2. POWER: Is the SIM800L blinking? A fast blink (1x per sec) means it's searching for network. A slow blink (1x every 3 secs) means it's connected. No light = No power or not enough current (Requires 2 Amps!).")
        print("3. COMMON GROUND: Ensure the Pi and the SIM800L share the exact same ground connection.")
        print("4. RASPI-CONFIG: Did you enable the Serial Port in 'sudo raspi-config' -> Interface Options? Ensure you disabled the serial login shell, but enabled the serial hardware.")

if __name__ == '__main__':
    test_sim800l()
