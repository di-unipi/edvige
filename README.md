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

## Workflow

This repository is downloaded on a Raspberry Pi 3B that renders and serves the web page. Every five minutes, a cronjob runs the `calendar_podman.sh`. We do **not** handle automatic refreshing of the website, which should be done by an extension/plugin of your choice in the browser.

Other scripts used by the cronjob are:
- `monitor.sh` to turn on and off the TV screen at specific times, and
- `refresh_pixels.sh` to refresh the screen pixels to avoid burn-in effects.

```
# m h  dom mon dow   command
*/5 9-18 * * 1-5 cd /home/pi/edvige && bash scripts/calendar_podman.sh
30 18 * * 1-5 cd /home/pi/edvige && bash scripts/refresh_pixels.sh
30 8  * * 1-5 cd /home/pi/edvige && bash scripts/monitor.sh on
40 18 * * 1-5 cd /home/pi/edvige && bash scripts/monitor.sh off
```

## Local Development

To develop locally, you can edit this repository and test the changes by running the `calendar_podman.sh` script as described above. You can then serve the `www` folder using a simple HTTP server, for example:

```bash
cd www
python3 -m http.server 8000
```

The `deploy.sh` script can be used to deploy the changes to the Raspberry Pi via `rsync`.

```bash
bash scripts/deploy.sh
```
