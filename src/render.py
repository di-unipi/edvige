from csv import DictReader
from datetime import datetime as dt

# Layout for the next talks
raw = """
.row.project
  .col-2
    h3.mb-0 %%%DAY%%%
    h5.month.mb-0 %%%MONTH%%%
    p %%%HOUR%%%
  .col-10
    p.author #[span.me %%%AUTHOR%%%]
    h4.title.mb-1
      | %%%TITLE%%%
    p.address %%%LUOGO%%%"""

# Layout for the upcoming talk
raw_upcoming = """
.row.next
  .col-9
    p.author #[span.me %%%AUTHOR%%%]
    h2.title.mb-0.mt-1
      | %%%TITLE%%%
    p.address %%%LUOGO%%%
  .col-2
    h1.day %%%DAY%%%
    h4.month.mb-0 %%%MONTH%%%
    p %%%HOUR%%%
  .col-11
      p
        | %%%ABSTRACT%%%
      """

# Footer
raw_footer = """
.col-6
    p Last update: %%%DATE%%% at %%%HOUR%%%
.col-6.text-end
    p Made with ❤️ by 🦉
"""


def render_talk(talk: dict, upcoming: bool = False):
    """
    The talk dictionary should contain
    the following keys:
    - Titolo
    - Autore
    - Data (in format %d/%m/%Y)
    - Ora
    - Abstract (optional)
    """
    if upcoming:
        template = raw_upcoming
    else:
        template = raw

    # Parse date
    date = dt.strptime(talk['Data'], '%d/%m/%Y')

    # Get month name
    month = date.strftime('%B')

    # Get cardinal day without leading zero
    day = str(int(date.strftime('%d')))

    # Add suffix to day
    day += suffix(int(day))

    # Build the output
    output = template.replace('%%%DAY%%%', day)
    output = output.replace('%%%MONTH%%%', month)
    output = output.replace('%%%HOUR%%%', talk['Ora'])
    output = output.replace('%%%LUOGO%%%', talk['Luogo'])
    output = output.replace('%%%AUTHOR%%%', talk['Autore'])
    output = output.replace('%%%TITLE%%%', talk['Titolo'])

    # Eventually add abstract
    if talk['Abstract'] and upcoming:
        lines = talk['Abstract'].split('\n')
        abstract = '#[br] \n        |'.join(lines)
        # import sys
        # print(abstract, file=sys.stderr)
        # sys.exit(1)
        output = output.replace('%%%ABSTRACT%%%', abstract)
    else:
        output = output.replace('%%%ABSTRACT%%%', 'No abstract available')

    return output


def suffix(d: int):
    """
    Returns the correct suffix for
    a given day of the month.
    """
    return 'th' if 11 <= d <= 13 \
           else {1: 'st', 2: 'nd', 3: 'rd'}.get(d % 10, 'th')


if __name__ == '__main__':
    import argparse

    # Parse arguments
    parser = argparse.ArgumentParser(description='Render talks')
    parser.add_argument('-n', '--number', type=int, default=4,
                        help='Number of talks to render')
    parser.add_argument('-d', '--date', type=str,
                        help='Render page for a specific date '
                             '(format: DD/MM/YYYY)')
    parser.add_argument('csv_filename', type=str,
                        help='CSV file containing talks')
    args = parser.parse_args()

    # Parse CSV file into a dictionary
    with open(args.csv_filename, 'r') as fp:
        csv_reader = DictReader(fp)
        talks = list(csv_reader)

    # Get current datetime
    if not args.date:
        now = dt.now()
    else:
        now = dt.strptime(args.date, '%d/%m/%Y')

    # Sort by time
    talks.sort(key=lambda t: dt.strptime(t['Ora'], '%H:%M'))
    # Sort by date
    talks.sort(key=lambda t: dt.strptime(t['Data'], '%d/%m/%Y'))
    # Put together date and time
    for t in talks:
        date = dt.strptime(t['Data'], '%d/%m/%Y')
        time = dt.strptime(t['Ora'], '%H:%M')
        t['datetime'] = dt(date.year, date.month, date.day,
                           time.hour, time.minute)
        if t['datetime'] > now:
            print(f'Ok {t["Titolo"]} {t["datetime"]} {now}')

    # Filter talks
    talks = [talk for talk in talks if talk['Titolo']]
    future = [talk for talk in talks if talk['datetime'] > now]

    # Assign upcoming
    upcoming, future = future[0], future[1:]

    # Render upcoming
    with open('layout/upcoming.pug', 'w') as f:
        f.write('.row.mt-4.mb-2\n')
        f.write('  h1 #[span.emoji 🚀] Upcoming\n')
        f.write(render_talk(upcoming, True))

    # Render future talks
    with open('layout/next.pug', 'w') as f:
        if future:
            f.write('.row.mt-4.mb-4\n')
            f.write('  h1 #[span.emoji 🔮] Next Events\n')
            # Write the next n talks
            for talk in future[:args.number]:
                f.write(render_talk(talk))
        else:
            f.write('')

    # Render footer with date and hour
    with open('layout/footer.pug', 'w') as f:
        footer = raw_footer.replace('%%%DATE%%%', now.strftime('%d/%m/%Y'))
        footer = footer.replace('%%%HOUR%%%', now.strftime('%H:%M'))
        f.write(footer)
