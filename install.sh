#!/bin/bash

# install.sh
#
# This script automates the setup of the WALTR Firmware Installer project.
# It performs the following steps:
# 1. Updates system packages and installs necessary tools (git, python3, pip).
# 2. Clones or updates the Git repository.
# 3. Installs Python dependencies using pip.
# 4. Creates and installs a Systemd service file to run the main application
#    automatically on boot.
# 5. Starts the Systemd service.
#
# Usage:
#   bash install.sh
#
# IMPORTANT:
#   - Replace "YOUR_GIT_REPO_URL_HERE" with your actual Git repository URL.
#   - It requires 'sudo' privileges for system-level operations.

# Exit immediately if a command exits with a non-zero status.
set -e

# --- Configuration ---
REPO_URL="https://github.com/waltrdotin/firmwareUpload.git" 
INSTALL_DIR="$HOME/firmwareUpload"
VENV_DIR="${INSTALL_DIR}/venv"
SERVICE_NAME="waltr_firmware_installer"
SERVICE_FILE="${SERVICE_NAME}.service"
PYTHON_SCRIPT="installer.py"
USER_TO_RUN_AS=$(whoami)

# --- Functions ---

install_system_dependencies() {
    echo "--- Updating package lists and installing system dependencies ---"
    sudo apt update
    sudo apt install -y git python3 python3-pip
    echo "System dependencies (git, python3, pip) installed."
}
setup_pigpiod_service() {
    echo "--- Setting up pigpiod service ---"
    sudo systemctl enable pigpiod
    sudo systemctl start pigpiod
    if sudo systemctl is-active --quiet pigpiod; then
        echo "pigpiod service is active (running)."
    else
        echo "WARNING: pigpiod service failed to start. Please check 'sudo systemctl status pigpiod'."
    fi
}

clone_or_update_repo() {
    echo "--- Cloning or updating Git repository ---"
    if [ -d "$INSTALL_DIR" ]; then
        echo "Installation directory '$INSTALL_DIR' already exists. Pulling latest changes..."
        cd "$INSTALL_DIR"
        git pull
    else
        echo "Cloning '$REPO_URL' into '$INSTALL_DIR'..."
        git clone "$REPO_URL" "$INSTALL_DIR"
        cd "$INSTALL_DIR"
    fi
    echo "Repository cloned/updated successfully."
}
setup_virtual_environment() {
    echo "--- Setting up Python virtual environment ---"
    if [ ! -d "$VENV_DIR" ]; then
        echo "Creating virtual environment at '$VENV_DIR'..."
        python3 -m venv "$VENV_DIR"
        echo "Virtual environment created."
    else
        echo "Virtual environment already exists at '$VENV_DIR'."
    fi
}

install_python_dependencies() {
    echo "--- Installing Python dependencies ---"
    if [ ! -f "requirements.txt" ]; then
        echo "requirements.txt not found. Generating a basic one."
        echo "gpiozero" > requirements.txt
        echo "esptool" >> requirements.txt
        echo "requests" >> requirements.txt
        echo "dotenv" >> requirements.txt
    fi
   "$VENV_DIR/bin/python" -m pip3 install -r requirements.txt
    echo "Python dependencies installed."
}

create_and_install_systemd_service() {
    echo "--- Creating and installing Systemd service file ---"
    SERVICE_FILE_PATH="/etc/systemd/system/${SERVICE_FILE}"

    # Create the service file content using a 'here-document'
    cat <<EOF | sudo tee "$SERVICE_FILE_PATH"
[Unit]
Description=WALTR Firmware Installer Service
After=network.target

[Service]
ExecStart=${VENV_DIR}/bin/python ${INSTALL_DIR}/${PYTHON_SCRIPT}
WorkingDirectory=${INSTALL_DIR}
Restart=always
User=${USER_TO_RUN_AS}
Group=${USER_TO_RUN_AS}
Environment=PYTHONUNBUFFERED=1

[Install]
WantedBy=multi-user.target # Start when the system enters multi-user runlevel
EOF

    echo "Systemd service file created at '$SERVICE_FILE_PATH'"
    sudo systemctl daemon-reload
    sudo systemctl enable "${SERVICE_NAME}"
    echo "Systemd service enabled to start on boot."
}

# Function to start the Systemd service
start_systemd_service() {
    echo "--- Starting Systemd service ---"
    sudo systemctl start "${SERVICE_NAME}"
    echo "Service started. You can check its status with: sudo systemctl status ${SERVICE_NAME}"
    echo "To view live logs from the service, use: journalctl -u ${SERVICE_NAME} -f"
    echo "To stop the service: sudo systemctl stop ${SERVICE_NAME}"
    echo "To restart the service: sudo systemctl restart ${SERVICE_NAME}"
}

# --- Main Execution ---
echo "--- Starting WALTR Firmware Installer Setup ---"

# Check if the script is run with root privileges (or can use sudo)
if [[ $EUID -ne 0 ]]; then
    echo "This script requires 'sudo' privileges for system package installation and Systemd service management."
    echo "You may be prompted for your password during execution."
fi

install_system_dependencies

setup_pigpiod_service

clone_or_update_repo

setup_virtual_environment

install_python_dependencies

create_and_install_systemd_service

start_systemd_service

echo "--- WALTR Firmware Installer Setup Complete! ---"
echo "The service should now be running in the background."
echo "If you make changes to your code, remember to pull them and restart the service:"
echo "cd ${INSTALL_DIR} && git pull && sudo systemctl restart ${SERVICE_NAME}"



