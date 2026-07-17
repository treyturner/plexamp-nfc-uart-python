#!/bin/bash
set -e

SERVICE_NAME="plexamp-nfc.service"
APP_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENV_DIR="$APP_DIR/venv"

echo "Updating system packages..."
sudo apt update
sudo apt install -y python3 python3-dev python3-pip python3-venv build-essential

echo "Creating virtual environment..."
if [ ! -d "$VENV_DIR" ]; then
  python3 -m venv "$VENV_DIR"
fi

echo "Installing Python requirements..."
source "$VENV_DIR/bin/activate"
pip install --upgrade pip
pip install -r "$APP_DIR/requirements.txt"
deactivate

echo "Installing systemd service..."
if [ ! -f "$APP_DIR/$SERVICE_NAME" ]; then
  echo "❌ ERROR: $SERVICE_NAME not found in $APP_DIR"
  exit 1
fi

sudo cp "$APP_DIR/$SERVICE_NAME" /etc/systemd/system/$SERVICE_NAME
sudo systemctl daemon-reload
sudo systemctl enable $SERVICE_NAME
sudo systemctl restart $SERVICE_NAME

echo "Installation complete!"
echo
echo "Check logs with:    sudo journalctl -f -u $SERVICE_NAME"
echo "Check status with:  systemctl status $SERVICE_NAME"
