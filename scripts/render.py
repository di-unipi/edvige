"""
Render in Pug format the next talks
"""

import math
import re
from datetime import date as d
from datetime import datetime as dt
from datetime import time
from typing import Optional

import fire  # type: ignore
from bs4 import BeautifulSoup  # type: ignore
from icalendar import Calendar  # type: ignore


def as_datetime(value):
    """Convert icalendar date/datetime values to timezone-aware datetime."""
    if isinstance(value, dt):
        return value.astimezone()

    if isinstance(value, d):
        return dt.combine(value, time.min).astimezone()

    raise TypeError(f"Unsupported date type: {type(value)}")


def suffix(d: int) -> str:
    """Returns the correct suffix for a given day of the month."""
    return "th" if 11 <= d <= 13 else {1: "st", 2: "nd", 3: "rd"}.get(d % 10, "th")


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
    """Renders the footer."""
    now = dt.now().astimezone()
    footer_pug = ".col-6\n"
    footer_pug += f"    p.mb-0 Last update: {now.strftime('%d/%m/%Y')} at {now.strftime('%H:%M')}\n"
    footer_pug += ".col-6.text-end\n"
    footer_pug += "    p.mb-0 Made with ❤️ by the Department's Communication Team\n"
    return footer_pug


def parse_event_name(name: str) -> tuple[str, str, list[str]]:
    """Parse the event title.

    Supported formats:

    1. [TAGS] Title (Auth1, Inst1; Auth2, Inst2; Auth3; Auth4, Inst4)
    2. [TAGS] Title
    3. Fallback: raw name

    The authors list is optional.
    For each author, the name is required, while the institution is optional.

    Args:
        name: Raw event title as found in the ICS SUMMARY field.

    Returns:
        A tuple containing:
          - title: The parsed event title.
          - subtitle: Authors information, if available. Multiple authors are
            separated by "; ". Empty string if not available.
          - hashtags: A list of tags parsed from TAGS, may be empty.
    """
    pattern = re.compile(
        r"^\[(?P<type>[^\]]+)\]\s+"
        r"(?P<title>.*?)"
        r"(?:\s+\((?P<authors>[^()]*)\))?"
        r"$"
    )

    match = pattern.match(name)
    if not match:
        return name, "", []

    title = match.group("title").strip()
    hashtags = _split_tags(match.group("type"))

    raw_authors = match.group("authors")
    if not raw_authors:
        return title, "", hashtags

    authors = _split_authors(raw_authors)
    subtitle = ", ".join(authors)

    return title, subtitle, hashtags


def _split_authors(raw: str) -> list[str]:
    """Split and normalize authors.

    Supported author formats:

    - Auth1, Inst1
    - Auth2, Inst2
    - Auth3

    Authors are separated by semicolon.
    The author name is required.
    The institution is optional.
    """
    authors: list[str] = []

    for item in raw.split(";"):
        item = item.strip()
        if not item:
            continue

        parts = [part.strip() for part in item.split(",", maxsplit=1)]

        author = parts[0]
        if not author:
            continue

        if len(parts) == 2 and parts[1]:
            authors.append(f"{author} ({parts[1]})")
        else:
            authors.append(author)

    return authors


def _split_tags(raw: str) -> list[str]:
    """Split and normalize tag strings.

    Args:
        raw: Raw TAGS string, e.g. "Seminar, Physics".

    Returns:
        A list of normalized tags, spaces removed.
    """
    return [tag.strip() for tag in raw.split(",") if tag.strip()]


def render_hashtag(hashtag: str) -> str:
    return hashtag


def render_card(talk: dict, now: dt, past_event: bool = False) -> str:
    """Renders the card."""

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

        # Keep only the first 10 lines, considering
        # an average of 58 chars per line.
        max_lines = 7
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
    if past_event:
        card_pug += ".card.mb-3.past-event.invisible\n"
    else:
        card_pug += ".card.mb-3.invisible\n"

    card_pug += "  .row.g-0\n"
    card_pug += "    .col-md-3\n"
    card_pug += "      .info\n"

    # Date and time
    for line in dt_pug.split("\n"):
        card_pug += f"        {line}\n"

    # Badge for live/ended event
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

    # Hashtags
    if hashtags:
        card_pug += "        .hashtags.mt-3.pt-3.text-muted.small\n"
        # for hashtag in hashtags:
        #     card_pug += f"          span.hashtag {render_hashtag(hashtag)}\n"
        card_pug += f"        span.hashtag {', '.join(hashtags)}\n"

    # Main content
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

    return card_pug


def main(csv_filename: str, date: Optional[str] = None, number: Optional[int] = 15):
    """Main."""
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
                        "Inizio": as_datetime(component.get("dtstart").dt),
                        "Fine": as_datetime(component.get("dtend").dt),
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

    # Select cards to render: future first, then past in reverse order
    cards = future[:number]
    past_number = max(number - len(cards), 0)
    cards = cards + list(reversed(past))[:past_number]

    # Render events
    with open("layout/events.pug", "w", encoding="utf-8") as f:
        for talk in cards:
            if talk in future:
                f.write(render_card(talk, now))
            else:
                assert talk in past
                f.write(render_card(talk, now, past_event=True))

    # Render footer
    with open("layout/footer.pug", "w", encoding="utf-8") as f:
        footer = render_footer()
        f.write(footer)

    print(f"Rendered {len(cards)} events.")


if __name__ == "__main__":
    fire.Fire(main)
