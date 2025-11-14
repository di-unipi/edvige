import math
import re
from datetime import datetime as dt, date as dt_date, time as dt_time
from pathlib import Path
from typing import Optional, List, Dict, Any

import fire
from bs4 import BeautifulSoup
from icalendar import Calendar
import yaml

# === ICS Downloader =====================================

URL_ICS = (
    "https://calendar.google.com/calendar/ical/"
    "c_31hk6lrp2plgq36e1heodpbca0%40group.calendar.google.com/"
    "public/basic.ics"
)


def download_ics(
    url: str = URL_ICS,
    dest_path: Path = Path(__file__).parent / "basic.ics",
):
    """Scarica un file ICS da URL e lo salva in dest_path."""
    import requests

    response = requests.get(url)
    response.raise_for_status()

    with open(dest_path, mode="wb") as localfile:
        localfile.write(response.content)


# === Utility per formattazione data/ora =====================================


def suffix(d: int) -> str:
    """Restituisce il suffisso inglese per un giorno (st, nd, rd, th)."""
    if 11 <= d <= 13:
        return "th"
    last = d % 10
    if last == 1:
        return "st"
    if last == 2:
        return "nd"
    if last == 3:
        return "rd"
    return "th"


def format_day_month(start: dt) -> tuple[str, str]:
    """Restituisce (day, month) per Jekyll, es. ('5th', 'March')."""
    day_int = int(start.strftime("%d"))
    day = f"{day_int}{suffix(day_int)}"
    month = start.strftime("%B")
    return day, month


def format_time(start: dt, end: dt) -> str:
    """Restituisce 'HH:MM-HH:MM'."""
    start_time = start.strftime("%H:%M")
    end_time = end.strftime("%H:%M")
    return f"{start_time}-{end_time}"


# === Parsing titolo / hashtag ===============================================


def parse_event_name(name: str) -> tuple[str, str, List[str]]:
    """
    Analizza il summary e restituisce (title, subtitle, hashtags).

    Pattern supportati:
      [TYPE] Title (Speaker, Institution)
      [TYPE] Title (Speaker)
      [TYPE] Title
      altrimenti: (name, "", [])
    """
    # 1) [TYPE] Title (Speaker, Institution)
    pattern = re.compile(
        r"\[(?P<type>.+)\] (?P<title>.+) \((?P<speaker>.+), (?P<institution>.+)\)"
    )
    match = pattern.match(name)
    if match:
        title = match.group("title")
        subtitle = f'{match.group("speaker")}, {match.group("institution")}'
        hashtags = [x.strip() for x in match.group("type").split(",")]
        return title, subtitle, hashtags

    # 2) [TYPE] Title (Speaker)
    pattern = re.compile(r"\[(?P<type>.+)\] (?P<title>.+) \((?P<speaker>.+)\)")
    match = pattern.match(name)
    if match:
        title = match.group("title")
        subtitle = match.group("speaker")
        hashtags = [x.strip() for x in match.group("type").split(",")]
        return title, subtitle, hashtags

    # 3) [TYPE] Title
    pattern = re.compile(r"\[(?P<type>.+)\] (?P<title>.+)")
    match = pattern.match(name)
    if match:
        title = match.group("title")
        subtitle = ""
        hashtags = [x.strip() for x in match.group("type").split(",")]
        return title, subtitle, hashtags

    # 4) Fallback
    return name, "", []


# === Abstract / descrizione ==================================================


def build_abstract_html(raw_description: Optional[str]) -> str:
    """
    Ricrea l'abstract troncato come nel tuo render.py, restituisce HTML con <br>.
    """
    if not raw_description:
        return ""

    # Rimuoviamo eventuale HTML presente nell'ICS
    soup = BeautifulSoup(raw_description, features="lxml")
    abstract_text = soup.get_text(strip=False)

    lines = abstract_text.split("\n")

    max_lines = 10
    avg_chars = 58
    curr_line = 0
    render_lines: List[str] = []
    ellipsis = False

    for line in lines:
        # budget di caratteri rimanente
        char_budget = avg_chars * (max_lines - curr_line)
        content = line[:char_budget]

        if len(line) > char_budget:
            if " " in content:
                content = content.rsplit(" ", 1)[0]
            content = content.rstrip() + "..."
            ellipsis = True

        if content:
            content_lines = math.ceil(len(content) / avg_chars)
        else:
            content_lines = 0

        curr_line += max(1, content_lines)
        render_lines.append(content)

        if curr_line >= max_lines:
            break

    if not ellipsis and len(lines) > len(render_lines):
        # aggiungi "(...)" alla fine se abbiamo tagliato le righe
        last_line = render_lines.pop()
        while len(last_line) == 0 and render_lines:
            last_line = render_lines.pop()
        last_line = last_line.rstrip() + " (...)"
        render_lines.append(last_line)

    # Costruiamo HTML con <br>
    render_lines = [l for l in render_lines if l is not None]
    return "<br>\n".join(render_lines)


