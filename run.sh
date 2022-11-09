#! /bin/bash

python3 src/downloader.py >> log &&
python3 src/render.py basic.ics >> log &&
pug --doctype html --pretty layout/index.pug --out . &&
mv index.html www/index.html &&
date >> log
