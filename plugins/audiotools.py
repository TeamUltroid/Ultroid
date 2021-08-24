# Ultroid - UserBot
# Copyright (C) 2021 TeamUltroid
#
# This file is a part of < https://github.com/TeamUltroid/Ultroid/ >
# PLease read the GNU Affero General Public License in
# <https://www.github.com/TeamUltroid/Ultroid/blob/main/LICENSE/>.

import os
import time
from datetime import datetime as dt

from hachoir.metadata import extractMetadata
from hachoir.parser import createParser
from telethon.tl.types import DocumentAttributeAudio

from . import *


@ultroid_cmd(pattern="makevoice$")
async def vnc(e):
    if not e.reply_to:
        return await eod(e, "Reply To Audio or video")
    r = await e.get_reply_message()
    if not mediainfo(r.media).startswith(("audio", "video")):
        return await eod(e, "Reply To Audio or video")
    xxx = await eor(e, "`processing...`")
    dl = r.file.name
    c_time = time.time()
    file = await downloader(
        "resources/downloads/" + dl,
        r.media.document,
        xxx,
        c_time,
        "Downloading " + dl + "...",
    )
    await xxx.edit(f"Downloaded Successfully, Now Converting to voice")
    await bash(
        f"ffmpeg -i {file.name} -map 0:a -codec:a libopus -b:a 100k -vbr on out.opus"
    )
    await e.client.send_file(e.chat_id, "out.opus", force_document=False, reply_to=r)
    await xxx.delete()
    os.remove(file.name)
    os.remove("out.opus")


@ultroid_cmd(pattern="atrim ?(.*)")
async def gen_sample(e):
    sec = e.pattern_match.group(1)
    if not sec or "-" not in sec:
        return await eod(e, "`Give time in format to trim`")
    a, b = sec.split("-")
    if int(a) >= int(b):
        return await eod(e, "`Incorrect Data`")
    vido = await e.get_reply_message()
    if vido and vido.media and mediainfo(vido.media).startswith(("video", "audio")):
        if hasattr(vido.media, "document"):
            vfile = vido.media.document
            name = vido.file.name
        else:
            vfile = vido.media
            name = ""
        if not name:
            name = dt.now().isoformat("_", "seconds") + ".mp4"
        xxx = await eor(e, "`Trying To Download...`")
        c_time = time.time()
        file = await downloader(
            "resources/downloads/" + name,
            vfile,
            xxx,
            c_time,
            "Downloading " + name + "...",
        )
        o_size = os.path.getsize(file.name)
        d_time = time.time()
        diff = time_formatter((d_time - c_time) * 1000)
        file_name = (file.name).split("/")[-1]
        out = file_name.replace(file_name.split(".")[-1], "_trimmed.aac")
        if int(b) > int(genss(file.name)):
            os.remove(file.name)
            return await eod(xxx, "`Wrong trim duration`")
        ss, dd = stdr(int(a)), stdr(int(b))
        xxx = await xxx.edit(
            f"`Downloaded {file.name} of {humanbytes(o_size)} in {diff}.\nNow Trimming Audio from `{ss}` to `{dd}`...`"
        )
        cmd = f'ffmpeg -i "{file.name}" -preset ultrafast -ss {ss} -to {dd} -vn -acodec copy "{out}" -y'
        await bash(cmd)
        os.remove(file.name)
        f_time = time.time()
        mmmm = await uploader(
            out,
            out,
            f_time,
            xxx,
            "Uploading " + out + "...",
        )
        metadata = extractMetadata(createParser(out))
        duration = 0
        artist = udB.get("artist") or ultroid_bot.first_name
        if metadata.has("duration"):
            duration = metadata.get("duration").seconds
        if metadata.has("artist"):
            artist = metadata.get("artist")
        attributes = [
            DocumentAttributeAudio(
                duration=duration,
                title=out.split(".")[0],
                performer=artist,
            )
        ]
        caption = f"Trimmed Audio From `{ss}` To `{dd}`"
        await e.client.send_file(
            e.chat_id,
            mmmm,
            thumb="resources/extras/ultroid.jpg",
            caption=caption,
            attributes=attributes,
            force_document=False,
            reply_to=e.reply_to_msg_id,
        )
        await xxx.delete()
    else:
        await eor(e, "`Reply To Video\\Audio File Only`", time=5)
