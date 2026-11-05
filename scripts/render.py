"""
Render the next talks as the HTML page
"""

import contextlib
import math
import os
import re
import tempfile
from datetime import date as d
from datetime import datetime as dt
from datetime import time, timedelta
from typing import Optional

import fire  # type: ignore
import recurring_ical_events  # type: ignore
from bs4 import BeautifulSoup  # type: ignore
from icalendar import Calendar  # type: ignore
from jinja2 import Environment, FileSystemLoader

TEMPLATE_DIR = "layout"
TEMPLATE_NAME = "index.html.j2"
LOCANDINA = "static/assets/locandina.png"

# Time window in which recurring events are expanded
LOOKBEHIND = timedelta(days=365)
LOOKAHEAD = timedelta(days=365)


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


def render_day(value: dt) -> str:
    """Renders the day of the month with its suffix, e.g. 5th November."""
    return f"{value.day}{suffix(value.day)} {value.strftime('%B')}"


def render_when(start: dt, end: dt, all_day: bool) -> str:
    """Renders the time span of an event, given its start and end."""
    # The end is exclusive: an event ending at midnight ends the day before
    last = end - timedelta(microseconds=1) if end > start else end
    same_day = last.date() == start.date()

    if all_day:
        return "All day" if same_day else f"Until {render_day(last)}"

    if same_day:
        return f"{start.strftime('%H:%M')}-{end.strftime('%H:%M')}"

    return f"{start.strftime('%H:%M')} until {render_day(end)}, {end.strftime('%H:%M')}"


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

    # Drop leading and trailing blank lines
    while lines and not lines[0].strip():
        lines.pop(0)
    while lines and not lines[-1].strip():
        lines.pop()

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
        # Drop trailing blank lines, then mark the truncation
        while render_lines and not render_lines[-1].strip():
            render_lines.pop()
        if render_lines:
            render_lines[-1] = render_lines[-1].rstrip() + " (...)"

    return render_lines


def build_event(talk: dict, now: dt, past_event: bool = False) -> dict:
    """Builds the template context of an event card."""

    # Parse title
    title, subtitle, hashtags = parse_event_name(talk["Titolo"])

    start, end = talk["Inizio"], talk["Fine"]
    abstract = talk["Abstract"]

    return {
        "title": title,
        "subtitle": subtitle,
        "hashtags": hashtags,
        "location": talk["Luogo"],
        "abstract": truncate_abstract(abstract) if abstract else [],
        "day": f"{start.day}{suffix(start.day)}",
        "month": start.strftime("%B"),
        "when": render_when(start, end, talk["TuttoIlGiorno"]),
        "live": start < now < end,
        "past": past_event,
    }


def write_atomic(path: str, content: str):
    """Writes the file via a unique temporary file, so readers never see a partial page."""
    directory = os.path.dirname(path) or "."
    fd, tmp_path = tempfile.mkstemp(
        dir=directory, prefix=f".{os.path.basename(path)}.", suffix=".tmp"
    )
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            f.write(content)
        # mkstemp creates the file as private, the page must be readable
        os.chmod(tmp_path, 0o644)
        os.replace(tmp_path, path)
    except BaseException:
        with contextlib.suppress(FileNotFoundError):
            os.unlink(tmp_path)
        raise


def main(
    ics_filename: str,
    output: str = "www/index.html",
    date: Optional[str] = None,
    number: Optional[int] = 15,
):
    """Main."""
    # Get current date and time
    if not date:
        now = dt.now().astimezone()
    else:
        now = dt.strptime(date, "%d/%m/%Y").astimezone()

    talks = []

    with open(ics_filename, "rb") as fp:
        # Read file as a string
        file = fp.read().decode("utf-8")
        gcal = Calendar.from_ical(file)

    # Expand recurring events, applying exceptions and moved occurrences
    for component in recurring_ical_events.of(gcal).between(now - LOOKBEHIND, now + LOOKAHEAD):
        # Skip cancelled events
        if str(component.get("status", "")).upper() == "CANCELLED":
            continue

        start = component.get("dtstart").dt
        talks.append(
            {
                "Titolo": component.get("summary"),
                "Inizio": as_datetime(start),
                # The end is always set, computed from DURATION if missing
                "Fine": as_datetime(component.get("dtend").dt),
                "TuttoIlGiorno": not isinstance(start, dt),
                "Luogo": component.get("location"),
                "Abstract": component.get("description"),
            }
        )

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
    cards = [(talk, False) for talk in future[:number]]
    past_number = max(number - len(cards), 0)
    cards += [(talk, True) for talk in list(reversed(past))[:past_number]]

    # Render the page
    env = Environment(
        loader=FileSystemLoader(TEMPLATE_DIR),
        autoescape=True,
    )
    template = env.get_template(TEMPLATE_NAME)
    page = template.render(
        events=[build_event(talk, now, past_event=is_past) for talk, is_past in cards],
        locandina=os.path.isfile(LOCANDINA),
        updated=dt.now().astimezone(),
    )
    write_atomic(output, page + "\n")

    print(f"Rendered {len(cards)} events.")


if __name__ == "__main__":
    fire.Fire(main)
