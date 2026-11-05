#! /bin/bash
set -e

# Log
mkdir -p logs/
echo "Start $(date)" >> logs/calendar.log

# Update Calendar Visualization
python3 scripts/downloader.py basic.ics >> logs/calendar.log

# Copy static files, then render the page
mkdir -p www
cp -r static/* www/
python3 scripts/render.py basic.ics --output www/index.html >> logs/calendar.log

# Remove temporary files
rm -f basic.ics

echo "End $(date)" >> logs/calendar.log
