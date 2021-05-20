# Ultroid - UserBot
# Copyright (C) 2020 TeamUltroid
#
# This file is a part of < https://github.com/TeamUltroid/Ultroid/ >
# PLease read the GNU Affero General Public License in
# <https://www.github.com/TeamUltroid/Ultroid/blob/main/LICENSE/>.

"""
✘ Commands Available -

"""

import os
import time
from datetime import datetime as dt

from . import *


@ultroid_cmd(pattern="compress")
async def _(e):
    xxx = await eor(e, "`Trying To Download...`")
    vido = await e.get_reply_message()
    if video and video.media:
        if "video" in mediainfo(vido.media):
            if hasattr(vido.media, "document"):
                vfile = vido.media.document
            else:
                vfile = vido.media
            name = vido.file.name
            if not name:
                name = "video_" + dt.now().isoformat("_", "seconds") + ".mp4"
            c_time = time.time()
            file = await downloader(
                "resources/downloads/" + name,
                vfile,
                xxx,
                c_time,
                "Downloading " + vido.file.name + "...",
            )
            o_size = os.path.getsize(file.name)
            d_time = time.time()
            diff = time_formatter((d_time - c_time) * 1000)
            file_name = (file.name).split("/")[-1]
            await xxx.edit(
                f"`Downloaded {file.name} of {humanbytes(o_size)} in {diff}.\nNow Compressing...`"
            )
            await bash(
                f'ffmpeg -i "{file.name}" -preset ultrafast -c:v libx265 -crf 27 -map 0:v -c:a aac -map 0:a -c:s copy -map 0:s? "{file_name}_compressed.mkv"'
            )
            c_size = os.path.getsize(f"{file_name}-compressed.mkv")
            f_time = time.time()
            difff = time_formatter((f_time - d_time) * 1000)
            await xxx.edit(
                f"`Compressed {humanbytes(o_size)} to {humanbytes(c_size)} in {difff}\nTrying to Upload...`"
            )
            differ = 100 - ((c_size / o_size) * 100)
            caption = f"`File: ``{file_name}-compressed.mkv`\n"
            caption += f"`Original Size: ``{humanbytes(o_size)}`\n"
            caption += f"`Compressed Size: ``{humanbytes(c_size)}`\n"
            caption += f"`Compression Ratio: ``{differ:.2f}%`\n"
            caption += f"`Time Taken To Compress: ``{difff}`"
            mmmm = await uploader(
                f"{file_name}_compressed.mkv",
                f"{file_name}_compressed.mkv",
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


HELP.update({f"{__name__.split('.')[1]}": f"{__doc__.format(i=HNDLR)}"})
