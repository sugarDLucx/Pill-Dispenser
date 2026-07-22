# Smart Pill Dispenser - Raspberry Pi Setup Guide

This guide will walk you through setting up the Smart Pill Dispenser hardware and software on a Raspberry Pi.

## 1. Hardware Requirements & Wiring

You will need a robust **5V 10A Power Supply** to power the entire system. 
**Important**: Power the SIM module, cooling relay, and PCA9685 directly from the power supply, NOT through the Raspberry Pi's 5V pins to prevent brownouts.

For a detailed breakdown of all GPIO pins and connections, please read the `WIRING_PINOUT.txt` file located in the root of this project.

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
3. **Generate Audio Files**:
   We use pre-recorded `.mp3` files for audio feedback. Run the provided script to generate the default voice lines using Google TTS:
   ```bash
   cd ~/Pill-Dispenser
   python backend/generate_audio.py
   ```
   *(Ensure you have internet access during this step. After this, the system works offline).*

4. **Enable Bluetooth Auto-Connect Daemon**:
   To automatically connect to your trusted Bluetooth speakers on boot, make the script executable:
   ```bash
   chmod +x backend/bt_autoconnect.sh
   ```

5. **Test the Backend**:
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
   Create `/etc/systemd/system/pill-backend.service` to auto-start the Python server on boot. Include a line to execute `bt_autoconnect.sh` before the main application starts.
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
