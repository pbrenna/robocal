import configparser
import sys
import requests
import time
from multiprocessing import Process
import icalendar
import caldav
import pytz
from datetime import datetime, timedelta, date
from icalevents.icalparser import parse_events
import sched
import schedule

conf = configparser.ConfigParser()
try:
    conf.read(sys.argv[1])
except:
    print("Usage: main.py config.ini", file=sys.stderr)
    sys.exit(1)
try:
    cal = conf['calendar']
    url = cal['url']
    user = cal['user']
    password = cal['password']
except KeyError:
    print("The configuration file must contain at least a calendar key", file=sys.stderr)
    sys.exit(1)
update_freq = int(cal.get("update_frequency", 15))
sleep_seconds = update_freq * 60


def sleep_fun(tdelta):
    try:
        time.sleep(tdelta.total_seconds())
    except AttributeError:
        time.sleep(tdelta)


sch_proc = None

while True:
    sch = None
    if sch_proc is not None:
        print("Kill process")
        sch_proc.terminate()
    try:
        client = caldav.DAVClient(url, username=user, password=password)
        principal = client.principal()
    except OSError:
        print("Calendar fetch failed. Retrying in {} seconds.".format(
            sleep_seconds), file=sys.stderr)
        time.sleep(sleep_seconds)
    future_events = []
    next_minute = datetime.now(pytz.utc) + timedelta(minutes=1)
    for calendar in principal.calendars():
        for event in calendar.events():
            url = str(event.url)
            url_base = url[url.rfind("/")+1:]
            ical_text = event.data
            future_events += parse_events(ical_text, start=next_minute)
    sch = sched.scheduler(lambda: datetime.now(pytz.utc),
                          sleep_fun)
    schedule.populate_scheduler(sch, future_events, conf)
    sch_proc = Process(target=schedule.schedule_proc, args=(sch,))
    sch_proc.start()
    time.sleep(sleep_seconds)
