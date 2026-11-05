#! /bin/bash
set -e

# Log
mkdir -p logs/
echo "Start $(date)" >> logs/calendar.log

# Copy static files, then render the page
mkdir -p www
cp -r static/* www/
python3 scripts/render.py data/debug.ics --output www/index.html >> logs/calendar.log

echo "End $(date)" >> logs/calendar.log
