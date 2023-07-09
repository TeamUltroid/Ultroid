# Ultroid - UserBot
# Copyright (C) 2021-2023 TeamUltroid
#
# This file is a part of < https://github.com/TeamUltroid/Ultroid/ >
# PLease read the GNU Affero General Public License in
# <https://www.github.com/TeamUltroid/Ultroid/blob/main/LICENSE/>.
"""
✘ Commands Available -

• {i}unsplash <search query> ; <no of pics>
    Unsplash Image Search.
"""

from pyUltroid.fns.misc import unsplashsearch

from . import asyncio, download_file, get_string, os, ultroid_cmd


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
    res = await unsplashsearch(match, limit=num)
    if not res:
        return await ult.eor(get_string("unspl_1"), time=5)
    CL = [download_file(rp, f"{match}-{e}.png") for e, rp in enumerate(res)]
    imgs = [z[0] for z in (await asyncio.gather(*CL)) if z]
    await ult.respond(f"Uploaded {len(imgs)} Images!", file=imgs)
    await tep.delete()
    [os.remove(img) for img in imgs]
