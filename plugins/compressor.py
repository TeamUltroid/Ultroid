# Ultroid - UserBot
# Copyright (C) 2021-2025 TeamUltroid
#
# This file is a part of < https://github.com/TeamUltroid/Ultroid/ >
# PLease read the GNU Affero General Public License in
# <https://www.github.com/TeamUltroid/Ultroid/blob/main/LICENSE/>.

from . import get_help

__doc__ = get_help("help_compressor")


import asyncio
import os
import re
import time
from datetime import datetime as dt

from telethon.errors.rpcerrorlist import MessageNotModifiedError
from telethon.tl.types import DocumentAttributeVideo

from pyUltroid.fns.tools import metadata

from . import (
    ULTConfig,
    bash,
    downloader,
    get_string,
    humanbytes,
    math,
    mediainfo,
    time_formatter,
    ultroid_cmd,
    uploader,
)


@ultroid_cmd(pattern="compress( (.*)|$)")
async def _(e):
    cr = e.pattern_match.group(1).strip()
    crf = 27
    to_stream = False
    if cr:
        k = e.text.split()
        if len(k) == 2:
            crf = int(k[1]) if k[1].isdigit() else 27
        elif len(k) > 2:
            crf = int(k[1]) if k[1].isdigit() else 27
            to_stream = "stream" in k[2]
    vido = await e.get_reply_message()
    if vido and vido.media and "video" in mediainfo(vido.media):
        if hasattr(vido.media, "document"):
            vfile = vido.media.document
            name = vido.file.name
        else:
            vfile = vido.media
            name = ""
        if not name:
            name = "video_" + dt.now().isoformat("_", "seconds") + ".mp4"
        xxx = await e.eor(get_string("audiotools_5"))
        c_time = time.time()
        file = await downloader(
            f"resources/downloads/{name}",
            vfile,
            xxx,
            c_time,
            f"Downloading {name}...",
        )

        o_size = os.path.getsize(file.name)
        d_time = time.time()
        diff = time_formatter((d_time - c_time) * 1000)
        file_name = (file.name).split("/")[-1]
        out = file_name.replace(file_name.split(".")[-1], "compressed.mkv")
        await xxx.edit(
            f"`Downloaded {file.name} of {humanbytes(o_size)} in {diff}.\nNow Compressing...`"
        )
        x, y = await bash(
            f'mediainfo --fullscan """{file.name}""" | grep "Frame count"'
        )
        if y and y.endswith("NOT_FOUND"):
            return await xxx.edit(f"ERROR: `{y}`")
        total_frames = x.split(":")[1].split("\n")[0]
        progress = f"progress-{c_time}.txt"
        with open(progress, "w"):
            pass
        proce = await asyncio.create_subprocess_shell(
            f'ffmpeg -hide_banner -loglevel quiet -progress {progress} -i """{file.name}""" -preset ultrafast -vcodec libx265 -crf {crf} -c:a copy """{out}""" -y',
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        while proce.returncode != 0:
            await asyncio.sleep(3)
            with open(progress, "r+") as fil:
                text = fil.read()
                frames = re.findall("frame=(\\d+)", text)
                size = re.findall("total_size=(\\d+)", text)
                speed = 0
                if len(frames):
                    elapse = int(frames[-1])
                if len(size):
                    size = int(size[-1])
                    per = elapse * 100 / int(total_frames)
                    time_diff = time.time() - int(d_time)
                    speed = round(elapse / time_diff, 2)
                if int(speed) != 0:
                    some_eta = ((int(total_frames) - elapse) / speed) * 1000
                    text = f"`Compressing {file_name} at {crf} CRF.\n`"
                    progress_str = "`[{0}{1}] {2}%\n\n`".format(
                        "".join("●" for _ in range(math.floor(per / 5))),
                        "".join("" for _ in range(20 - math.floor(per / 5))),
                        round(per, 2),
                    )

                    e_size = f"{humanbytes(size)} of ~{humanbytes((size / per) * 100)}"
                    eta = f"~{time_formatter(some_eta)}"
                    try:
                        await xxx.edit(
                            text
                            + progress_str
                            + "`"
                            + e_size
                            + "`"
                            + "\n\n`"
                            + eta
                            + "`"
                        )
                    except MessageNotModifiedError:
                        pass
        os.remove(file.name)
        c_size = os.path.getsize(out)
        f_time = time.time()
        difff = time_formatter((f_time - d_time) * 1000)
        await xxx.edit(
            f"`Compressed {humanbytes(o_size)} to {humanbytes(c_size)} in {difff}\nTrying to Upload...`"
        )
        differ = 100 - ((c_size / o_size) * 100)
        caption = f"**Original Size: **`{humanbytes(o_size)}`\n"
        caption += f"**Compressed Size: **`{humanbytes(c_size)}`\n"
        caption += f"**Compression Ratio: **`{differ:.2f}%`\n"
        caption += f"\n**Time Taken To Compress: **`{difff}`"
        n_file, _ = await e.client.fast_uploader(
            out, show_progress=True, event=e, message="Uploading...", to_delete=True
        )
        if to_stream:
            data = await metadata(out)
            width = data["width"]
            height = data["height"]
            duration = data["duration"]
            attributes = [
                DocumentAttributeVideo(
                    duration=duration, w=width, h=height, supports_streaming=True
                )
            ]
            await e.client.send_file(
                e.chat_id,
                n_file,
                thumb=ULTConfig.thumb,
                caption=caption,
                attributes=attributes,
                force_document=False,
                reply_to=e.reply_to_msg_id,
            )
        else:
            await e.client.send_file(
                e.chat_id,
                n_file,
                thumb=ULTConfig.thumb,
                caption=caption,
                force_document=True,
                reply_to=e.reply_to_msg_id,
            )
            await xxx.delete()
            os.remove(out)
            os.remove(progress)
    else:
        await e.eor(get_string("audiotools_8"), time=5)
