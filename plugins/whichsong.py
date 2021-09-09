# Ultroid - UserBot
# Copyright (C) 2021 TeamUltroid
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

from . import *

shazam = Shazam()


@ultroid_cmd(pattern="whichsong$")
async def song_recog(event):
    if not event.is_reply:
        return await eor(event, "`Reply to a song file to recognise it!`", time=10)
    reply = await event.get_reply_message()
    t_ = mediainfo(reply.media)
    if t_ != "audio":
        return await eor(event, "`Please use as reply to an audio file.`", time=5)
    xx = await eor(event, "`Downloading...`")
    path_to_song = "./temp/shaazam_cache/unknown.mp3"
    await reply.download_media(path_to_song)
    await xx.edit("`Trying to identify the song....`")
    try:
        res = await shazam.recognize_song(path_to_song)
    except Exception as e:
        return await eor(xx, str(e), time=10)
    remove(path_to_song)
    try:
        x = res["track"]
        await xx.edit(f"**Song Recognised!**\nName: __{x['title']}__")
    except KeyError:
        return await eor(xx, "`Couldn't identify song :(`", time=5)
