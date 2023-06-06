from datetime import datetime as dt
from icalendar import Calendar
from bs4 import BeautifulSoup

# Layout for the next talks
raw = """
.row.project
  .col-2
    h3.mb-0 %%%DAY%%%
    h5.month.mb-0 %%%MONTH%%%
    p.small %%%HOUR%%%-%%%END%%%
  .col-10
    h4.title.mb-1
      | %%%TITLE%%%
    p.address %%%LUOGO%%%"""

# Layout for the upcoming talk
raw_upcoming = """
.row.next
  .col-9
    h2.title.mb-0.mt-1
      | %%%TITLE%%%
    p.address %%%LUOGO%%%
  .col-2
    h1.day %%%DAY%%%
    h4.month.mb-0 %%%MONTH%%%
    p %%%HOUR%%%-%%%END%%%
  .col-11
      p
        | %%%ABSTRACT%%%"""

# Layout for the next talks
raw_second = """
.row.project
  .col-2
    h3.mb-0 %%%DAY%%%
    h5.month.mb-0 %%%MONTH%%%
    p.small %%%HOUR%%%-%%%END%%%
  .col-10
    h4.title.mb-1
      | %%%TITLE%%%
    p.address.mb-1 %%%LUOGO%%%
    p.shortabs
      | %%%ABSTRACT%%%"""


# Footer
raw_footer = """
.col-6
    p Last update: %%%DATE%%% at %%%HOUR%%%
.col-6.text-end
    p Made with ❤️ by 🦉
"""


def render_talk(talk: dict, upcoming: bool = False, second: bool = False):
    """
    The talk dictionary should contain
    the following keys:
    - Titolo
    - Inizio
    - Fine
    - Abstract (optional)
    """
    if upcoming:
        template = raw_upcoming
    elif second:
        template = raw_second
    else:
        template = raw

    # Get month name
    month = talk['Inizio'].strftime('%B')

    # Get cardinal day without leading zero
    day = str(int(talk['Inizio'].strftime('%d')))

    # Add suffix to day
    day += suffix(int(day))

    # Build the output
    output = template.replace('%%%DAY%%%', day)
    output = output.replace('%%%MONTH%%%', month)
    output = output.replace('%%%HOUR%%%', dt.strftime(talk['Inizio'], '%H:%M'))
    output = output.replace('%%%END%%%', dt.strftime(talk['Fine'], '%H:%M'))
    if talk['Luogo'] is not None:
        output = output.replace('%%%LUOGO%%%', talk['Luogo'])
    else:
        output = output.replace('%%%LUOGO%%%', 'Not Available')
    output = output.replace('%%%TITLE%%%', talk['Titolo'])

    # Eventually add abstract
    if talk['Abstract'] and (upcoming or second):
        # Retrieve abstract
        abstract = talk['Abstract']
        # Shorten abstract
        if second:
            # Load abstract
            soup = BeautifulSoup(abstract,
                                 features='lxml')
            # Get text
            abstract = soup.get_text(strip=False)
            # Keep only first 350 characters
            abstract = abstract[:350] + '...'

        lines = abstract.split('\n')
        if upcoming:
            abstract = '#[br] \n        |'.join(lines)
        else:
            abstract = '#[br] \n      |'.join(lines)

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
    parser.add_argument('-n', '--number', type=int, default=5,
                        help='Number of talks to render')
    parser.add_argument('-d', '--date', type=str,
                        help='Render page for a specific date '
                             '(format: DD/MM/YYYY)')
    parser.add_argument('csv_filename', type=str,
                        help='CSV file containing talks')
    parser.add_argument('showcase_filename', type=str,
                        help='Markdown file containing the showcase',
                        nargs='?')
    args = parser.parse_args()

    # Assign arguments
    showcase = args.showcase_filename

    talks = []
    with open(args.csv_filename, 'rb') as fp:
        gcal = Calendar.from_ical(fp.read())
        for component in gcal.walk():
            if component.name == "VEVENT":
                talks.append({
                    'Titolo': component.get('summary'),
                    'Inizio': component.get('dtstart').dt.astimezone(),
                    'Fine': component.get('dtend').dt.astimezone(),
                    'Luogo': component.get('location'),
                    'Abstract': component.get('description')
                })

    # Get current date and time
    if not args.date:
        now = dt.now().astimezone()
    else:
        now = dt.strptime(args.date, '%d/%m/%Y')

    # Sort by start time
    talks.sort(key=lambda t: t['Inizio'])

    # Filter talks
    talks = [talk for talk in talks if talk['Titolo']]
    future = [talk for talk in talks if talk['Fine'] > now]

    # Log future events
    for t in future:
        print(f'Ok {t["Titolo"]} {t["Inizio"]} {now}')

    # Check if there are future events
    if future:

        # There is not a showcase event
        if not showcase:
            # Assign upcoming
            upcoming, future = future[0], future[1:]

            # Render upcoming
            with open('layout/upcoming.pug', 'w') as f:
                f.write('.row.mt-4.mb-2\n')
                f.write('  h1 #[span.emoji 🚀] Upcoming')
                f.write(render_talk(upcoming, True))
        else:
            with open('layout/upcoming.pug', 'w') as f:
                f.write('.row.mt-4.mb-2.justify-content-center\n')
                f.write("  include:markdown-it(linkify"
                        "langPrefix='highlight-' html='true')"
                        " ../showcase.md")

        # Render next events
        with open('layout/next.pug', 'w') as f:
            if future:
                # Write header
                f.write('.row.mt-4.mb-4\n')
                f.write('  h1 #[span.emoji 🔮] Next Events\n')

                # Write the next n talks
                second = True
                for talk in future[:args.number]:
                    f.write(render_talk(talk, second=second))
                    second = False
            else:
                # Empty next events
                f.write('')

    else:
        # There is not a showcase event
        if not showcase:
            fname = 'layout/upcoming.pug'
        else:
            fname = 'layout/next.pug'

        # Empty upcoming
        with open(fname, 'w') as f:
            f.write('.row.mt-4.mb-2\n')
            f.write('  h1 #[span.emoji 💀] No Events\n')

    # Render footer with date and hour
    with open('layout/footer.pug', 'w') as f:
        footer = raw_footer.replace('%%%DATE%%%', now.strftime('%d/%m/%Y'))
        footer = footer.replace('%%%HOUR%%%', now.strftime('%H:%M'))
        f.write(footer)
