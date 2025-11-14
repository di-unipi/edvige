#! /bin/bash
# Script to refresh pixels from firefox.

# Set display for xdotool
export DISPLAY=":0.0"

# Get the window ID
WID=$(xdotool search --name "Mozilla Firefox" | head -1)

# Check that WID is a number
if ! [[ $WID =~ ^[0-9]+$ ]]; then
  exit 1
fi

# Refresh Firefox
xdotool windowactivate "$WID"
xdotool key ctrl+t
sleep 1
xdotool type "file:///home/pi/edvige/www/random/index.html"
sleep 2
xdotool key KP_Enter
sleep 300
xdotool key ctrl+w
