#! /bin/bash
set -e

# Log
mkdir -p logs/
echo "Start $(date)" >> logs/calendar.log

# Update Calendar Visualization
python3 scripts/downloader.py basic.ics >> logs/calendar.log

# Render the pug files
python3 scripts/render.py basic.ics >> logs/calendar.log

# Check if static/assets/locandina.png exists
if [ -f static/assets/locandina.png ]; then
    node_modules/.bin/pug --doctype html --pretty layout/index_locandina.pug --out .
    mv index_locandina.html index.html
else
    node_modules/.bin/pug --doctype html --pretty layout/index.pug --out .
fi

# Remove temporary pug files
rm -f layout/footer.pug
rm -f layout/events.pug
rm -f basic.ics

# Move to folder
mkdir -p www
cp -r static/* www/
mv index.html www/index.html

echo "End $(date)" >> logs/calendar.log
