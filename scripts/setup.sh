#!/bin/bash

# Define colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Print colored output
print_green() {
    echo -e "${GREEN}$1${NC}"
}

print_yellow() {
    echo -e "${YELLOW}$1${NC}"
}

print_red() {
    echo -e "${RED}$1${NC}"
}

# Get script directory and project root
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_ROOT="$( cd "$SCRIPT_DIR/.." && pwd )"

# Install required system packages
print_yellow "Installing required system packages..."
sudo apt-get update && sudo apt-get install -y python3-full python3-pip python3-venv

# Remove existing virtual environment if it exists
if [ -d "$SCRIPT_DIR/.venv" ]; then
    print_yellow "Removing existing virtual environment..."
    rm -rf "$SCRIPT_DIR/.venv"
fi

# Create fresh virtual environment
print_yellow "Creating new virtual environment..."
python3 -m venv "$SCRIPT_DIR/.venv"

# Activate virtual environment
print_yellow "Activating virtual environment..."
source "$SCRIPT_DIR/.venv/bin/activate"

# Upgrade pip
print_yellow "Upgrading pip..."
python3 -m pip install --upgrade pip

# Install required packages
print_yellow "Installing required packages..."
pip install --no-cache-dir torch --index-url https://download.pytorch.org/whl/cpu
pip install --no-cache-dir safetensors numpy

# Verify installations
print_yellow "Verifying installations..."
if python3 -c "import torch; import safetensors; import numpy; print('All packages installed successfully!')"; then
    print_green "Package verification successful!"
else
    print_red "Package verification failed!"
    exit 1
fi

# Run the conversion script
print_yellow "Running conversion script..."
print_yellow "Input directory: $PROJECT_ROOT/Llama-3.2-3B-Instruct"
print_yellow "Output file: $PROJECT_ROOT/model.gguf"

if python3 convert.py --input "$PROJECT_ROOT/Llama-3.2-3B-Instruct" --output "$PROJECT_ROOT/model.gguf"; then
    print_green "Conversion completed successfully!"
else
    print_red "Conversion failed. Check the error messages above."
    exit 1
fi

# Deactivate virtual environment
deactivate

print_green "Process complete!"
print_yellow "To activate this environment again, run:"
print_green "source $SCRIPT_DIR/.venv/bin/activate"