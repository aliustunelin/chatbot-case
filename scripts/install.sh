#!/bin/bash

# Docker environment için basitleştirilmiş kurulum scripti

echo "Installing dependencies for Docker environment..."

# Check if uv is installed
if ! command -v uv &> /dev/null; then
    echo "uv is not installed. Installing it now..."
    pip install uv
else
    echo "uv is already installed. Proceeding..."
fi

# Check if virtual environment exists
if [ -d ".venv" ]; then
    echo "Virtual environment already exists. Activating it..."
    source .venv/bin/activate
else
    echo "Creating a new virtual environment with Python 3.11..."
    # Python 3.11 ile virtual environment oluştur
    if command -v python3.11 &> /dev/null; then
        uv venv --python=python3.11
    elif command -v python3 &> /dev/null && python3 --version | grep -q "3.11"; then
        uv venv --python=python3
    else
        echo "Python 3.11 not found. Please install Python 3.11 first."
        echo "You can use 'make old-install' which will install Python 3.11 via pyenv."
        exit 1
    fi
    source .venv/bin/activate
fi

# Install requirements
echo "Installing requirements with uv..."
uv pip install -r requirements.txt 

echo "Installation completed successfully!" 