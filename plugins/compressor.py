import os
import time

from . import *


@ultroid_cmd(pattern="compress ?(.*)")
async def _(e):
    xxx = await eor(e, "`Trying To Download...`")
    crf = e.pattern_match.group(1)
    if not crf:
        crf = 28
    if e.reply_to_msg_id:
        vido = await e.get_reply_message()
        if (
            vido.document.mime_type == "video/mp4"
            or vido.document.mime_type == "video/x-matroska"
        ):
            c_time = time.time()
            file = await downloader(
                "resources/downloads/" + vido.file.name,
                vido.media.document,
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
            cmds = [
                "ffmpeg -i",
                file.name,
                "-preset ultrafast -vcodec libx265 -crf",
                crf,
                file_name + "-compressed.mp4",
            ]
            await bash(*cmds)
            c_size = os.path.getsize(f"{file_name}-compressed.mp4")
            f_time = time.time()
            difff = time_formatter((f_time - d_time) * 1000)
            await xxx.edit(
                f"`Compressed {humanbytes(o_size)} to {humanbytes(c_size)} in {difff}\nTrying to Upload...`"
            )
            differ = 100 - ((c_size / o_size) * 100)
            caption = f"`File: ``{file_name}-compressed.mp4`\n"
            caption += f"`Original Size: ``{humanbytes(o_size)}`\n"
            caption += f"`Compressed Size: ``{humanbytes(c_size)}`\n"
            caption += f"`Compression Ratio: ``{differ:.2f}%`\n"
            caption += f"`Time Taken To Compress: ``{difff}`"
            mmmm = await uploader(
                f"{file_name}-compressed.mp4",
                f"{file_name}",
                f_time,
                xxx,
                "Uploading " + file_name + "...",
            )
            await e.client.send_file(
                e.chat_id,
                mmmm,
                thumb="resources/extras/new_thumb.jpg",
                caption=caption,
                force_document=True,
            )
            await xxx.delete()
