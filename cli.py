import sys
import requests

def main():
    if len(sys.argv) < 2:
        print("Pill Dispenser CLI Control")
        print("Usage: python3 cli.py <command>")
        print("\nExamples:")
        print("  python3 cli.py list")
        print("  python3 cli.py add 1 Losartan Daily 08:00AM, 08:00PM")
        print("  python3 cli.py remove Losartan")
        print("  python3 cli.py cool on")
        print("  python3 cli.py user +1234567890")
        sys.exit(1)

    cmd = " ".join(sys.argv[1:])
    try:
        resp = requests.post("http://127.0.0.1:8000/api/command", json={"command": cmd})
        if resp.status_code == 200:
            data = resp.json()
            print(data.get("response", "Command executed."))
        else:
            print(f"Error: Backend returned status code {resp.status_code}")
    except requests.exceptions.ConnectionError:
        print("Error: Could not connect to the backend. Is the pill-backend.service running?")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
