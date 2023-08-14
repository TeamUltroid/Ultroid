# Ultroid - UserBot
# Copyright (C) 2021-2023 TeamUltroid
#
# This file is a part of < https://github.com/TeamUltroid/Ultroid/ >
# PLease read the GNU Affero General Public License in
# <https://www.github.com/TeamUltroid/Ultroid/blob/main/LICENSE/>.
"""
✘ Commands Available -

• `{i}whichsong`
   Reply to a song file, to recognise the song.
"""

from os import remove

from shazamio import Shazam

from . import get_string, mediainfo, ultroid_cmd

shazam = Shazam()


@ultroid_cmd(pattern="whichsong$")
async def song_recog(event):
    reply = await event.get_reply_message()
    if not (reply and mediainfo(reply.media) == "audio"):
        return await event.eor(get_string("whs_1"), time=5)
    xx = await event.eor(get_string("com_5"))
    path_to_song = "resources/downloads/"
    await reply.download_media(path_to_song)
    await xx.edit(get_string("whs_2"))
    try:
        res = await shazam.recognize_song(path_to_song)
    except Exception as e:
        return await xx.eor(str(e), time=10)
    finally:
        remove(path_to_song)

    try:
        x = res["track"]
        await xx.edit(get_string("whs_4").format(x["title"]))
    except KeyError:
        return await xx.eor(get_string("whs_3"), time=5)
