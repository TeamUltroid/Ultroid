# Ultroid - UserBot
# Copyright (C) 2021 TeamUltroid
#
# This file is a part of < https://github.com/TeamUltroid/Ultroid/ >
# PLease read the GNU Affero General Public License in
# <https://www.github.com/TeamUltroid/Ultroid/blob/main/LICENSE/>.
"""
✘ Commands Available -

• `{i}saavn <search query>`
    Download songs from Saavn

"""
import os
import time

from telethon.tl.types import DocumentAttributeAudio

from . import *


@ultroid_cmd(
    pattern="saavn ?(.*)",
)
async def siesace(e):
    song = e.pattern_match.group(1)
    if not song:
        return await eor(e, "`Give me Something to Search", time=5)
    hmm = time.time()
    lol = await eor(e, f"`Searching {song} on Saavn...`")
    song, duration, performer, thumb = await saavn_dl(song)
    if not song:
        return await eod(lol, "`Song not found...`")
    title = song.split(".")[0]
    okk = await uploader(song, song, hmm, lol, "Uploading " + title + "...")
    await e.reply(
        file=okk,
        message="`" + title + "`" + "\n`From Saavn`",
        attributes=[
            DocumentAttributeAudio(
                duration=int(duration),
                title=title,
                performer=performer,
            )
        ],
        supports_streaming=True,
        thumb=thumb,
    )
    await lol.delete()
    [os.remove(x) for x in [song, thumb]]
