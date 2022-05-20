#! /bin/bash

python3 downloader.py >> log &&
python3 render.py events.csv >> log &&
pug --doctype html --pretty src/index.pug --out . &&
date >> log
