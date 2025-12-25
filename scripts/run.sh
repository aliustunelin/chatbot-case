#!/bin/bash

# Docker environment için basitleştirilmiş run scripti

echo "Starting application in Docker environment..."

# Activate virtual environment
if [ -d ".venv" ]; then
    echo "Activating virtual environment..."
    source .venv/bin/activate
    echo "Using Python $(python --version)"
else
    echo "Virtual environment not found. Make sure to run 'make install' first."
    exit 1
fi

# Run the Python application
echo "Running application..."
python app.py 