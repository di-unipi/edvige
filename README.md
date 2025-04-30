# Edvige 🦉

Edvige is the codename
for the communication team
of the [Department of Computer Science](https://di.unipi.it)
at the University of Pisa.
In this repository,
you will find the code
to serve our public calendar,
which we currently screencast
near the coffee machines. ☕

Assuming that you already installed
`npm` for
[NodeJS](https://nodejs.org/en/)
and `pip3` for
[Python](https://www.python.org/),
you can install the required dependencies
as follows.

```bash
npm ci
```

yep, that easy.

Then, we keep track of the Department events
via a Google Calendar.
The following command automatically downloads
the calendar as an ICS file and generates
a static website in `www` to visualize
upcoming events.

```bash
npm run calendar
```

## Workflow

This repository is downloaded on a Raspberry Pi 2
that renders and serves the web page.
Due to the limited computational power of the device,
we render the page offline
and just visualize it
in the browser.
Every five minutes,
a cronjob
runs the `npm run calendar` command
that

1. Downloads the `ics` file from Google Calendar
2. Renders the webpage and its dependecies in the `www` folder


Cronjob

```
*/5 9-18 * * 1-5 cd /home/pi/edvige && bash scripts/calendar.sh && bash scripts/refresh_firefox.sh
30 18 * * 1-5 cd /home/pi/edvige/ && bash scripts/refresh_pixels.sh
30 8  * * 1-5 export DISPLAY=":0.0"; xrandr --output HDMI-1 --auto
40 18 * * 1-5 export DISPLAY=":0.0"; xrandr --output HDMI-1 --off
```

## Docker / Podman

```bash
podman build -t edvige .
podman run -p 8080:8080 edvige
```
