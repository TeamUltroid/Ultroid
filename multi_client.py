import os
import subprocess
import sys

vars = ["API_ID", "API_HASH", "SESSION", "REDIS_URI", "REDIS_PASSWORD"]

def _check(z):
    new = []
    for var in vars:
        ent = os.environ.get(var + z)
        if not ent:
            return False, new
        new.append(ent)
    return True, new

procs = []
for z in range(5):
    n = str(z + 1)
    if z == 0:
        z = ""
    fine, out = _check(str(z))
    if fine:
        procs.append(subprocess.Popen([sys.executable, "-m", "pyUltroid", *out, n]))

if not procs:
    sys.exit(f"No client configured: set {', '.join(vars)} (suffix 1-4 for extra clients).")

for proc in procs:
    proc.wait()
