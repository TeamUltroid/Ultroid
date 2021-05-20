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

import os
import time
from datetime import datetime as dt

from . import *


@ultroid_cmd(pattern="compress ?(.*)")
async def _(e):
    crf = e.pattern_match.group(1)
    if not crf:
        crf = 28
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
            await xxx.edit(
                f"`Downloaded {file.name} of {humanbytes(o_size)} in {diff}.\nNow Compressing...`"
            )
            cmd = "ffmpeg -i "+"""{file.name}"""+"-preset ultrafast -c:v -vcodec libx265 -crf "+crf+"-map 0:v -c:a aac -map 0:a -c:s copy -map 0:s? "+file_name+"_compressed.mp4"
            await bash(cmd)
            c_size = os.path.getsize(f"{file_name}_compressed.mp4")
            f_time = time.time()
            difff = time_formatter((f_time - d_time) * 1000)
            await xxx.edit(
                f"`Compressed {humanbytes(o_size)} to {humanbytes(c_size)} in {difff}\nTrying to Upload...`"
            )
            differ = 100 - ((c_size / o_size) * 100)
            caption = f"`File: ``{file_name}_compressed.mp4`\n"
            caption += f"`Original Size: ``{humanbytes(o_size)}`\n"
            caption += f"`Compressed Size: ``{humanbytes(c_size)}`\n"
            caption += f"`Compression Ratio: ``{differ:.2f}%`\n"
            caption += f"`Time Taken To Compress: ``{difff}`"
            mmmm = await uploader(
                f"{file_name}_compressed.mp4",
                f"{file_name}",
                f_time,
                xxx,
                "Uploading " + file_name + "...",
            )
            await e.client.send_file(
                e.chat_id,
                mmmm,
                thumb="resources/extras/ultroid.jpg",
                caption=caption,
                force_document=True,
            )
            await xxx.delete()
        else:
            await eod(e, "`Reply To Video File Only`")
    else:
        await eod(e, "`Reply To Video File Only`")


HELP.update({f"{__name__.split('.')[1]}": f"{__doc__.format(i=HNDLR)}"})
