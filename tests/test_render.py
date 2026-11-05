"""
Tests for the calendar download and rendering.

Run from the repository root with: python3 -m unittest discover -s tests
"""

import os
import stat
import sys
import tempfile
import time
import unittest
from datetime import datetime as dt
from datetime import timedelta
from unittest import mock

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "scripts"))

import downloader  # noqa: E402
import render  # noqa: E402
from bs4 import BeautifulSoup  # noqa: E402

TZ = "Europe/Rome"


def read(path: str, mode: str = "r"):
    """Reads a whole file."""
    with open(path, mode, **({} if "b" in mode else {"encoding": "utf-8"})) as f:
        return f.read()

# Render in the container's timezone. The POSIX rule for Europe/Rome does not
# need the system zoneinfo database.
os.environ["TZ"] = "CET-1CEST,M3.5.0,M10.5.0/3"
time.tzset()


def ics(*events: str) -> str:
    """Wraps VEVENT bodies into a calendar."""
    body = "".join(f"BEGIN:VEVENT\n{e.strip()}\nEND:VEVENT\n" for e in events)
    return f"BEGIN:VCALENDAR\nVERSION:2.0\nPRODID:-//test//EN\n{body}END:VCALENDAR\n"


class RenderTestCase(unittest.TestCase):
    """Renders calendars to a temporary page and parses the cards."""

    def setUp(self):
        self.cwd = os.getcwd()
        os.chdir(ROOT)
        self.tmp = tempfile.TemporaryDirectory()
        self.output = os.path.join(self.tmp.name, "index.html")

    def tearDown(self):
        os.chdir(self.cwd)
        self.tmp.cleanup()

    def render(self, calendar: str, date: str = "02/11/2026", number: int = 15):
        path = os.path.join(self.tmp.name, "calendar.ics")
        with open(path, "w", encoding="utf-8") as f:
            f.write(calendar)
        with mock.patch("builtins.print"):
            render.main(path, output=self.output, date=date, number=number)
        with open(self.output, encoding="utf-8") as f:
            self.html = f.read()
        soup = BeautifulSoup(self.html, "html.parser")
        return [c for c in soup.select("#left > .card") if "special-card" not in c["class"]]


class TestEvents(RenderTestCase):
    def test_recurring_events_are_expanded(self):
        cards = self.render(ics(f"""
UID:weekly
DTSTART;TZID={TZ}:20261008T100000
DTEND;TZID={TZ}:20261008T110000
RRULE:FREQ=WEEKLY;COUNT=10
EXDATE;TZID={TZ}:20261112T100000
SUMMARY:[Seminar] Weekly
""", f"""
UID:weekly
RECURRENCE-ID;TZID={TZ}:20261119T100000
DTSTART;TZID={TZ}:20261119T150000
DTEND;TZID={TZ}:20261119T160000
SUMMARY:[Seminar] Weekly (moved)
"""), number=3)
        days = [c.select_one(".date").get_text(" ") + " " + c.select_one(".time").get_text() for c in cards]
        # 12th is excluded, 19th is moved to the afternoon
        self.assertEqual(days, ["Thu 5 November 10:00\u201311:00", "Thu 19 November 15:00\u201316:00",
                                "Thu 26 November 10:00\u201311:00"])
        self.assertTrue(all("past-event" not in c["class"] for c in cards))

    def test_cancelled_events_are_skipped(self):
        cards = self.render(ics("""
UID:cancelled
DTSTART:20261110T090000Z
DTEND:20261110T100000Z
STATUS:CANCELLED
SUMMARY:[Seminar] Cancelled
""", """
UID:confirmed
DTSTART:20261110T090000Z
DTEND:20261110T100000Z
STATUS:CONFIRMED
SUMMARY:[Seminar] Confirmed
"""))
        self.assertEqual([c.select_one(".card-title").get_text() for c in cards], ["Confirmed"])

    def test_events_without_dtend(self):
        cards = self.render(ics("""
UID:allday
DTSTART;VALUE=DATE:20261110
SUMMARY:[Seminar] All day
""", """
UID:duration
DTSTART:20261111T090000Z
DURATION:PT2H
SUMMARY:[Seminar] With duration
"""))
        self.assertEqual([c.select_one(".time").get_text() for c in cards], ["All day", "10:00\u201312:00"])

    def test_past_events_fill_remaining_cards(self):
        cards = self.render(ics("""
UID:past1
DTSTART:20261020T090000Z
DTEND:20261020T100000Z
SUMMARY:[Seminar] Older
""", """
UID:past2
DTSTART:20261025T090000Z
DTEND:20261025T100000Z
SUMMARY:[Seminar] Newer
""", """
UID:future
DTSTART:20261110T090000Z
DTEND:20261110T100000Z
SUMMARY:[Seminar] Future
"""), number=2)
        titles = [(c.select_one(".card-title").get_text(), "past-event" in c["class"]) for c in cards]
        self.assertEqual(titles, [("Future", False), ("Newer", True)])

    def test_debug_calendar(self):
        cards = self.render(read(os.path.join(ROOT, "data", "debug.ics")),
                            date="01/06/2026")
        self.assertEqual(len(cards), 12)

    def test_hashtags_inside_container(self):
        cards = self.render(ics("""
UID:tags
DTSTART:20261110T090000Z
DTEND:20261110T100000Z
SUMMARY:[Seminar, Physics] Tagged
"""))
        self.assertEqual(cards[0].select_one(".hashtags .hashtag").get_text(), "Seminar / Physics")

    def test_last_update_is_machine_readable(self):
        self.render(ics())
        soup = BeautifulSoup(self.html, "html.parser")
        updated = dt.fromisoformat(soup.select_one("#last-update")["data-updated"])
        self.assertLess(abs(dt.now().astimezone() - updated), timedelta(minutes=1))


