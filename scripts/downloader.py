"""
Download the calendar basic.ics
"""

import requests
import sys

URL = 'https://calendar.google.com/calendar/ical/' \
      'c_31hk6lrp2plgq36e1heodpbca0%40group.calendar.google.com/' \
      'public/basic.ics'


if __name__ == '__main__':
    fname = sys.argv[1]
    response = requests.get(URL)
    with open(fname, mode='wb') as localfile:
        localfile.write(response.content)
