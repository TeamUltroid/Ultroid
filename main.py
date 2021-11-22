import subprocess, asyncio, os

vars = ["API_ID", "API_HASH", "SESSION", "REDIS_URI", "REDIS_PASSWORD"]

def _check(z):
    new = []
    for var in vars:
        ent = os.environ.get(var + z)
        if not ent:
            return None, []
        new.append(ent)
    return True, new


for z in range(2):
    if z == 0:
        z = ""
    fine, out = _check(str(z))
    if fine:
        subprocess.Popen(["python3", "-m", "pyUltroid", out[0], out[1], out[2], out[3], out[4]],
                     stdin=None, stderr=None, stdout=None, cwd=None)
        print(f"Started")

loop = asyncio.get_event_loop()
try:
    print("Running All")
    loop.run_forever()
except BaseException:
    loop.close()
