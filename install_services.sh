#!/bin/bash

# Ensure script is run as root
if [ "$EUID" -ne 0 ]; then 
  echo "Please run this script with sudo: sudo ./install_services.sh"
  exit
fi

PROJECT_DIR="/home/meddispenser/Pill-Dispenser"
PI_USER="meddispenser"

echo "Creating Backend Service..."
cat <<EOF > /etc/systemd/system/pill-backend.service
[Unit]
Description=Smart Pill Dispenser Backend & Hardware Daemon
After=network.target bluetooth.target

[Service]
User=$PI_USER
WorkingDirectory=$PROJECT_DIR
# Try to connect bluetooth before starting the server
ExecStartPre=/bin/bash $PROJECT_DIR/backend/bt_autoconnect.sh
ExecStart=$PROJECT_DIR/venv/bin/uvicorn backend.main:app --host 0.0.0.0 --port 8000
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
EOF

echo "Creating Frontend Service..."
cat <<EOF > /etc/systemd/system/pill-frontend.service
[Unit]
Description=Smart Pill Dispenser Frontend (React/Vite)
After=network.target pill-backend.service

[Service]
User=$PI_USER
WorkingDirectory=$PROJECT_DIR/frontend
ExecStart=/usr/bin/npm run dev
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
EOF

echo "Enabling and Starting Services..."
systemctl daemon-reload
systemctl enable pill-backend.service
systemctl enable pill-frontend.service

echo "================================================="
echo "Done! The background services are installed and will start automatically on every boot."
echo "You can manually start them right now without rebooting by running:"
echo "sudo systemctl start pill-backend"
echo "sudo systemctl start pill-frontend"
echo "================================================="
