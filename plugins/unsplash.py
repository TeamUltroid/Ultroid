import asyncio
import os

from core import rm
from utilities.helper import download_file

from . import get_string, ultroid_cmd


@ultroid_cmd(pattern="unsplash( (.*)|$)")
async def searchunsl(ult):
    match = ult.pattern_match.group(1).strip()
    if not match:
        return await ult.eor("Give me Something to Search")
    num = 5
    if ";" in match:
        num = int(match.split(";")[1])
        match = match.split(";")[0]
    tep = await ult.eor(get_string("com_1"))
    with rm.get("search", helper=True, dispose=True) as mod:
        res = await mod.unsplash(match, limit=num)
    if not res:
        return await ult.eor(get_string("unspl_1"), time=5)
    CL = [download_file(rp, f"{match}-{e}.png") for e, rp in enumerate(res)]
    imgs = [z[0] for z in (await asyncio.gather(*CL)) if z]
    await ult.respond(f"Uploaded {len(imgs)} Images!", file=imgs)
    await tep.delete()
    [os.remove(img) for img in imgs]
