#! /bin/bash
# Script to refresh Firefox, if it is running.

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
xdotool key F5