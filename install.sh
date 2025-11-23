#!/bin/bash
# Script de instalación para PiCar-X Feedback Loop
# Ejecutar en Raspberry Pi con PiCar-X

set -e

echo "=========================================="
echo "PiCar-X Feedback Loop - Instalación"
echo "=========================================="
echo ""

# Verificar que estamos en Raspberry Pi
if [ ! -f /proc/device-tree/model ]; then
    echo "ADVERTENCIA: No parece ser una Raspberry Pi"
    read -p "¿Continuar de todas formas? (y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

echo "1. Actualizando sistema..."
sudo apt-get update

echo ""
echo "2. Instalando dependencias del sistema..."
sudo apt-get install -y \
    python3-pip \
    python3-dev \
    portaudio19-dev \
    python3-pyaudio \
    git

echo ""
echo "3. Instalando robot-hat..."
if [ ! -d "/tmp/robot-hat" ]; then
    cd /tmp
    git clone -b v2.0 https://github.com/sunfounder/robot-hat.git
    cd robot-hat
    sudo python3 setup.py install
    cd -
else
    echo "robot-hat ya descargado, saltando..."
fi

echo ""
echo "4. Instalando picar-x..."
if [ ! -d "/tmp/picar-x" ]; then
    cd /tmp
    git clone -b v2.0 https://github.com/sunfounder/picar-x.git
    cd picar-x
    sudo python3 setup.py install
    cd -
else
    echo "picar-x ya descargado, saltando..."
fi

echo ""
echo "5. Instalando dependencias de Python..."
pip3 install -r requirements.txt

echo ""
echo "6. Descargando modelo Vosk (inglés)..."
VOSK_MODEL_DIR="$HOME/vosk-model-small-en-us-0.15"
if [ ! -d "$VOSK_MODEL_DIR" ]; then
    cd $HOME
    wget https://alphacephei.com/vosk/models/vosk-model-small-en-us-0.15.zip
    unzip vosk-model-small-en-us-0.15.zip
    rm vosk-model-small-en-us-0.15.zip
    echo "Modelo Vosk instalado en: $VOSK_MODEL_DIR"
else
    echo "Modelo Vosk ya existe, saltando..."
fi

echo ""
echo "7. Configurando I2S para audio..."
if [ -f "/tmp/picar-x/i2samp.sh" ]; then
    cd /tmp/picar-x
    sudo bash i2samp.sh
else
    echo "ADVERTENCIA: Script i2samp.sh no encontrado"
fi

echo ""
echo "8. Creando directorios..."
mkdir -p $HOME/Pictures/feedback_loop

echo ""
echo "9. Configurando permisos..."
chmod +x examples/*.py

echo ""
echo "=========================================="
echo "Instalación completada!"
echo "=========================================="
echo ""
echo "PRÓXIMOS PASOS:"
echo ""
echo "1. Configurar API keys (opcional, solo para LLM):"
echo "   cp config/secret.py.example config/secret.py"
echo "   nano config/secret.py"
echo ""
echo "2. Calibrar el PiCar-X:"
echo "   cd /tmp/picar-x/example"
echo "   sudo python3 calibration.py"
echo ""
echo "3. Ejecutar ejemplo básico:"
echo "   sudo python3 examples/basic_loop.py"
echo ""
echo "4. Ver documentación:"
echo "   cat README.md"
echo "   cat ARCHITECTURE.md"
echo ""
echo "¡Disfruta tu PiCar-X con feedback loop!"
echo ""
