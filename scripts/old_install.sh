#!/bin/bash

# Pyenv path ayarları
export PYENV_ROOT="$HOME/.pyenv"
export PATH="$PYENV_ROOT/bin:$PATH"

# Check if pyenv is installed
if ! command -v pyenv &> /dev/null; then
    echo "pyenv is not installed. Installing it now..."
    if [[ "$OSTYPE" == "darwin"* ]]; then
        echo "Detected macOS. Installing pyenv using Homebrew..."
        brew install pyenv
        echo 'export PYENV_ROOT="$HOME/.pyenv"' >> ~/.zshrc
        echo 'command -v pyenv >/dev/null || export PATH="$PYENV_ROOT/bin:$PATH"' >> ~/.zshrc
        echo 'eval "$(pyenv init -)"' >> ~/.zshrc
        source ~/.zshrc
    elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
        echo "Detected Linux. Installing pyenv..."
        # Eski pyenv dizinini sil
        if [ -d "$PYENV_ROOT" ]; then
            echo "Removing existing .pyenv directory..."
            rm -rf "$PYENV_ROOT"
        fi
        curl https://pyenv.run | bash
        echo 'export PYENV_ROOT="$HOME/.pyenv"' >> ~/.bashrc
        echo 'command -v pyenv >/dev/null || export PATH="$PYENV_ROOT/bin:$PATH"' >> ~/.bashrc
        echo 'eval "$(pyenv init -)"' >> ~/.bashrc
        # Path'i hemen yükle
        export PATH="$PYENV_ROOT/bin:$PATH"
        eval "$(pyenv init -)"
    else
        echo "Unsupported OS. Please install pyenv manually."
        exit 1
    fi
else
    echo "pyenv is already installed. Proceeding..."
    # pyenv'i başlat
    eval "$(pyenv init -)"
fi

# Install Python 3.11 with pyenv if not already installed
if ! pyenv versions | grep -q "3.11"; then
    echo "Installing Python 3.11 via pyenv..."
    pyenv install 3.11
    echo "Setting Python 3.11 as the local version for this project..."
    pyenv local 3.11
else
    echo "Python 3.11 is already installed. Setting as local version..."
    pyenv local 3.11
fi

# Check if uv is installed
if ! command -v uv &> /dev/null; then
    echo "uv is not installed. Installing it now..."
    if [[ "$OSTYPE" == "darwin"* ]]; then
        echo "Detected macOS. Installing uv using Homebrew..."
        brew install uv
    elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
        echo "Detected Linux. Installing uv using pip..."
        # Önce pip'i güncelle
        python -m pip install --upgrade pip
        # uv'yi pip ile yükle
        pip install uv
    else
        echo "Unsupported OS. Please install uv manually."
        exit 1
    fi
else
    echo "uv is already installed. Proceeding..."
fi

# Check if virtual environment exists
if [ -d ".venv" ]; then
    echo "Virtual environment already exists. Activating it..."
    source .venv/bin/activate
else
    echo "Creating a new virtual environment with Python 3.11..."
    uv venv --python=python3.11
    source .venv/bin/activate
fi

# Install requirements
echo "Installing requirements with uv..."
uv pip install -r requirements.txt

echo "Installation completed successfully!"