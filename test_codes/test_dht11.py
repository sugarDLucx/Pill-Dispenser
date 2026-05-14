import time
import board
import adafruit_dht

# Initial the dht device, with data pin connected to:
# board.D4 corresponds to GPIO 4
dhtDevice = adafruit_dht.DHT11(board.D4)

def test_dht():
    try:
        # Read the temperature and humidity
        temperature_c = dhtDevice.temperature
        humidity = dhtDevice.humidity
        print(f"Temperature: {temperature_c:.1f} C    Humidity: {humidity}%")
    except RuntimeError as error:
        # Errors happen fairly often on DHT sensors, so we catch them
        print(f"RuntimeError: {error.args[0]}")
    except Exception as error:
        dhtDevice.exit()
        raise error
        
if __name__ == "__main__":
    print("Starting DHT11 test...")
    try:
        for i in range(5):
            print(f"Reading {i+1}/5:")
            test_dht()
            time.sleep(2.0)
    finally:
        dhtDevice.exit()
        print("DHT11 test completed.")
