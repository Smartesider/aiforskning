#!/bin/bash
# Startup script for AI Ethics Testing Framework
# Configured for Docker/Portainer deployment at 172.17.0.8:8020

set -e

echo "🚀 Starting AI Ethics Testing Framework"
echo "📍 Target IP: 172.17.0.8"
echo "📍 Port mapping: 8020:80 (host:container)"
echo "🔧 Current directory: $(pwd)"

# Check if we're in a container
if [ -f /.dockerenv ]; then
    echo "🐳 Running in Docker container"
    BIND_ADDRESS="0.0.0.0:80"
else
    echo "💻 Running on host system"
    # Try port 8020 first, fall back to 8022 if occupied
    if python3 -c "import socket; s=socket.socket(); s.bind(('0.0.0.0', 8020)); s.close()" 2>/dev/null; then
        BIND_ADDRESS="0.0.0.0:8020"
        echo "🎯 Port 8020 available - will replace static site"
    else
        BIND_ADDRESS="0.0.0.0:8022"
        echo "⚠️  Port 8020 occupied - using 8022 (needs proxy setup)"
    fi
fi

echo "🔗 Binding to: $BIND_ADDRESS"

# Check Python availability
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3 not found"
    exit 1
fi

echo "✅ Python3 found: $(python3 --version)"

# Try to install dependencies if pip is available
if command -v pip3 &> /dev/null; then
    echo "📦 Installing dependencies..."
    pip3 install -r requirements.txt --user --quiet
elif python3 -m pip --version &> /dev/null; then
    echo "📦 Installing dependencies with python3 -m pip..."
    python3 -m pip install -r requirements.txt --user --quiet
else
    echo "⚠️  pip not available, trying to run with existing packages..."
fi

# Check if gunicorn is available
if command -v gunicorn &> /dev/null || python3 -c "import gunicorn" 2>/dev/null; then
    echo "🔥 Starting with Gunicorn..."
    if command -v gunicorn &> /dev/null; then
        gunicorn --bind $BIND_ADDRESS --workers 4 --timeout 120 --config gunicorn.conf.py run_app:app
    else
        python3 -m gunicorn --bind $BIND_ADDRESS --workers 4 --timeout 120 --config gunicorn.conf.py run_app:app
    fi
else
    echo "📡 Starting with Flask development server..."
    export HOST=${BIND_ADDRESS%:*}
    export PORT=${BIND_ADDRESS#*:}
    python3 run_app.py
fi
