#!/bin/bash

# Exit on error
set -e

echo "Installing acitoolkit and dependencies..."

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "Python 3 is required but not installed. Please install Python 3 first."
    exit 1
fi

# Install system dependencies
if command -v apt-get &> /dev/null; then
    # For Ubuntu/Debian
    echo "Installing system dependencies..."
    sudo apt-get update
    sudo apt-get install -y python3-venv graphviz
elif command -v yum &> /dev/null; then
    # For RHEL/CentOS
    echo "Installing system dependencies..."
    sudo yum install -y python3-venv graphviz
elif command -v brew &> /dev/null; then
    # For macOS
    echo "Installing system dependencies..."
    brew install graphviz
else
    echo "Warning: Could not install system dependencies automatically."
    echo "Please ensure graphviz is installed on your system."
fi

# Create and activate virtual environment
echo "Creating Python virtual environment..."
python3 -m venv venv
source venv/bin/activate

# Upgrade pip
echo "Upgrading pip..."
pip install --upgrade pip

# Install Python dependencies
echo "Installing Python dependencies..."
pip install -r requirements.txt

# Install the package in development mode
echo "Installing acitoolkit in development mode..."
pip install -e .

echo "Installation complete!"
echo "To activate the virtual environment, run: source venv/bin/activate" 