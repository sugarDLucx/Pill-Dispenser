# Smart Pill Dispenser - Raspberry Pi Setup Guide

This guide will walk you through setting up the Smart Pill Dispenser hardware and software on a Raspberry Pi.

## 1. Hardware Requirements & Wiring

You will need a robust **5V 10A Power Supply** to power the entire system. 
**Important**: Power the SIM module, cooling relay, and PCA9685 directly from the power supply, NOT through the Raspberry Pi's 5V pins to prevent brownouts.

### Pin Connections (Raspberry Pi Header)
*   **GPIO 23**: Medicine Taken Button (Input) - *Must not be 17, as the touchscreen uses 17 for touch interrupts!*
*   **GPIO 24**: Cooling Fan / Peltier Relay (Output) - *Must not be 27, as the touchscreen uses 27 for screen reset!*
*   **GPIO 4**: DHT11 Temperature Sensor (Data pin)
*   **GPIO 2 (SDA) & GPIO 3 (SCL)**: I2C connections for the PCA9685 Servo Controller.
*   **GPIO 14 (TXD) & GPIO 15 (RXD)**: UART connections for the GSM/SIM Module.

---

## 2. Operating System Configuration

1. Install Raspberry Pi OS (a 64-bit kernel with a 32-bit or 64-bit user space works, as our scripts auto-detect this).
2. Open the configuration tool:
   ```bash
   sudo raspi-config
   ```
3. **Enable I2C**: Go to `Interface Options` -> `I2C` -> Enable.
4. **Enable UART (Serial)**: Go to `Interface Options` -> `Serial Port`. 
   * *Would you like a login shell to be accessible over serial?* **NO**
   * *Would you like the serial port hardware to be enabled?* **YES**
5. Reboot the Raspberry Pi.

---

## 3. Backend Setup (FastAPI & Hardware Daemon)

1. **Clone/Move the project** to your Raspberry Pi, e.g., `/home/meddispenser/Pill-Dispenser`.
2. **Install Python dependencies**:
   ```bash
   sudo apt update
   sudo apt install python3-pip python3-venv portaudio19-dev
   
   cd ~/Pill-Dispenser
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```
3. **Install the Audio Engine (Piper TTS)**:
   We use Piper for offline Text-to-Speech. Run the provided setup script:
   ```bash
   cd ~/Pill-Dispenser/backend
   chmod +x setup_piper.sh
   ./setup_piper.sh
   ```
4. **Test the Backend**:
   ```bash
   cd ~/Pill-Dispenser
   source venv/bin/activate
   uvicorn backend.main:app --host 0.0.0.0 --port 8000
   ```
   *You should see the hardware daemon start up and the API become available.*

---

## 4. Frontend Setup (React/Vite)

1. **Install Node.js 20.x**:
   ```bash
   curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash -
   sudo apt-get install -y nodejs
   ```
   *(Verify installation by running `node -v` and `npm -v`)*
2. **Install frontend dependencies**:
   ```bash
   cd ~/Pill-Dispenser/frontend
   npm install
   ```
3. **Start the Frontend**:
   ```bash
   npm run dev
   ```
   *This will run the frontend on port 5173. You can access it via a browser.*

---

## 5. Setting up Kiosk Mode (Optional but Recommended)

If your Raspberry Pi has a touchscreen attached, you will want the UI to automatically launch in full-screen mode on boot.

1. **Create a Systemd Service for the Backend**:
   Create `/etc/systemd/system/pill-backend.service` to auto-start the Python server on boot.
2. **Create a Systemd Service for the Frontend**:
   You can either serve the built React app (`npm run build`) via a simple HTTP server or run Vite.
3. **Launch Chromium in Kiosk Mode**:
   Edit the autostart file for the Raspberry Pi GUI:
   ```bash
   nano ~/.config/wayfire.ini # Or ~/.config/lxsession/LXDE-pi/autostart depending on OS version
   ```
   Add the following line to launch the browser pointing to your local frontend:
   ```bash
   chromium-browser --kiosk --disable-pinch --overscroll-history-navigation=0 http://localhost:5173
   ```

## 6. Usage Notes
*   **Time Editor**: The frontend UI features a custom swipe-to-scroll time picker designed perfectly for the Pi's touchscreen.
*   **Audio Issues**: If no audio plays, verify that your speaker is plugged into the RPi audio jack or USB sound card, and check `alsamixer` to ensure the volume is turned up.
