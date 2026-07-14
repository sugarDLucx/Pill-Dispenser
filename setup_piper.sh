#!/bin/bash

# Exit on error
set -e

echo "Starting Piper TTS setup for Raspberry Pi (AArch64)..."

# Create a directory for piper
mkdir -p backend/piper
cd backend/piper

echo "Detecting OS architecture..."
BITNESS=$(getconf LONG_BIT)
if [ "$BITNESS" = "64" ]; then
    echo "Detected 64-bit OS user space."
    PIPER_URL="https://github.com/rhasspy/piper/releases/download/2023.11.14-2/piper_linux_aarch64.tar.gz"
else
    echo "Detected 32-bit OS user space."
    PIPER_URL="https://github.com/rhasspy/piper/releases/download/2023.11.14-2/piper_linux_armv7l.tar.gz"
fi

# Download Piper binary
echo "Downloading Piper from $PIPER_URL ..."
wget -qO piper.tar.gz "$PIPER_URL"

# Extract
echo "Extracting Piper..."
tar -xf piper.tar.gz --strip-components=1
rm piper.tar.gz

# Download the en_US-lessac-low model
echo "Downloading en_US-lessac-low model..."
wget -qO en_US-lessac-low.onnx https://huggingface.co/rhasspy/piper-voices/resolve/v1.0.0/en/en_US/lessac/low/en_US-lessac-low.onnx?download=true
wget -qO en_US-lessac-low.onnx.json https://huggingface.co/rhasspy/piper-voices/resolve/v1.0.0/en/en_US/lessac/low/en_US-lessac-low.onnx.json?download=true

echo "Piper setup complete!"
echo "You can test it by running: echo 'Hello world' | ./piper --model en_US-lessac-low.onnx --output_file test.wav"
