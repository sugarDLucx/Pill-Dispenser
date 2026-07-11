#!/bin/bash

# Exit on error
set -e

echo "Starting Piper TTS setup for Raspberry Pi (AArch64)..."

# Create a directory for piper
mkdir -p backend/piper
cd backend/piper

# Download Piper binary for aarch64
echo "Downloading Piper..."
wget -qO piper.tar.gz https://github.com/rhasspy/piper/releases/download/v1.2.0/piper_linux_aarch64.tar.gz

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
