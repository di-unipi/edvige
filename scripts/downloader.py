"""
Download the calendar basic.ics
"""

import os
import sys

import requests

URL = 'https://calendar.google.com/calendar/ical/' \
      'c_31hk6lrp2plgq36e1heodpbca0%40group.calendar.google.com/' \
      'public/basic.ics'

# Seconds to wait for the connection and for each read
TIMEOUT = 30


def download(url: str, fname: str):
    """Downloads the calendar, failing on errors instead of saving them."""
    response = requests.get(url, timeout=TIMEOUT)
    response.raise_for_status()

    # Refuse error or captive portal pages served with a 200 status
    if not response.content.lstrip().startswith(b'BEGIN:VCALENDAR'):
        raise ValueError(f'Downloaded file is not a calendar: {response.content[:80]!r}')

    # Write via a temporary file, so a failure never leaves a partial calendar
    tmp_fname = f'{fname}.tmp'
    with open(tmp_fname, mode='wb') as localfile:
        localfile.write(response.content)
    os.replace(tmp_fname, fname)


if __name__ == '__main__':
    download(URL, sys.argv[1])
