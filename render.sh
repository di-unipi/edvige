#! /bin/env bash
python html_generator.py "$1" > index.mjml
mjml index.mjml > index.html
