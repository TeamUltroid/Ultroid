# Ultroid - UserBot
# Copyright (C) 2020 TeamUltroid
#
# This file is a part of < https://github.com/TeamUltroid/Ultroid/ >
# PLease read the GNU Affero General Public License in
# <https://www.github.com/TeamUltroid/Ultroid/blob/main/LICENSE/>.

"""
✘ Commands Available

• `{i}unzip <reply to zip file>`
    unzip the replied file.
"""

import asyncio
import os
import time
import zipfile

from . import *


@ultroid_cmd(pattern="unzip$")
async def _(ult):
    if not ult.is_reply:
        return await eor(ult, "`Reply to a Zipfile..`")
    gt = await ult.get_reply_message()
    msg = await eor(ult, "`Processing...`")
    if not (
        gt.media
        and gt.media.document
        and gt.media.document.mime_type == "application/zip"
    ):
        return await msg.edit("`Reply to a Zipfile...`")
    k = time.time()
    d = "resources/downloads/"
    dnl = await ultroid_bot.download_media(
        gt,
        d,
        progress_callback=lambda d, t: asyncio.get_event_loop().create_task(
            progress(d, t, msg, k, "Downloading to my Storage..."),
        ),
    )
    place = "resources/downloads/extracted/"
    with zipfile.ZipFile(dnl, "r") as zip_ref:
        zip_ref.extractall(place)
    filename = sorted(get_lst_of_files(place, []))
    await msg.edit("Unzipping now")
    THUMB = udB.get("THUMB_URL")
    Enum = 0
    Elist = "**Errors Occured while Unzip**\n\n"
    for single_file in filename:
        if os.path.exists(single_file):
            caption_rts = os.path.basename(single_file)
            try:
                await ultroid_bot.send_file(
                    ult.chat_id,
                    single_file,
                    thumb=THUMB,
                    caption=f"**File Name :** {caption_rts}",
                    force_document=True,
                    reply_to=ult.message.id,
                )
            except Exception as e:
                Enum += 1
                Elist += f"{Enum}. {caption_rts}\n- __{str(e)}__\n"
            os.remove(single_file)
    os.remove(dnl)
    await msg.edit(f"**Unzipped `{len(filename)-Enum}/{len(filename)}` Files**")
    if Enum > 0:
        if len(Elist) < 4096:
            await ultroid_bot.send_message(int(udB.get("LOG_CHANNEL")), Elist)
        else:
            file = open("UnzipError.txt", "w").write(Elist)
            file.close()
            await ultroid_bot.send_message(
                int(udB.get("LOG_CHANNEL")),
                "UnzipError.txt",
                caption=f"`Error Occured on Unzip cmd",
            )
            os.remove("UnzipError.txt")


def get_lst_of_files(input_directory, output_lst):
    filesinfolder = os.listdir(input_directory)
    for file_name in filesinfolder:
        current_file_name = os.path.join(input_directory, file_name)
        if os.path.isdir(current_file_name):
            return get_lst_of_files(current_file_name, output_lst)
        output_lst.append(current_file_name)
    return output_lst


HELP.update({f"{__name__.split('.')[1]}": f"{__doc__.format(i=HNDLR)}"})
