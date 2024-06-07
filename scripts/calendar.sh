#! /bin/bash
set -e 

# Log
echo "Start $(date)" >> calendar.log

# Update Calendar Visualization
python3 scripts/downloader.py basic.ics >> calendar.log

# Render the pug files
python3 scripts/render.py basic.ics >> calendar.log

# Pug rendering
node_modules/.bin/pug --doctype html --pretty layout/index.pug --out .

# Remove temporary pug files
rm -f layout/footer.pug
rm -f layout/next.pug
rm -f layout/upcoming.pug
rm -f basic.ics

# Move to folder
cp -r static www/
mv index.html www/index.html

echo "End $(date)" >> calendar.log
