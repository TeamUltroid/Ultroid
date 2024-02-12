# Ultroid - UserBot
# Copyright (C) 2021-2024 TeamUltroid
#
# This file is a part of < https://github.com/TeamUltroid/Ultroid/ >
# PLease read the GNU Affero General Public License in
# <https://www.github.com/TeamUltroid/Ultroid/blob/main/LICENSE/>.
"""
✘ Commands Available

•`{i}invertgif`
  Make Gif Inverted(negative).

•`{i}bwgif`
  Make Gif black and white

•`{i}rvgif`
  Reverse a gif

•`{i}vtog`
  Reply To Video , It will Create Gif
  Video to Gif

•`{i}gif <query>`
   Send video regarding to query.
"""
import os
import random
import time
from datetime import datetime as dt

from . import HNDLR, LOGS, bash, downloader, get_string, mediainfo, ultroid_cmd


@ultroid_cmd(pattern="(bw|invert)gif$")
async def igif(e):
    match = e.pattern_match.group(1).strip()
    a = await e.get_reply_message()
    if not (a and a.media):
        return await e.eor("`Reply To gif only`", time=5)
    wut = mediainfo(a.media)
    if "gif" not in wut:
        return await e.eor("`Reply To Gif Only`", time=5)
    xx = await e.eor(get_string("com_1"))
    z = await a.download_media()
    if match == "bw":
        cmd = f'ffmpeg -i "{z}" -vf format=gray ult.gif -y'
    else:
        cmd = f'ffmpeg -i "{z}" -vf lutyuv="y=negval:u=negval:v=negval" ult.gif -y'
    try:
        await bash(cmd)
        await e.client.send_file(e.chat_id, "ult.gif", supports_streaming=True)
        os.remove(z)
        os.remove("ult.gif")
        await xx.delete()
    except Exception as er:
        LOGS.info(er)


@ultroid_cmd(pattern="rvgif$")
async def reverse_gif(event):
    a = await event.get_reply_message()
    if not (a and a.media) and "video" not in mediainfo(a.media):
        return await event.eor("`Reply To Video only`", time=5)
    msg = await event.eor(get_string("com_1"))
    file = await a.download_media()
    await bash(f'ffmpeg -i "{file}" -vf reverse -af areverse reversed.mp4 -y')
    await event.respond("- **Reversed Video/GIF**", file="reversed.mp4")
    await msg.delete()
    os.remove(file)
    os.remove("reversed.mp4")


@ultroid_cmd(pattern="gif( (.*)|$)")
async def gifs(ult):
    get = ult.pattern_match.group(1).strip()
    xx = random.randint(0, 5)
    n = 0
    if ";" in get:
        try:
            n = int(get.split(";")[-1])
        except IndexError:
            pass
    if not get:
        return await ult.eor(f"`{HNDLR}gif <query>`")
    m = await ult.eor(get_string("com_2"))
    gifs = await ult.client.inline_query("gif", get)
    if not n:
        await gifs[xx].click(
            ult.chat_id, reply_to=ult.reply_to_msg_id, silent=True, hide_via=True
        )
    else:
        for x in range(n):
            await gifs[x].click(
                ult.chat_id, reply_to=ult.reply_to_msg_id, silent=True, hide_via=True
            )
    await m.delete()


@ultroid_cmd(pattern="vtog$")
async def vtogif(e):
    a = await e.get_reply_message()
    if not (a and a.media):
        return await e.eor("`Reply To video only`", time=5)
    wut = mediainfo(a.media)
    if "video" not in wut:
        return await e.eor("`Reply To Video Only`", time=5)
    xx = await e.eor(get_string("com_1"))
    dur = a.media.document.attributes[0].duration
    tt = time.time()
    if int(dur) < 120:
        z = await a.download_media()
        await bash(
            f'ffmpeg -i {z} -vf "fps=10,scale=320:-1:flags=lanczos,split[s0][s1];[s0]palettegen[p];[s1][p]paletteuse" -loop 0 ult.gif -y'
        )
    else:
        filename = a.file.name
        if not filename:
            filename = "video_" + dt.now().isoformat("_", "seconds") + ".mp4"
        vid = await downloader(filename, a.media.document, xx, tt, get_string("com_5"))
        z = vid.name
        await bash(
            f'ffmpeg -ss 3 -t 100 -i {z} -vf "fps=10,scale=320:-1:flags=lanczos,split[s0][s1];[s0]palettegen[p];[s1][p]paletteuse" -loop 0 ult.gif'
        )

    await e.client.send_file(e.chat_id, "ult.gif", support_stream=True)
    os.remove(z)
    os.remove("ult.gif")
    await xx.delete()
