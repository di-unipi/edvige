# Edvige 🦉

Edvige is the codename for the communication team of the [Department of Computer Science](https://di.unipi.it) at the University of Pisa. In this repository, you will find the code to serve our public calendar, which we currently screencast near the coffee machines. ☕

We keep track of the Department events via a Google Calendar and render it as a static website on a Raspberry Pi running Raspbian.

## Rendering

The `calendar_podman.sh` script uses [Podman](https://podman.io/) to run a container that renders the website. To use it, first install Podman and build the image described in Containerfile.

```bash
sudo apt update && sudo apt install -y podman
podman build -t edvige .
```

Then, you can run the script to populate the `www` folder with the rendered website.

```bash
bash scripts/calendar_podman.sh
```

The page is rendered by `scripts/render.py` from the [Jinja2](https://jinja.palletsprojects.com/) template `layout/index.html.j2`, with HTML autoescaping enabled. Recurring events are expanded with [recurring-ical-events](https://pypi.org/project/recurring-ical-events/), and cancelled events are skipped. The poster column is shown when `static/assets/locandina.png` exists. Bootstrap and the IBM Plex Sans and Mono fonts (SIL Open Font License) are served from `static/vendor/`, so the screen does not depend on a CDN.

Both stdout and stderr of each run are logged in `logs/calendar.log`, which is rotated to `logs/calendar.log.1` when it exceeds 1 MB. A run is skipped if the previous one is still in progress. When the page has not been updated for more than 15 minutes, its footer shows an "Outdated!" warning: check the log.

The container installs the pinned dependencies listed in `requirements.txt`. After changing the dependencies in `pyproject.toml`, update the lock file and regenerate it with [uv](https://docs.astral.sh/uv/), then rebuild the image:

```bash
uv lock
uv export --format requirements-txt --no-dev --no-emit-project -o requirements.txt
```

If the image was built from a different `requirements.txt` than the deployed one, each run fails and logs `Error: the image is outdated`, until the image is rebuilt.

## Workflow

This repository is downloaded on a Raspberry Pi 3B that renders and serves the web page. Every five minutes, a cronjob runs the `calendar_podman.sh`. The page automatically refreshes every 60 seconds via the `autorefresh.js` script.

Other scripts used by the cronjob are:
- `monitor.sh` to turn on and off the TV screen at specific times, and
- `refresh_pixels.sh` to refresh the screen pixels to avoid burn-in effects.

Install the crontab as the user that owns the repository, cloned in `~/edvige`; cron sets `$HOME` to that user's home directory. Cron discards the output of the jobs when no mail server is installed, so a job that fails before `calendar.sh` starts leaves no trace in `logs/calendar.log`: run the command by hand, or check `journalctl -t CRON`.

```
# m h  dom mon dow   command
*/5 8-17 * * 1-5 cd "$HOME"/edvige && bash scripts/calendar_podman.sh
0-25/5 18 * * 1-5 cd "$HOME"/edvige && bash scripts/calendar_podman.sh
30 18 * * 1-5 cd "$HOME"/edvige && bash scripts/refresh_pixels.sh
30 8  * * 1-5 cd "$HOME"/edvige && bash scripts/monitor.sh on
40 18 * * 1-5 cd "$HOME"/edvige && bash scripts/monitor.sh off
```

The calendar is rendered from 8:00, so the page is up to date when the screen turns on at 8:30. It is not rendered after 18:25, so the pixel refresh started at 18:30 runs until the screen turns off. The next morning, the first render restores the calendar.

## Local Development

To develop locally, you can edit this repository and test the changes by running the `calendar_podman.sh` script as described above. You can also render the events in `data/debug.ics` without downloading the calendar, with `bash scripts/calendar_debug.sh`. You can then serve the `www` folder using a simple HTTP server, for example:

```bash
cd www
python3 -m http.server 8000
```

The tests run from the repository root, with the dependencies installed (e.g. `uv sync`):

```bash
uv run python -m unittest discover -s tests
```

The `deploy.sh` script can be used to deploy the changes to the Raspberry Pi via `rsync`. Then, rebuild the image on the Raspberry Pi:

```bash
bash deploy.sh
ssh edvige 'cd edvige && podman build -t edvige .'
```
