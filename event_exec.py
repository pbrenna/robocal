import subprocess
import sys
import shlex
import os
import signal


def evexec(ev, conf, duration_sec):
    parts = ev.summary.strip().split(" ")
    action = conf['action.' + parts[0]]
    auto_kill = True if action.get("auto_kill", "True") != "False" else False
    start_exec = action.get("start_exec", "").strip()
    end_exec = action.get("end_exec", "").strip()
    should_stop = auto_kill or end_exec != ""
    env = {'subprocess': None}
    if start_exec != "":
        command = start_exec + " " + \
            str(duration_sec) + " " + " ".join([shlex.quote(x) for x in parts])
        env['subprocess'] = subprocess.Popen(
            command, shell=True, stdout=sys.stdout, stderr=sys.stderr, preexec_fn=os.setsid)

    return (env, should_stop)


def evexec_stop(ev, should_stop, conf, envir):
    print("Stopping " + ev.summary)
    parts = ev.summary.split(" ")
    action = conf['action.' + parts[0]]
    subp = envir['subprocess']
    if subp is not None and should_stop:
        os.killpg(os.getpgid(subp.pid), signal.SIGTERM)
    end_exec = action.get("end_exec", "").strip()
    if end_exec != "":
        command = end_exec + " " + \
            " ".join([shlex.quote(x) for x in parts])
        subprocess.Popen(
            command, shell=True, stdout=sys.stdout, stderr=sys.stderr)
    print("Stopped " + ev.summary)
