# Ultroid - UserBot
# Copyright (C) 2021 TeamUltroid
#
# This file is a part of < https://github.com/TeamUltroid/Ultroid/ >
# PLease read the GNU Affero General Public License in
# <https://www.github.com/TeamUltroid/Ultroid/blob/main/LICENSE/>.

"""
✘ Commands Available -

•`{i}sample <duration in seconds>`
   Creates Short sample of video..

• `{i}vshots <number of shots>`
   Creates screenshot of video..

• `{i}vtrim <start time> - <end time> in seconds`
    Crop a Lengthy video..
"""

import glob
import os
import time
from datetime import datetime as dt

from hachoir.metadata import extractMetadata
from hachoir.parser import createParser
from telethon.tl.types import DocumentAttributeVideo

from . import *


@ultroid_cmd(pattern="sample ?(.*)")
async def gen_sample(e):
    sec = e.pattern_match.group(1)
    stime = 35
    if sec and sec.isdigit():
        stime = int(sec)
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
        out = file_name.replace(file_name.split(".")[-1], "_sample.mkv")
        xxx = await xxx.edit(
            f"Downloaded `{file.name}` of `{humanbytes(o_size)}` in `{diff}`.\n\nNow Generating Sample of `{stime}` seconds..."
        )
        ss, dd = duration_s(file.name, stime)
        cmd = f'ffmpeg -i "{file.name}" -preset ultrafast -ss {ss} -to {dd} -codec copy -map 0 "{out}" -y'
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
        duration = metadata.get("duration").seconds
        hi, _ = await bash(f'mediainfo "{out}" | grep "Height"')
        wi, _ = await bash(f'mediainfo "{out}" | grep "Width"')
        height = int(hi.split(":")[1].split("pixels")[0].replace(" ", ""))
        width = int(wi.split(":")[1].split("pixels")[0].replace(" ", ""))
        attributes = [
            DocumentAttributeVideo(
                duration=duration, w=width, h=height, supports_streaming=True
            )
        ]
        caption = f"A Sample Video Of `{stime}` seconds"
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
        await eor(e, "`Reply To Video File Only`", time=5)


@ultroid_cmd(pattern="vshots ?(.*)")
async def gen_shots(e):
    ss = e.pattern_match.group(1)
    shot = 5
    if ss and ss.isdigit():
        shot = int(ss)
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
        xxx = await xxx.edit(
            f"Downloaded `{file.name}` of `{humanbytes(o_size)}` in `{diff}`.\n\nNow Generating `{shot}` screenshots..."
        )
        await bash("rm -rf ss && mkdir ss")
        cmd = f'ffmpeg -i "{file.name}" -vf fps=0.009 -vframes {shot} "ss/pic%01d.png"'
        await bash(cmd)
        os.remove(file.name)
        pic = glob.glob("ss/*")
        text = f"Uploaded {len(pic)}/{shot} screenshots"
        if not pic:
            text = "`Failed to Take Screenshots..`"
            pic = None
        await e.client.send_message(e.chat_id, text, file=pic)
        await bash("rm -rf ss")
        await xxx.delete()


@ultroid_cmd(pattern="vtrim ?(.*)")
async def gen_sample(e):
    sec = e.pattern_match.group(1)
    if not sec or "-" not in sec:
        return await eod(e, "`Give time in format to trim`")
    a, b = sec.split("-")
    if int(a) >= int(b):
        return await eod(e, "`Incorrect Data`")
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
        out = file_name.replace(file_name.split(".")[-1], "_trimmed.mkv")
        if int(b) > int(genss(file.name)):
            os.remove(file.name)
            return await eod(xxx, "`Wrong trim duration`")
        ss, dd = stdr(int(a)), stdr(int(b))
        xxx = await xxx.edit(
            f"Downloaded `{file.name}` of `{humanbytes(o_size)}` in `{diff}`.\n\nNow Trimming Video from `{ss}` to `{dd}`..."
        )
        cmd = f'ffmpeg -i "{file.name}" -preset ultrafast -ss {ss} -to {dd} -codec copy -map 0 "{out}" -y'
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
        duration = metadata.get("duration").seconds
        hi, _ = await bash(f'mediainfo "{out}" | grep "Height"')
        wi, _ = await bash(f'mediainfo "{out}" | grep "Width"')
        height = int(hi.split(":")[1].split("pixels")[0].replace(" ", ""))
        width = int(wi.split(":")[1].split("pixels")[0].replace(" ", ""))
        attributes = [
            DocumentAttributeVideo(
                duration=duration, w=width, h=height, supports_streaming=True
            )
        ]
        caption = f"Trimmed Video From `{ss}` To `{dd}`"
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
        await eor(e, "`Reply To Video File Only`", time=5)
