# Ultroid - UserBot
# Copyright (C) 2020 TeamUltroid
#
# This file is a part of < https://github.com/TeamUltroid/Ultroid/ >
# PLease read the GNU Affero General Public License in
# <https://www.github.com/TeamUltroid/Ultroid/blob/main/LICENSE/>.

"""
✘ Commands Available -

•`{i}compress`

"""

import asyncio
import os
import re
import time
from datetime import datetime as dt
from telethon.tl.types import DocumentAttributeVideo
from hachoir.metadata import extractMetadata
from hachoir.parser import createParser

from . import *


@ultroid_cmd(pattern="compress (\d+)?(.*)")
async def _(e):
    crf = e.pattern_match.group(1)
    if not crf:
        crf = 27
    to_stream = e.pattern_match.group(2)
    vido = await e.get_reply_message()
    if vido and vido.media:
        if "video" in mediainfo(vido.media):
            if hasattr(vido.media, "document"):
                vfile = vido.media.document
                name = vido.file.name
            else:
                vfile = vido.media
                name = ""
            if not name:
                name = "video_" + dt.now().isoformat("_", "seconds") + ".mp4"
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
            out = file_name.replace(file_name.split(".")[-1], " compressed.mkv")
            await xxx.edit(
                f"`Downloaded {file.name} of {humanbytes(o_size)} in {diff}.\nNow Compressing...`"
            )
            x, y = await bash(
                f'mediainfo --fullscan """{file.name}""" | grep "Frame count"'
            )
            total_frames = x.split(":")[1].split("\n")[0]
            progress = "progress.txt"
            with open(progress, "w") as fk:
                pass
            proce = await asyncio.create_subprocess_shell(
                f'ffmpeg -hide_banner -loglevel quiet -progress {progress} -i """{file.name}""" -preset ultrafast -c:v libx265 -crf {crf} -map 0:v -c:a aac -map 0:a -c:s copy -map 0:s? """{out}""" -y',
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )
            while proce.returncode != 0:
                await asyncio.sleep(3)
                with open(progress, "r+") as fil:
                    text = fil.read()
                    frames = re.findall("frame=(\\d+)", text)
                    size = re.findall("total_size=(\\d+)", text)

                    if len(frames):
                        elapse = int(frames[-1])
                    if len(size):
                        size = int(size[-1])
                        per = elapse * 100 / int(total_frames)
                        progress_str = "`[{0}{1}] {2}%\n`".format(
                            "".join(["●" for i in range(math.floor(per / 5))]),
                            "".join(["" for i in range(20 - math.floor(per / 5))]),
                            round(per, 2),
                        )
                        e_size = humanbytes(size)
                        await xxx.edit(progress_str + "\n" + "`" + e_size + "`")
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
            mmmm = await uploader(
                out,
                out,
                f_time,
                xxx,
                "Uploading " + out + "...",
            )
            if to_stream and "| stream" in to_stream:
                metadata = extractMetadata(createParser(out))
                duration = metadata.get('duration').seconds
                height = metadata.get('height')
                width = metadata.get('width')
                attributes=[DocumentAttributeVideo(duration=duration, w=width, h=height, supports_streaming=True)]
                await e.client.send_file(
                    e.chat_id,
                    mmmm,
                    thumb="resources/extras/ultroid.jpg",
                    caption=caption,
                    attributes=attributes,
                    force_document=False,
                    reply_to=e.reply_to_msg_id,
                )
            else:
                await e.client.send_file(
                    e.chat_id,
                    mmmm,
                    thumb="resources/extras/ultroid.jpg",
                    caption=caption,
                    force_document=True,
                    reply_to=e.reply_to_msg_id,
                )
            await xxx.delete()
            os.remove(out)
        else:
            await eod(e, "`Reply To Video File Only`")
    else:
        await eod(e, "`Reply To Video File Only`")


HELP.update({f"{__name__.split('.')[1]}": f"{__doc__.format(i=HNDLR)}"})
