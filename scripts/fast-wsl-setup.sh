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

# Progress spinner function
spinner() {
    local pid=$1
    local delay=0.1
    local spinstr='|/-\'
    while ps -p $pid > /dev/null; do
        local temp=${spinstr#?}
        printf " [%c]  " "$spinstr"
        local spinstr=$temp${spinstr%"$temp"}
        sleep $delay
        printf "\b\b\b\b\b\b"
    done
    printf "    \b\b\b\b"
}

print_yellow "Starting optimized setup..."

# Create virtual environment
VENV_DIR=".venv"
if [ ! -d "$VENV_DIR" ]; then
    print_yellow "Creating virtual environment..."
    python3 -m venv "$VENV_DIR"
fi

# Activate virtual environment
source "$VENV_DIR/bin/activate"

# Install CPU-only version of PyTorch (much smaller download)
print_yellow "Installing PyTorch (CPU version - faster installation)..."
pip install --no-cache-dir torch --index-url https://download.pytorch.org/whl/cpu &
spinner $!

print_yellow "Installing other required packages..."
pip install --no-cache-dir safetensors numpy &
spinner $!

# Verify installation
print_yellow "Verifying installations..."
if python3 -c "import torch; import safetensors; import numpy; print('Packages verified!')" &> /dev/null; then
    print_green "All packages installed successfully!"
else
    print_red "Package verification failed!"
    exit 1
fi

# Run conversion
print_yellow "Starting model conversion..."
print_yellow "Note: This step may take several minutes depending on your system..."
python3 convert.py --input "../Llama-3.2-3B-Instruct" --output "../model.gguf"

print_green "Setup complete!"
print_yellow "To activate this environment later, run:"
print_green "source .venv/bin/activate"