class TestEscaping(RenderTestCase):
    def test_injection_is_escaped(self):
        cards = self.render(ics(r"""
UID:evil
DTSTART:20261110T090000Z
DTEND:20261110T100000Z
SUMMARY:[SEM] Hello #{1+1}\n- process.exit(1)\n<script>alert(1)</script>
LOCATION:Room !{1} <b>x</b>
DESCRIPTION:&lt;img src=x onerror=alert(1)&gt; #[b x]
"""))
        self.assertNotIn("<script>", self.html)
        self.assertNotIn("<img src=x", self.html)
        self.assertNotIn("<b>x</b>", self.html)
        card = cards[0]
        self.assertIn("<script>alert(1)</script>", card.select_one(".card-title").get_text())
        self.assertEqual(card.select_one(".location").get_text(), "Room !{1} <b>x</b>")
        self.assertEqual(card.select_one(".abstract").get_text(), "<img src=x onerror=alert(1)> #[b x]")


class TestAbstract(unittest.TestCase):
    def test_leading_blank_lines(self):
        lines = render.truncate_abstract("<br>\n" * 8 + "Text")
        self.assertEqual(lines, ["Text"])

    def test_only_blank_lines(self):
        self.assertEqual(render.truncate_abstract("<p></p>\n\n\n\n\n\n\n\n\n"), [])

    def test_truncated_with_marker(self):
        lines = render.truncate_abstract("\n".join(f"line {i}" for i in range(10)))
        self.assertEqual(len(lines), 7)
        self.assertEqual(lines[-1], "line 6 (...)")

    def test_long_line_ellipsis(self):
        lines = render.truncate_abstract("word " * 200)
        self.assertTrue(lines[-1].endswith("..."))


class TestWhen(unittest.TestCase):
    def at(self, *args):
        return dt(*args).astimezone()

    def test_same_day(self):
        self.assertEqual(render.render_when(self.at(2026, 11, 5, 14), self.at(2026, 11, 5, 15, 30), False),
                         "14:00\u201315:30")

    def test_ending_at_midnight(self):
        self.assertEqual(render.render_when(self.at(2026, 11, 5, 20), self.at(2026, 11, 6), False),
                         "20:00\u201300:00")

    def test_multi_day(self):
        self.assertEqual(render.render_when(self.at(2026, 11, 5, 9), self.at(2026, 11, 7, 18), False),
                         "09:00 until 7 November, 18:00")

    def test_all_day(self):
        self.assertEqual(render.render_when(self.at(2026, 11, 5), self.at(2026, 11, 6), True), "All day")

    def test_all_day_multi_day(self):
        self.assertEqual(render.render_when(self.at(2026, 11, 5), self.at(2026, 11, 8), True),
                         "Until 7 November")


class TestWriteAtomic(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.path = os.path.join(self.tmp.name, "index.html")

    def tearDown(self):
        self.tmp.cleanup()

    def test_readable_and_no_leftovers(self):
        render.write_atomic(self.path, "page")
        self.assertEqual(read(self.path), "page")
        self.assertEqual(stat.S_IMODE(os.stat(self.path).st_mode), 0o644)
        self.assertEqual(os.listdir(self.tmp.name), ["index.html"])

    def test_overlapping_writes(self):
        """A second run writing while the first one publishes must not corrupt the page."""
        real_replace = os.replace
        nested = []

        def replace(src, dst):
            if not nested:
                nested.append(True)
                render.write_atomic(self.path, "B" * 1000)
            real_replace(src, dst)

        with mock.patch("render.os.replace", side_effect=replace):
            render.write_atomic(self.path, "A" * 1000)
        self.assertEqual(read(self.path), "A" * 1000)
        self.assertEqual(os.listdir(self.tmp.name), ["index.html"])


class TestDownloader(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.path = os.path.join(self.tmp.name, "basic.ics")

    def tearDown(self):
        self.tmp.cleanup()

    def response(self, content: bytes, status: int = 200):
        response = mock.Mock(content=content, status_code=status)
        response.raise_for_status.side_effect = None if status < 400 else Exception(status)
        return response

    def test_saves_calendar_with_timeout(self):
        with mock.patch("downloader.requests.get", return_value=self.response(b"BEGIN:VCALENDAR\n")) as get:
            downloader.download("https://example.test/basic.ics", self.path)
        self.assertEqual(get.call_args.kwargs["timeout"], downloader.TIMEOUT)
        self.assertEqual(read(self.path, "rb"), b"BEGIN:VCALENDAR\n")

    def test_rejects_http_errors(self):
        with mock.patch("downloader.requests.get", return_value=self.response(b"oops", 503)):
            with self.assertRaises(Exception):
                downloader.download("https://example.test/basic.ics", self.path)
        self.assertFalse(os.path.exists(self.path))

    def test_rejects_non_calendar(self):
        with mock.patch("downloader.requests.get", return_value=self.response(b"<html>Login</html>")):
            with self.assertRaises(ValueError):
                downloader.download("https://example.test/basic.ics", self.path)
        self.assertFalse(os.path.exists(self.path))


if __name__ == "__main__":
    unittest.main()
