"""
Render in Pug format the next talks
"""

import math
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


def render_date(start: dt, end: dt) -> str:
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
    dt_pug = f"h3.day.mb-0 {day}\n"
    dt_pug += f"h5.month.mb-0 {month}\n"
    dt_pug += f"p {start_time}-{end_time}\n"
    return dt_pug


def render_footer() -> str:
    """Renders the footer"""
    now = dt.now().astimezone()
    footer_pug = ".col-6\n"
    footer_pug += f"    p.mb-0 Last update: {now.strftime('%d/%m/%Y')} at {now.strftime('%H:%M')}\n"
    footer_pug += ".col-6.text-end\n"
    footer_pug += "    p.mb-0 Made with ❤️ by the Department's Communication Team\n"
    return footer_pug


def parse_event_name(name: str) -> tuple[str, str, list[str]]:
    """Parse the title"""
    # Check if it matches [TYPE] Title (Speaker name, Institution)
    pattern = re.compile(
        r"\[(?P<type>.+)\] (?P<title>.+) \((?P<speaker>.+), (?P<institution>.+)\)"
    )
    match = pattern.match(name)
    if match:
        title = match.group("title")
        subtitle = f'{match.group("speaker")}, {match.group("institution")}'
        hashtags = match.group("type").split(",")
        return title, subtitle, hashtags

    # Try then to match [TYPE] Title (Speaker name)
    pattern = re.compile(r"\[(?P<type>.+)\] (?P<title>.+) \((?P<speaker>.+)\)")
    match = pattern.match(name)
    if match:
        title = match.group("title")
        subtitle = f'{match.group("speaker")}'
        hashtags = match.group("type").split(",")
        return title, subtitle, hashtags

    # Try then to match [TYPE] Title
    pattern = re.compile(r"\[(?P<type>.+)\] (?P<title>.+)")
    match = pattern.match(name)
    if match:
        title = match.group("title")
        subtitle = ""
        hashtags = match.group("type").split(",")
        return title, subtitle, hashtags

    return name, "", []


def render_hashtag(hashtag: str) -> str:
    return hashtag


def render_card(talk: dict, now: dt, past_event: bool = False) -> str:
    """Renders the card"""

    # Parse title
    title, subtitle, hashtags = parse_event_name(talk["Titolo"])

    # Check if the event is live
    is_live = talk["Inizio"] < now < talk["Fine"]

    # Get the datetime object
    dt_pug = render_date(talk["Inizio"], talk["Fine"])
    location = talk["Luogo"]

    # Get the abstract
    abstract = talk["Abstract"]
    if abstract:
        # Load abstract
        soup = BeautifulSoup(abstract, features="lxml")
        # Get text
        abstract = soup.get_text(strip=False)
        # Split by lines
        lines = abstract.split("\n")

        # Keep only the first 6 lines, we consider
        # an average of 60 chars per line.
        max_lines = 10
        avg_chars = 58
        curr_line = 0
        render_lines = []
        ellipsis = False

        for line in lines:
            char_budget = avg_chars * (max_lines - curr_line)
            content = line[:char_budget]
            if len(line) > char_budget:
                content = content.rsplit(" ", 1)[0]
                content = content + "..."
                ellipsis = True
            content_lines = math.ceil(len(content) / avg_chars)
            curr_line += max(1, content_lines)
            render_lines.append(content)
            if curr_line >= max_lines:
                break

        if not ellipsis and len(lines) > len(render_lines):
            last_line = render_lines.pop()
            while len(last_line) == 0:
                last_line = render_lines.pop()
            # Remove trailing spaces
            last_line = last_line.rstrip()
            last_line = last_line + " (...)"
            render_lines.append(last_line)

        abstract = "#[br] \n          | ".join(render_lines)

    # Compose the card
    card_pug = ""
    # card_pug += ".col\n"
    if past_event:
        card_pug += ".card.mb-3.past-event\n"
    else:
        card_pug += ".card.mb-3\n"
    card_pug += "  .row.g-0\n"
    card_pug += "    .col-md-3\n"
    card_pug += "      .info\n"
    for line in dt_pug.split("\n"):
        card_pug += f"        {line}\n"
    if is_live:
        card_pug += "        h4\n"
        card_pug += "          span.badge.bg-danger\n"
        card_pug += "            i.live-icon.bi.bi-broadcast\n"
        card_pug += "            span  LIVE\n"
    if past_event:
        card_pug += "        h5\n"
        card_pug += "          span.badge.bg-warning\n"
        card_pug += "            i.bi.bi-hourglass-bottom\n"
        card_pug += "            |  Ended!\n"
    card_pug += "    .col-md-9\n"
    card_pug += "      .card-body\n"
    card_pug += "        h3.card-title\n"
    card_pug += f"          | {title}\n"
    if subtitle:
        card_pug += "        h5.card-subtitle.text-body-secondary\n"
        card_pug += f"          | {subtitle}\n"
    if location:
        card_pug += "        p.i.text-body-secondary\n"
        card_pug += f"          | {location}\n"
    if abstract:
        card_pug += "        p.mt-1.card-text.abstract\n"
        card_pug += f"          | {abstract}\n"
    # if hashtags:
    #     card_pug += "  .card-footer\n"
    #     card_pug += "    p.mb-0\n"
    #     for hashtag in hashtags:
    #         card_pug += f"      span.hashtag {render_hashtag(hashtag)}\n"
    # card_pug += "      |  in \n"
    # if location:
    #     card_pug += f"      span.location {location}\n"
    return card_pug


def main(
    csv_filename: str, date: Optional[str] = None, number: Optional[int] = 15
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
    past = [talk for talk in talks if talk["Fine"] <= now]

    # Get the number of events to render
    if number is None:
        number = len(future)

    # Select cards to render (future and past in reverse order)
    cards = future[:number]
    past_number = max(number - len(cards), 0)
    cards = cards + list(reversed(past))[:past_number]

    # Log future events
    for t in future:
        print(f'[{now}] Future {t["Titolo"]} {t["Inizio"]}')
    # Log past events
    for t in past:
        print(f'[{now}] Past {t["Titolo"]} {t["Inizio"]}')

    # Render events
    with open("layout/events.pug", "w", encoding="utf-8") as f:
        for talk in cards:
            if talk in future:
                f.write(render_card(talk, now))
            else:
                assert talk in past
                f.write(render_card(talk, now, past_event=True))
            print(f'[{now}] Wrote {talk["Titolo"]} {talk["Inizio"]}')

    # Render footer
    with open("layout/footer.pug", "w", encoding="utf-8") as f:
        footer = render_footer()
        f.write(footer)


if __name__ == "__main__":
    fire.Fire(main)
