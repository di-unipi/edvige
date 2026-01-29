#!/bin/bash

# Script to turn off monitor display when called by crontab
export WAYLAND_DISPLAY=wayland-0
export XDG_RUNTIME_DIR=/run/user/1000

# check argument off / on
if [ "$1" == "off" ]; then
    /usr/bin/wlr-randr --output HDMI-A-1 --off
    exit 0
elif [ "$1" == "on" ]; then
    /usr/bin/wlr-randr --output HDMI-A-1 --on \
        --mode "1920x1080, 60.000000"
else
    echo "Usage: $0 {off|on}"
    exit 1
fi
