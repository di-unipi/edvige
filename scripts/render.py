"""
Render in Pug format the next talks
"""

import re
from datetime import datetime as dt
from typing import Optional

import fire  # type: ignore
from bs4 import BeautifulSoup  # type: ignore
from icalendar import Calendar  # type: ignore


def suffix(d: int) -> str:
    """Returns the correct suffix for a given day of the month."""
    return (
        "th"
        if 11 <= d <= 13
        else {1: "st", 2: "nd", 3: "rd"}.get(d % 10, "th")
    )


def render_info(start: dt, end: dt, location: str) -> str:
    """Renders the datetime object from the start and end time."""
    # Get cardinal day without leading zero
    day = str(int(start.strftime("%d")))
    # Add suffix to day
    day += suffix(int(day))

    # Get month name
    month = start.strftime("%B")

    # Start time and end time
    start_time = start.strftime("%H:%M")
    end_time = end.strftime("%H:%M")

    # Compose and return the object
    dt_pug = f"h3.mb-0 {day}\n"
    dt_pug += f"h5.month.mb-0 {month}\n"
    dt_pug += f"p.small {start_time}-{end_time}\n"
    dt_pug += f"p.small {location}"
    return dt_pug


def render_footer() -> str:
    """Renders the footer"""
    now = dt.now().astimezone()
    footer_pug = ".col-6\n"
    footer_pug += f"    p Last update: {now.strftime('%d/%m/%Y')} at {now.strftime('%H:%M')}\n"
    footer_pug += ".col-6.text-end\n"
    footer_pug += "    p Made with ❤️ by 🦉\n"
    return footer_pug


def parse_title(title: str) -> tuple[str, str]:
    """Parse the title"""
    # Check if it matches [TYPE] Title (Speaker name, Institution)
    pattern = re.compile(
        r"\[(?P<type>.+)\] (?P<title>.+) \((?P<speaker>.+), (?P<institution>.+)\)"
    )
    match = pattern.match(title)
    if match:
        title = match.group("title")
        subtitle = f'{match.group("speaker")}, {match.group("institution")}'
        hashtags = match.group("type").split(",")
        hashtags = [
            f'<span class="hashtag">#{h.strip()}</span>' for h in hashtags
        ]
        subtitle += '<div class="hashtags">' + " ".join(hashtags) + "</div>"
        return title, subtitle

    # Try then to match [TYPE] Title (Speaker name)
    pattern = re.compile(r"\[(?P<type>.+)\] (?P<title>.+) \((?P<speaker>.+)\)")
    match = pattern.match(title)
    if match:
        title = match.group("title")
        subtitle = f'{match.group("speaker")}'
        hashtags = match.group("type").split(",")
        hashtags = [
            f'<span class="hashtag">#{h.strip()}</span>' for h in hashtags
        ]
        subtitle += '<div class="hashtags">' + " ".join(hashtags) + "</div>"
        return title, subtitle

    return title, ""


def render_card(talk: dict) -> str:
    """Renders the card"""

    # Parse title
    title, subtitle = parse_title(talk["Titolo"])

    # Get the datetime object
    dt_pug = render_info(talk["Inizio"], talk["Fine"], talk["Luogo"])

    # Get the abstract
    abstract = talk["Abstract"]
    if abstract:
        # Load abstract
        soup = BeautifulSoup(abstract, features="lxml")
        # Get text
        abstract = soup.get_text(strip=False)
        # Keep only first 500 characters
        abstract = abstract[:500] + "..."
        # Split by lines
        lines = abstract.split("\n")
        abstract = "#[br] \n          | ".join(lines)

    # Compose the card
    card_pug = ""
    # card_pug += ".col\n"
    card_pug += ".card.mb-3\n"
    card_pug += "  .row.g-0\n"
    card_pug += "    .col-md-3\n"
    card_pug += "      .info\n"
    for line in dt_pug.split("\n"):
        card_pug += f"        {line}\n"
    card_pug += "    .col-md-9\n"
    card_pug += "      .card-body\n"
    card_pug += "        h5.card-title\n"
    card_pug += f"          | {title}\n"
    if subtitle:
        card_pug += "        h6.card-subtitle.mb-2.text-body-secondary\n"
        card_pug += f"          | {subtitle}\n"
    if abstract:
        card_pug += "        p.card-text\n"
        card_pug += f"          | {abstract}\n"
    return card_pug


def main(
    csv_filename: str, date: Optional[str] = None, number: Optional[int] = 9
):
    """Main"""
    talks = []
    with open(csv_filename, "rb") as fp:
        # Read file as a string
        file = fp.read().decode("utf-8")
        gcal = Calendar.from_ical(file)
        for component in gcal.walk():
            if component.name == "VEVENT":
                talks.append(
                    {
                        "Titolo": component.get("summary"),
                        "Inizio": component.get("dtstart").dt.astimezone(),
                        "Fine": component.get("dtend").dt.astimezone(),
                        "Luogo": component.get("location"),
                        "Abstract": component.get("description"),
                    }
                )

    # Get current date and time
    if not date:
        now = dt.now().astimezone()
    else:
        now = dt.strptime(date, "%d/%m/%Y").astimezone()

    # Sort by start time
    talks.sort(key=lambda t: t["Inizio"])

    # Filter talks
    talks = [talk for talk in talks if talk["Titolo"]]
    future = [talk for talk in talks if talk["Fine"] > now]

    # Get the number of events to render
    if number is None:
        number = len(future)

    # Log future events
    for t in future:
        print(f'[{now}] Read {t["Titolo"]} {t["Inizio"]}')

    # Render future events
    with open("layout/events.pug", "w", encoding="utf-8") as f:
        if future:
            for talk in future[:number]:
                f.write(render_card(talk))
                print(f'[{now}] Wrote {talk["Titolo"]} {talk["Inizio"]}')

    # Render footer
    with open("layout/footer.pug", "w", encoding="utf-8") as f:
        footer = render_footer()
        f.write(footer)


if __name__ == "__main__":
    fire.Fire(main)
