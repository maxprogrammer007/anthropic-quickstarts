#!/bin/bash

# Export the display variable so all subsequent commands can use it
export DISPLAY=:1

echo "Starting Xvfb (Virtual Screen)..."
# Start Xvfb on display :1 with a resolution of 1024x768 and 24-bit color
# The & runs it in the background
Xvfb $DISPLAY -screen 0 1024x768x24 &

# Wait for Xvfb to be ready by repeatedly trying to connect to it.
# xdpyinfo is a utility that gets information about an X server.
echo "Waiting for Xvfb to be ready..."
while ! xdpyinfo -display $DISPLAY > /dev/null 2>&1; do
    sleep 0.5
done
echo "Xvfb is ready."

# Now that the screen is ready, start all other services in the background
echo "Starting Window Manager, VNC, and other services..."
./mutter_startup.sh &
./tint2_startup.sh &
./x11vnc_startup.sh &
./novnc_startup.sh &

echo "All services started. Application is ready."

# Keep the script running to keep the container alive
tail -f /dev/null