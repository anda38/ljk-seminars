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

    seminar_blocks = soup.find_all("div", class_="seminar")  # adjust if needed

    for block in seminar_blocks:

        title_tag = block.find("h3")
        title = title_tag.text.strip() if title_tag else "TBA"

        speaker = block.find("span", class_="speaker")
        speaker = speaker.text.strip() if speaker else "Unknown"

        date = block.find("span", class_="date")
        date = date.text.strip() if date else None

        time = block.find("span", class_="time")
        time = time.text.strip() if time else "14:00"

        room = block.find("span", class_="room")
        room = room.text.strip() if room else "IMAG 106"

        series = block.find("span", class_="series")
        series = series.text.strip() if series else ""

        if not date:
            continue

        start_dt = parse_date_time(date, time)

        e = Event()
        e.name = title
        e.begin = start_dt
        e.duration = {"hours": 1}
        e.location = room
        e.description = f"Speaker: {speaker}\nSeries: {series}"
        e.uid = stable_uid(date, time, speaker)

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
