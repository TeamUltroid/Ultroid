from . import *
from asyncio import create_subprocess_shell, subprocess
@ultroid_cnd(pattern="getaddon (.*)")
async def ult_get(event):
    xx = await eor(event, get_string("com_1"), time=10)
    lnk = event.pattern.match_group(1)
    if not lnk:
        return await eod(xx, "`Give me a raw link.`")
    t = lnk.split('/')
    if t[2] != "raw.githubusercontent.com":
        return await eod(xx, "`You can only load plugins from a 'raw.githubusercontent.com' link..`") 
    nm = t[len(t)-1]
    cmd = f"wget {lnk} -o addons/{nm}"
    xnxx = await asyncio.create_subprocess_shell(cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE)
    stdout, stderr = await xnxx.communicate()