#!/bin/bash

# Exit on error
set -e

echo "Starting Piper TTS setup for Raspberry Pi (AArch64)..."

# Create a directory for piper
mkdir -p backend/piper
cd backend/piper

echo "Detecting OS architecture..."
ARCH=$(uname -m)
if [ "$ARCH" = "aarch64" ] || [ "$ARCH" = "arm64" ]; then
    PIPER_URL="https://github.com/rhasspy/piper/releases/download/2023.11.14-2/piper_linux_aarch64.tar.gz"
elif [ "$ARCH" = "armv7l" ] || [ "$ARCH" = "armhf" ] || [ "$ARCH" = "armv6l" ]; then
    PIPER_URL="https://github.com/rhasspy/piper/releases/download/2023.11.14-2/piper_linux_armv7l.tar.gz"
else
    # Fallback to aarch64 if unknown, but warn
    echo "Warning: Unknown architecture $ARCH. Defaulting to aarch64."
    PIPER_URL="https://github.com/rhasspy/piper/releases/download/2023.11.14-2/piper_linux_aarch64.tar.gz"
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
