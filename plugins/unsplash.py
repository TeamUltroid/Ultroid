# Ultroid - UserBot
# Copyright (C) 2021 TeamUltroid
#
# This file is a part of < https://github.com/TeamUltroid/Ultroid/ >
# PLease read the GNU Affero General Public License in
# <https://www.github.com/TeamUltroid/Ultroid/blob/main/LICENSE/>.
"""
✘ Commands Available -

• {i}unsplash <search query> ; <no of pics>
    Unsplash Image Search.
"""

from pyUltroid.functions.misc import unsplashsearch

from . import download_file, eor, get_string, os, ultroid_cmd


@ultroid_cmd(pattern="unsplash ?(.*)")
async def searchunsl(ult):
    match = ult.pattern_match.group(1)
    if not match:
        return await eor(ult, "Give me Something to Search")
    if ";" in match:
        num = int(match.split(";")[1])
        query = match.split(";")[0]
    else:
        num = 5
        query = match
    tep = await eor(ult, get_string("com_1"))
    res = await unsplashsearch(query, limit=num)
    if not res:
        return await eor(ult, get_string("unspl_1"), time=5)
    dir = "resources/downloads/"
    CL, nl = [], 0
    for rp in res:
        Hp = await download_file(rp, f"{dir}img-{nl}.png")
        CL.append(Hp)
        nl += 1
    await ult.client.send_file(ult.chat_id, CL, caption=f"Uploaded {len(res)} Images!")
    await tep.delete()
    [os.remove(img) for img in CL]
