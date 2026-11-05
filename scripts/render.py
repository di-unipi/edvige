"""
Render the next talks as the HTML page
"""

import math
import os
import re
from datetime import date as d
from datetime import datetime as dt
from datetime import time
from typing import Optional

import fire  # type: ignore
from bs4 import BeautifulSoup  # type: ignore
from icalendar import Calendar  # type: ignore
from jinja2 import Environment, FileSystemLoader

TEMPLATE_DIR = "layout"
TEMPLATE_NAME = "index.html.j2"
LOCANDINA = "static/assets/locandina.png"


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


def truncate_abstract(abstract: str) -> list[str]:
    """Extracts the abstract text and truncates it to fit the card."""
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

    return render_lines


def build_event(talk: dict, now: dt, past_event: bool = False) -> dict:
    """Builds the template context of an event card."""

    # Parse title
    title, subtitle, hashtags = parse_event_name(talk["Titolo"])

    # Get cardinal day without leading zero, with suffix
    start, end = talk["Inizio"], talk["Fine"]
    day = f"{start.day}{suffix(start.day)}"

    abstract = talk["Abstract"]

    return {
        "title": title,
        "subtitle": subtitle,
        "hashtags": hashtags,
        "location": talk["Luogo"],
        "abstract": truncate_abstract(abstract) if abstract else [],
        "day": day,
        "month": start.strftime("%B"),
        "start_time": start.strftime("%H:%M"),
        "end_time": end.strftime("%H:%M"),
        "live": start < now < end,
        "past": past_event,
    }


def write_atomic(path: str, content: str):
    """Writes the file via a temporary file, so readers never see a partial page."""
    tmp_path = os.path.join(os.path.dirname(path) or ".", f".{os.path.basename(path)}.tmp")
    with open(tmp_path, "w", encoding="utf-8") as f:
        f.write(content)
    os.replace(tmp_path, path)


def main(
    ics_filename: str,
    output: str = "www/index.html",
    date: Optional[str] = None,
    number: Optional[int] = 15,
):
    """Main."""
    talks = []

    with open(ics_filename, "rb") as fp:
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

    # Render the page
    env = Environment(
        loader=FileSystemLoader(TEMPLATE_DIR),
        autoescape=True,
    )
    template = env.get_template(TEMPLATE_NAME)
    page = template.render(
        events=[build_event(talk, now, past_event=talk not in future) for talk in cards],
        locandina=os.path.isfile(LOCANDINA),
        updated=dt.now().astimezone(),
    )
    write_atomic(output, page + "\n")

    print(f"Rendered {len(cards)} events.")


if __name__ == "__main__":
    fire.Fire(main)
