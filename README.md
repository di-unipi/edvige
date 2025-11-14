# Edvige 🦉

Edvige is the codename for the communication team of the [Department of Computer Science](https://di.unipi.it) at the University of Pisa.

This repository contains the code powering  our public event calendar, 
which is displayed near the coffee machines ☕️ and used internally for departmental communication.

The current version of Edvige is built with:

- **Jekyll** (static site generator)  
- **Python** (ICS → YAML event extraction)  
- **rsync / Makefile** for deployment automation  

The result is a fully static website served by our Raspberry Pi.

---

## 🚀 **Setup**

Before starting, ensure you have:

- **Ruby** + **Bundler** + **Jekyll** installed  
- **Python 3** with `pip`  
- (optional) `rsync` for local deployment  

Install Ruby & Python dependencies:

```bash
make setup
```

---

## 🔧 **Local Development**

Start a live-reloading development server:

```bash
make serve
```

---

## 🏗 **Build Pipeline**

```bash
make render
```

This command:

1. Downloads the ICS  
2. Converts it to `_data/events.yml`  
3. Builds the Jekyll site
4. Cleans temporary files

---

# 🌀 **Raspberry Pi Workflow**

Cronjob:

```
*/5 9-18 * * 1-5 cd /home/pi/edvige && make build && bash scripts/refresh_firefox.sh
30 18 * * 1-5 cd /home/pi/edvige/ && bash scripts/refresh_pixels.sh
30 8  * * 1-5 export DISPLAY=":0.0"; xrandr --output HDMI-1 --auto
40 18 * * 1-5 export DISPLAY=":0.0"; xrandr --output HDMI-1 --off
```

---

# ❤️ Credits

Made with care by the [Communication Team 🦉](mailto:comunicazione@di.unipi.it) 
of the Department of Computer Science, University of Pisa.
