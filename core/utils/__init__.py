import sys, subprocess, re
from ..config import Config

def isMultiClient():
    if getArg := list(filter(re.compile("--run=(.*)").match, sys.argv)):
        runCode = getArg[0].split("=")[-1]
    else:
        return startMultiClient()
    _session = getattr(Config, f"SESSION{runCode}")
    _db = _get_db(runCode)
    _botToken = getattr(Config, f"BOT_TOKEN{runCode}")

    if not (_db and _session):
        return
    return runCode, _session, _botToken
    

def _get_db(count):

    _db = None
    for key in ["REDIS_URI", "MONGO_URI", "DATABASE_URL"]:
        _db = getattr(Config, f"{key}{count}")
        if _db:
            break

    return _db

def startMultiClient():
    start = 1
    while True:
        _db = _get_db(start)
        if _db and getattr(Config, f"SESSION{start}"):
            subprocess.call([sys.executable, "-m", "core", f"--run={start}"])
            start += 1
            continue
        break


