#!/bin/bash
set -e

# Start virtual display
export DISPLAY=:99
Xvfb :99 -screen 0 1920x1080x24 &
sleep 1

# Start window manager
fluxbox &
sleep 1

# Start VNC server
x11vnc -display :99 -nopw -forever -shared -rfbport 5900 &
sleep 1

# Start noVNC web client (access via http://localhost:6080)
websockify --web /usr/share/novnc/ 6080 localhost:5900 &
sleep 1

echo "============================================="
echo "  Web UI:  http://localhost:8000"
echo "  noVNC:   http://localhost:6080"
echo "============================================="

# If "web" is passed as first arg (or no args), start the web UI
if [ "$1" = "web" ] || [ $# -eq 0 ]; then
    exec python -m uvicorn web:app --host 0.0.0.0 --port 8000
else
    # Otherwise run main.py with CLI args
    exec python main.py "$@"
fi
