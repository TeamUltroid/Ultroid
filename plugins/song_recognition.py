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
    if not event.reply_to_msg_id:
        return await eod(event, "`Reply to a song file to recognise it!`", time=10)
    xx = await eor(event, get_string("com_1"))
    reply = await event.get_reply_message()
    t_ = mediainfo(reply.media)
    if t_ != "audio":
        return await eod(xx, "`Please use as reply to an audio file.`", time=5)
    await xx.edit("`Downloading...`")
    path_to_song = "./temp/shaazam_cache/unknown.mp3"
    await reply.download_media(path_to_song)
    await xx.edit("`Trying to identify the song....`")
    try:
        res = await shazam.recognize_song(path_to_song)
    except Exception as e:
        return await eod(xx, str(e), time=10)
    try:
        x = res["track"]
    except KeyError:
        return await eod(xx, "`Couldn't identify song :(`", time=5)
    await xx.edit(f"**Song Recognised!**\nName: __{x['title']}__")
    remove(path_to_song)
