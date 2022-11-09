"""
Download the calendar basic.ics
"""

import requests

URL = 'https://calendar.google.com/calendar/ical/' \
      'c_31hk6lrp2plgq36e1heodpbca0%40group.calendar.google.com/' \
      'public/basic.ics'
FNAME = 'basic.ics'


if __name__ == '__main__':
    response = requests.get(URL)
    with open(FNAME, mode='wb') as localfile:
        localfile.write(response.content)
