#! /bin/bash
set -e 

# Log
mkdir -p logs/
echo "Start $(date)" >> logs/calendar.log

# Update Calendar Visualization
python3 scripts/downloader.py basic.ics >> logs/calendar.log

# Render the pug files
python3 scripts/render.py basic.ics >> logs/calendar.log

# Pug rendering
node_modules/.bin/pug --doctype html --pretty layout/index.pug --out .

# Remove temporary pug files
rm -f layout/footer.pug
rm -f layout/next.pug
rm -f layout/upcoming.pug
rm -f basic.ics

# Move to folder
rm -r www/
cp -r static www/
mv index.html www/index.html

echo "End $(date)" >> logs/calendar.log
