# Ultroid - UserBot
# Copyright (C) 2021-2022 TeamUltroid
#
# This file is a part of < https://github.com/TeamUltroid/Ultroid/ >
# PLease read the GNU Affero General Public License in
# <https://www.github.com/TeamUltroid/Ultroid/blob/main/LICENSE/>.
"""
✘ Commands Available -

`{i}makevoice <reply to audio>`
   creates a voice note from Audio.

`{i}atrim <from time> - <to time>`
   trim audio as per given time.
   time must be in seconds. `{i}atrim 50-70`

`{i}extractaudio <reply to media>`
   To extract the audio from it.

"""

import os
import time
from datetime import datetime as dt

from pyUltroid.functions.tools import set_attributes

from . import (
    LOGS,
    bash,
    downloader,
    eod,
    eor,
    genss,
    get_string,
    humanbytes,
    mediainfo,
    stdr,
    time_formatter,
    ultroid_cmd,
    uploader,
)


@ultroid_cmd(pattern="makevoice$")
async def vnc(e):
    if not e.reply_to:
        return await eod(e, get_string("audiotools_1"))
    r = await e.get_reply_message()
    if not mediainfo(r.media).startswith(("audio", "video")):
        return await eod(e, get_string("spcltool_1"))
    xxx = await e.eor(get_string("com_1"))
    file, _ = await e.client.fast_downloader(
        r.document,
    )
    await xxx.edit(get_string("audiotools_2"))
    await bash(
        f"ffmpeg -i '{file.name}' -map 0:a -codec:a libopus -b:a 100k -vbr on out.opus"
    )
    try:
        await e.client.send_message(
            e.chat_id, file="out.opus", force_document=False, reply_to=r
        )
    except Exception as er:
        LOGS.exception(er)
        return await xxx.edit("`Failed to convert in Voice...`")
    await xxx.delete()
    os.remove(file.name)
    os.remove("out.opus")


@ultroid_cmd(pattern="atrim( (.*)|$)")
async def trim_aud(e):
    sec = e.pattern_match.group(1).strip()
    if not sec or "-" not in sec:
        return await eod(e, get_string("audiotools_3"))
    a, b = sec.split("-")
    if int(a) >= int(b):
        return await eod(e, get_string("audiotools_4"))
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
        xxx = await e.eor(get_string("audiotools_5"))
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
        if int(b) > int(await genss(file.name)):
            os.remove(file.name)
            return await eod(xxx, get_string("audiotools_6"))
        ss, dd = stdr(int(a)), stdr(int(b))
        xxx = await xxx.edit(
            f"Downloaded `{file.name}` of `{humanbytes(o_size)}` in `{diff}`.\n\nNow Trimming Audio from `{ss}` to `{dd}`..."
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
        attributes = await set_attributes(out)

        caption = get_string("audiotools_7").format(ss, dd)
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
        await e.eor(get_string("audiotools_1"), time=5)


@ultroid_cmd(pattern="extractaudio$")
async def ex_aud(e):
    reply = await e.get_reply_message()
    if not (reply and reply.media and mediainfo(reply.media).startswith("video")):
        return await e.eor(get_string("audiotools_8"))
    name = reply.file.name or "video.mp4"
    vfile = reply.media.document
    msg = await e.eor(get_string("com_1"))
    c_time = time.time()
    file = await downloader(
        "resources/downloads/" + name,
        vfile,
        msg,
        c_time,
        "Downloading " + name + "...",
    )
    out_file = file.name + ".aac"
    cmd = f"ffmpeg -i {file.name} -vn -acodec copy {out_file}"
    o, err = await bash(cmd)
    os.remove(file.name)
    attributes = await set_attributes(out_file)

    f_time = time.time()
    try:
        fo = await uploader(
            out_file,
            out_file,
            f_time,
            msg,
            "Uploading " + out_file + "...",
        )
    except FileNotFoundError:
        return await eor(msg, get_string("audiotools_9"))
    await e.client.send_file(
        e.chat_id,
        fo,
        caption=get_string("audiotools_10"),
        thumb="resources/extras/ultroid.jpg",
        attributes=attributes,
        reply_to=e.reply_to_msg_id,
    )
    await msg.delete()
