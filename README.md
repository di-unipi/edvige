# Edvige 🦉

After creating the body of an email in the `archive` folder as `month_year.md`, just:

```bash
make
```

yep, that easy.

# 🤖 0xFEED

Code for the live presentation of the next events
from the 0xFEED communications team.

The tool works in two steps:

1. Firstly, the script `downloader.py` downloads alle the events from a Google Spreadsheet, using the module [`gspread`](https://github.com/burnash/gspread), and writes them to the `events.csv` file.

    *N.B.* To properly work, the script needs to be run with a file named `credentials.json` in the same directory. To know how to create this file, please refer to the [`gspread` documentation](https://docs.gspread.org/en/latest/oauth2.html).

2. Secondly, the script `render.py` reads the `events.csv` file
and updates the templates `upcoming.pug` and `next.pug`. The
former contains the first upcoming event, the latter all the
following events.

Consequently, the static HTML page `index.html` is generated
via the command:
```bash
pug --doctype html --pretty src/index.pug --out .
```

The procedure is automated in the `run.sh` bash script, which also logs the described steps.

## ⏱ CRONJOB

The `cronjob.txt` file contains commands to schedule some operations:

```bash
# Execute 'run.sh' script every hour
0 * * * * cd /home/pi/0xfeed && ./run.sh

# "Turn on" the display linked to the raspberry, at 8am on every day-of-week from Monday through Friday.
0 8  * * 1-5 vcgencmd display_power 1

# "Turn off" the display linked to the raspberry, at 7pm on every day-of-week from Monday through Friday.
0 19 * * 1-5 vcgencmd display_power 0
```
