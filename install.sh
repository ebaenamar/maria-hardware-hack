#!/bin/bash
# Installation script for PiCar-X Feedback Loop
# Run on Raspberry Pi with PiCar-X

set -e

echo "=========================================="
echo "PiCar-X Feedback Loop - Installation"
echo "=========================================="
echo ""

# Verify we are on Raspberry Pi
if [ ! -f /proc/device-tree/model ]; then
    echo "WARNING: This doesn't appear to be a Raspberry Pi"
    read -p "Continue anyway? (y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

echo "1. Updating system..."
sudo apt-get update

echo ""
echo "2. Installing system dependencies..."
sudo apt-get install -y \
    python3-pip \
    python3-dev \
    portaudio19-dev \
    python3-pyaudio \
    git \
    alsa-utils \
    libasound2-dev

echo ""
echo "3. Installing robot-hat..."
if [ ! -d "/tmp/robot-hat" ]; then
    cd /tmp
    git clone -b v2.0 https://github.com/sunfounder/robot-hat.git
    cd robot-hat
    sudo python3 setup.py install
    cd -
else
    echo "robot-hat already downloaded, skipping..."
fi

echo ""
echo "4. Installing picar-x..."
if [ ! -d "/tmp/picar-x" ]; then
    cd /tmp
    git clone -b v2.0 https://github.com/sunfounder/picar-x.git
    cd picar-x
    sudo python3 setup.py install
    cd -
else
    echo "picar-x already downloaded, skipping..."
fi

echo ""
echo "5. Installing Python dependencies..."
pip3 install -r requirements.txt

echo ""
echo "6. Downloading Vosk model (English)..."
VOSK_MODEL_DIR="$HOME/vosk-model-small-en-us-0.15"
if [ ! -d "$VOSK_MODEL_DIR" ]; then
    cd $HOME
    wget https://alphacephei.com/vosk/models/vosk-model-small-en-us-0.15.zip
    unzip vosk-model-small-en-us-0.15.zip
    rm vosk-model-small-en-us-0.15.zip
    echo "Vosk model installed at: $VOSK_MODEL_DIR"
else
    echo "Vosk model already exists, skipping..."
fi

echo ""
echo "7. Configuring I2S for audio..."
if [ -f "/tmp/picar-x/i2samp.sh" ]; then
    cd /tmp/picar-x
    sudo bash i2samp.sh
else
    echo "WARNING: i2samp.sh script not found"
fi

echo ""
echo "8. Creating directories..."
mkdir -p $HOME/Pictures/feedback_loop

echo ""
echo "9. Setting permissions..."
chmod +x examples/*.py

echo ""
echo "=========================================="
echo "Installation completed!"
echo "=========================================="
echo ""
echo "NEXT STEPS:"
echo ""
echo "1. Configure API keys (optional, only for LLM):"
echo "   cp config/secret.py.example config/secret.py"
echo "   nano config/secret.py"
echo ""
echo "2. Test microphone (if using voice control):"
echo "   arecord -l  # List audio devices"
echo "   arecord -d 5 test.wav && aplay test.wav"
echo ""
echo "3. Calibrate PiCar-X:"
echo "   cd /tmp/picar-x/example"
echo "   sudo python3 calibration.py"
echo ""
echo "4. Run basic example:"
echo "   sudo python3 examples/basic_loop.py"
echo ""
echo "5. View documentation:"
echo "   cat README.md"
echo "   cat ARCHITECTURE.md"
echo ""
echo "Enjoy your PiCar-X with feedback loop!"
echo ""
