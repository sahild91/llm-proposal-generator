#!/bin/bash
# LLM Proposal Generator Startup Script for Linux/macOS

set -e

echo "Starting LLM Proposal Generator..."
echo

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "ERROR: Python 3 is not installed or not in PATH"
    echo "Please install Python 3.7+ from https://python.org or your package manager"
    exit 1
fi

# Check Python version
python_version=$(python3 -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')")
if ! python3 -c "import sys; exit(0 if sys.version_info >= (3, 7) else 1)"; then
    echo "ERROR: Python 3.7+ is required. Found Python $python_version"
    exit 1
fi

# Check if main.py exists
if [ ! -f "main.py" ]; then
    echo "ERROR: main.py not found"
    echo "Please make sure you're running this from the application directory"
    exit 1
fi

# Check if pip is available
if ! command -v pip3 &> /dev/null; then
    echo "ERROR: pip3 is not installed"
    echo "Please install pip3 using your package manager"
    exit 1
fi

# Check if requirements are installed
echo "Checking dependencies..."
if ! python3 -c "import requests, yaml" &> /dev/null; then
    echo "Installing dependencies..."
    pip3 install -r requirements.txt
    if [ $? -ne 0 ]; then
        echo "ERROR: Failed to install dependencies"
        echo "You may need to run: sudo pip3 install -r requirements.txt"
        exit 1
    fi
fi

# Create directories if they don't exist
mkdir -p Projects
mkdir -p config

# Check if configuration exists
if [ ! -f "config/llm_config.yaml" ]; then
    if [ -f "config/llm_config.yaml.example" ]; then
        echo "Creating default configuration..."
        cp "config/llm_config.yaml.example" "config/llm_config.yaml"
        echo
        echo "IMPORTANT: Please edit config/llm_config.yaml with your API keys"
        echo "before using the application."
        echo
    else
        echo "WARNING: No configuration template found"
        echo "You may need to create config/llm_config.yaml manually"
    fi
fi

# Start the application
echo "Starting application..."
echo
python3 main.py

# Handle exit
exit_code=$?
if [ $exit_code -ne 0 ]; then
    echo
    echo "Application exited with an error (code: $exit_code)."
    echo "Check the error messages above for details."
else
    echo
    echo "Application closed normally."
fi

echo
read -p "Press Enter to exit..."