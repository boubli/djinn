#!/bin/bash
# DJINN - AI CLI Installer

echo "🔮 Installing DJINN..."

# Check for Python
if ! command -v python3 &> /dev/null; then
    if ! command -v python &> /dev/null; then
        echo "❌ Python is not installed. Please install Python 3.8+ first."
        exit 1
    else
        PYTHON_CMD=python
    fi
else
    PYTHON_CMD=python3
fi

# Check for Pip
if ! command -v pip &> /dev/null && ! command -v pip3 &> /dev/null; then
    echo "❌ Pip is not found. Please ensure pip is installed."
    exit 1
fi

# Install/Update DJINN
echo "📦 Installing/Updating djinn-cli via pip..."
$PYTHON_CMD -m pip install --upgrade djinn-cli

if [ $? -eq 0 ]; then
    echo "✅ DJINN installed successfully!"
    echo "🚀 Run 'djinn config' to get started."
else
    echo "❌ Installation failed."
    exit 1
fi
