#! /bin/bash
set -e

# Log stdout and stderr, rotating the log when it exceeds 1 MB
mkdir -p logs/
LOG=logs/calendar.log
if [ -f "$LOG" ] && [ "$(stat -c %s "$LOG")" -gt 1048576 ]; then
    mv -f "$LOG" "$LOG.1"
fi
exec >> "$LOG" 2>&1
echo "Start $(date)"

# Check that the image was built from the deployed dependencies
if [ -f requirements.deployed.txt ] && ! cmp -s requirements.txt requirements.deployed.txt; then
    echo "Error: the image is outdated, rebuild it with: podman build -t edvige ."
    exit 1
fi

# Update Calendar Visualization
python3 scripts/downloader.py basic.ics

# Copy static files, then render the page
mkdir -p www
cp -r static/* www/
python3 scripts/render.py basic.ics --output www/index.html

# Remove temporary files
rm -f basic.ics

echo "End $(date)"