# === Conversione VEVENT -> dict =============================================


def ensure_datetime(value) -> dt:
    """
    Alcuni ICS possono usare solo date (senza ora).
    Converte in datetime con mezzanotte se serve, e garantisce timezone.
    """
    if isinstance(value, dt):
        result = value
    elif isinstance(value, dt_date):
        result = dt.combine(value, dt_time.min)
    else:
        raise TypeError(f"Tipo datetime non supportato: {type(value)}")

    if result.tzinfo is None:
        result = result.astimezone()
    return result


def event_to_dict(component, now: dt) -> Dict[str, Any]:
    """Converte un componente VEVENT in un dict Jekyll-friendly."""

    summary = component.get("summary")
    title_raw = str(summary) if summary is not None else ""

    start = ensure_datetime(component.get("dtstart").dt)
    end = ensure_datetime(component.get("dtend").dt)

    location = component.get("location")
    description = component.get("description")

    # Parsing del nome
    title, subtitle, hashtags = parse_event_name(title_raw)

    # Giorno / mese / orario
    day, month = format_day_month(start)
    time_range = format_time(start, end)

    # LIVE / PAST
    live = start < now < end
    past = end <= now

    # Abstract HTML
    abstract_html = build_abstract_html(description)

    return {
        # valori usati dal template
        "day": day,
        "month": month,
        "time": time_range,
        "title": title,
        "subtitle": subtitle,
        "location": str(location) if location else "",
        "hashtags": hashtags,
        "abstract_html": abstract_html,
        "live": bool(live),
        "past": bool(past),
        # valori interni per ordinamento / filtro
        "_start_dt": start,
        "_end_dt": end,
    }


# === Main ====================================================================


def main(
    ics_path: Optional[str] = None,
    output: Optional[str] = None,
    date: Optional[str] = None,
    number: Optional[int] = 15,
) -> None:
    """
    Legge un ICS e scrive _data/events.yml in formato YAML per Jekyll.

    Args:
        ics_path: path al file .ics.
                  Se None, usa "basic.ics" nella *stessa cartella* di questo script.
        output: path del file YAML. Se None, usa "_data/events.yml" rispetto alla CWD.
        date: data di riferimento (dd/mm/YYYY). Se None -> ora attuale.
        number: numero massimo di eventi da mostrare (future+past).
    """
    script_dir = Path(__file__).resolve().parent

    # ICS di default: basic.ics nella stessa cartella dello script
    ics_file = (
        script_dir / "basic.ics"
        if ics_path is None
        else Path(ics_path).expanduser().resolve()
    )

    output_path = (
        Path("_data/events.yml")
        if output is None
        else Path(output).expanduser().resolve()
    )

    if not ics_file.is_file():
        raise FileNotFoundError(f"File ICS non trovato: {ics_file}")

    # Data di riferimento

    now = dt.strptime(date, "%d/%m/%Y").astimezone() if date else dt.now().astimezone()

    # Legge ICS
    events: List[Dict[str, Any]] = []

    content = ics_file.read_text(encoding="utf-8")
    gcal = Calendar.from_ical(content)

    for component in gcal.walk():
        if component.name != "VEVENT":
            continue
        summary = component.get("summary")
        if not summary:
            continue
        event_dict = event_to_dict(component, now)
        events.append(event_dict)

    # Ordina per data di inizio
    events.sort(key=lambda e: e["_start_dt"])

    # Split future / past
    future = [e for e in events if e["_end_dt"] > now]
    past = [e for e in events if e["_end_dt"] <= now]

    if number is None:
        number = len(future)

    selected: List[Dict[str, Any]] = []
    selected.extend(future[:number])
    past_number = max(number - len(selected), 0)
    selected.extend(list(reversed(past))[:past_number])

    # Serializzazione per YAML: togliamo i campi interni _start_dt/_end_dt,
    # e aggiungiamo start/end in ISO 8601.
    serialised: List[Dict[str, Any]] = []
    for e in selected:
        data = {k: v for k, v in e.items() if not k.startswith("_")}
        data["start"] = e["_start_dt"].isoformat()
        data["end"] = e["_end_dt"].isoformat()
        serialised.append(data)

    # Crea cartella _data se non esiste
    output_path.parent.mkdir(parents=True, exist_ok=True)

    yaml_text = yaml.dump(serialised, allow_unicode=True, sort_keys=False)
    output_path.write_text(yaml_text, encoding="utf-8")

    print(f"[LOG] Written {len(serialised)} events to {output_path}\n")


if __name__ == "__main__":
    download_ics()
    fire.Fire(main)
