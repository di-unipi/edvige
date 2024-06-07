#! /bin/bash
# Script to refresh Firefox, if it is running.

# Set display for xdotool
export DISPLAY=":0.0"

# Logging function to file ([YYYY-MM-DD HH:MM:SS] $1)
function log {
  echo "[$(date +"%Y-%m-%d %H:%M:%S")] $1" >> logs/refresh_firefox.log
}

# Get the window ID
WID=$(xdotool search --name "Mozilla Firefox" | head -1)

# Check that WID is a number
if ! [[ $WID =~ ^[0-9]+$ ]]; then
  log "Firefox not running"
  exit 1
fi

# Refresh Firefox
log "Firefox has WID $WID"
xdotool windowactivate "$WID"
xdotool key F5
log "Refreshed Firefox"
