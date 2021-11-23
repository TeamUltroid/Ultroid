import asyncio
import os
import subprocess

vars = ["API_ID", "API_HASH", "SESSION", "REDIS_URI", "REDIS_PASSWORD"]


def _check(z):
    new = []
    for var in vars:
        ent = os.environ.get(var + z)
        if not ent:
            return False, new
        new.append(ent)
    return True, new


for z in range(5):
    n = z + 1
    if z == 0:
        z = ""
    fine, out = _check(str(z))
    if fine:
        subprocess.Popen(
            ["python3", "-m", "pyUltroid", out[0], out[1], out[2], out[3], out[4], n],
            stdin=None,
            stderr=None,
            stdout=None,
            cwd=None,
        )

loop = asyncio.get_event_loop()
try:
    loop.run_forever()
except Exception as er:
    print(er)
finally:
    loop.close()
