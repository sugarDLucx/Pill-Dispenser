import time
import board
import adafruit_dht

# DHT pin is configured to GPIO 19 (Physical Pin 35)
DHT_PIN = board.D19

print("Initializing DHT11 Sensor on GPIO 19...")
dht_device = None

try:
    # Initialize the DHT11 device
    dht_device = adafruit_dht.DHT11(DHT_PIN)
    
    print("Reading sensor data... (Press Ctrl+C to stop)\n")
    
    while True:
        try:
            # Read temperature and humidity
            temperature_c = dht_device.temperature
            humidity = dht_device.humidity
            
            if temperature_c is not None and humidity is not None:
                print(f"Temp: {temperature_c:.1f} °C  |  Humidity: {humidity}%")
            else:
                print("Failed to retrieve data from sensor (None returned).")
                
        except RuntimeError as error:
            # DHT sensors often throw RuntimeErrors if they are read too quickly or if the Pi misses the timing
            print(f"Sensor read error (retrying): {error.args[0]}")
        except Exception as error:
            if dht_device:
                dht_device.exit()
            raise error
            
        # DHT11 requires a minimum of 2 seconds between reads
        time.sleep(2.0)
        
except KeyboardInterrupt:
    print("\nTest stopped by user.")
finally:
    if dht_device:
        dht_device.exit()
