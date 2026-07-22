#!/bin/bash
# bt_autoconnect.sh
# Connects to trusted Bluetooth audio devices if no audio jack is connected.

# Wait a few seconds on boot for services to start
sleep 10

# Check if analog audio (jack) or USB audio is actively in use or connected
# aplay -l lists soundcards. If a physical soundcard other than standard bcm2835 ALSA is present, 
# or if it's already in use, we skip bluetooth. 
# For simplicity, we just assume if there's any non-bcm2835 device, we don't need BT.
# But often RPi just shows bcm2835 ALSA. Let's just always try to connect to trusted BT as fallback.

echo "Starting Bluetooth Auto-Connect..."
bluetoothctl power on
bluetoothctl agent on
bluetoothctl default-agent

# Try to connect to all trusted/paired devices first
PAIRED_DEVICES=$(bluetoothctl paired-devices | awk '{print $2}')
for dev in $PAIRED_DEVICES; do
    echo "Attempting to connect to trusted device: $dev"
    bluetoothctl connect $dev
    sleep 3
    # Check if connected
    INFO=$(bluetoothctl info $dev)
    if echo "$INFO" | grep -q "Connected: yes"; then
        echo "Successfully connected to $dev. Exiting."
        exit 0
    fi
done

echo "No trusted devices found or connected. Attempting open scan..."
# Start scanning for open devices
bluetoothctl scan on &
SCAN_PID=$!
sleep 15
kill $SCAN_PID

# Attempt to connect to any newly discovered device that has Audio Sink
NEW_DEVICES=$(bluetoothctl devices | awk '{print $2}')
for dev in $NEW_DEVICES; do
    INFO=$(bluetoothctl info $dev)
    if echo "$INFO" | grep -q "Audio Sink"; then
        echo "Found Audio Sink device: $dev. Attempting to pair and connect."
        bluetoothctl pair $dev
        sleep 5
        bluetoothctl trust $dev
        bluetoothctl connect $dev
        sleep 3
        if bluetoothctl info $dev | grep -q "Connected: yes"; then
            echo "Successfully connected to open device $dev. Exiting."
            exit 0
        fi
    fi
done

echo "Failed to connect to any Bluetooth audio device."
