import requests
from bs4 import BeautifulSoup
from ics import Calendar, Event
from datetime import datetime
from dateutil import parser
import pytz
import hashlib

URL = "https://www-ljk.imag.fr/spip.php?article10"
TIMEZONE = pytz.timezone("Europe/Paris")

def stable_uid(date_str, time_str, speaker):
    base = f"{date_str}-{time_str}-{speaker}"
    return hashlib.md5(base.encode()).hexdigest() + "@ljk-seminars"

def parse_date_time(date_text, time_text):
    dt = parser.parse(f"{date_text} {time_text}", dayfirst=True)
    return TIMEZONE.localize(dt)

def scrape():
    response = requests.get(URL)
    soup = BeautifulSoup(response.text, "html.parser")

    events = []

    seminar_blocks = soup.find_all("li", class_="event")

    for block in seminar_blocks:

        title_tag = block.find("b", class_="titre-event")
        title = title_tag.text.strip() if title_tag else "TBA"

        speaker_tag = block.find("span", class_="auteur")
        speaker = speaker_tag.text.replace("", "").strip() if speaker_tag else "Unknown"

        date_tag = block.find("span", class_="date")
        if not date_tag:
            continue

        # Format example: "02/04/2026 - 14:00"
        date_text = date_tag.text.strip()
        date_part, time_part = [x.strip() for x in date_text.split("-")]

        room_tag = block.find("span", class_="lieu")
        room = room_tag.text.strip() if room_tag else ""

        series_tag = block.find("span", class_="nomseminaire")
        series = series_tag.text.strip() if series_tag else ""

        start_dt = parse_date_time(date_part, time_part)

        e = Event()
        e.name = title
        e.begin = start_dt
        e.duration = {"hours": 1}
        e.location = room
        e.description = f"Speaker: {speaker}\nSeries: {series}"
        e.uid = stable_uid(date_part, time_part, speaker)

        events.append(e)

    return events


def generate_ics(events):
    cal = Calendar()
    for e in events:
        cal.events.add(e)

    with open("seminars.ics", "w") as f:
        f.writelines(cal)

if __name__ == "__main__":
    events = scrape()
    generate_ics(events)
