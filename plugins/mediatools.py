# Ultroid - UserBot
# Copyright (C) 2021 TeamUltroid
#
# This file is a part of < https://github.com/TeamUltroid/Ultroid/ >
# PLease read the GNU Affero General Public License in
# <https://www.github.com/TeamUltroid/Ultroid/blob/main/LICENSE/>.
"""
✘ Commands Available -

• `{i}mediainfo <reply to media>`
   To get info about it.
"""
import os
import time
from datetime import datetime as dt

from . import (
    LOGS,
    bash,
    downloader,
    eor,
    get_string,
    make_html_telegraph,
    mediainfo,
    ultroid_cmd,
)


@ultroid_cmd(pattern="mediainfo$")
async def mi(e):
    r = await e.get_reply_message()
    if not (r and r.media):
        return await eor(e, get_string("cvt_3"), time=5)
    xx = mediainfo(r.media)
    murl = r.media.stringify()
    url = make_html_telegraph("Mediainfo", "Ultroid", f"<code>{murl}</code>")
    ee = await eor(e, f"**[{xx}]({url})**\n\n`Loading More...`", link_preview=False)
    taime = time.time()
    if hasattr(r.media, "document"):
        file = r.media.document
        mime_type = file.mime_type
        filename = r.file.name
        if not filename:
            if "audio" in mime_type:
                filename = "audio_" + dt.now().isoformat("_", "seconds") + ".ogg"
            elif "video" in mime_type:
                filename = "video_" + dt.now().isoformat("_", "seconds") + ".mp4"
        dl = await downloader(
            "resources/downloads/" + filename,
            file,
            ee,
            taime,
            f"`**[{xx}]({url})**\n\n`Loading More...",
        )
        naam = dl.name
    else:
        naam = await r.download_media()
    out, er = await bash(f"mediainfo '{naam}' --Output=HTML")
    if er:
        LOGS.info(er)
        return await ee.edit(f"**[{xx}]({url})**", link_preview=False)
    urll = make_html_telegraph("Mediainfo", "Ultroid", out)
    await ee.edit(
        f"**[{xx}]({url})**\n\n[{get_string('mdi_1')}]({urll})", link_preview=False
    )
    os.remove(naam)
