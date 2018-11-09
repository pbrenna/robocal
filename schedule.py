from multiprocessing import Process
from event_exec import evexec, evexec_stop
import time
from datetime import datetime
import pytz

def event_process(ev, conf):
    print("Started process for "+ev.summary)
    duration_sec = int((ev.end - ev.start).total_seconds())
    envir, should_stop = evexec(ev, conf, duration_sec)
    if should_stop:
        time.sleep(duration_sec)
        evexec_stop(ev, should_stop, conf, envir)

def event_lifecycle(ev, conf):
    print("Starting " + ev.summary)
    p = Process(target=event_process, args=(ev, conf))
    p.start()

def populate_scheduler(scheduler, events, conf):
    now = datetime.now(pytz.utc)
    for ev in events:
        if ev.start > now:
            scheduler.enterabs(ev.start, 1, event_lifecycle, argument=(ev, conf))

def schedule_proc(scheduler):
    print("Starting schedule process")
    scheduler.run()
