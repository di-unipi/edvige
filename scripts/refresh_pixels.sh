#! /bin/bash
# Script to refresh pixels from firefox.

# Set display for xdotool
export DISPLAY=":0.0"

# Logging function to file ([YYYY-MM-DD HH:MM:SS] $1)
function log {
  echo "[$(date +"%Y-%m-%d %H:%M:%S")] $1" >> refresh_pixels.log
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
xdotool key ctrl+t
log "Opened new tab"
sleep 1
xdotool type "file:///home/pi/edvige/www/random/index.html"
log "Typed URL"
sleep 2
xdotool key KP_Enter
log "Typed Enter"
sleep 300
xdotool key ctrl+w
log "Refreshed Pixels and Closed Tab"
