# Ultroid - UserBot
# Copyright (C) 2020 TeamUltroid
#
# This file is a part of < https://github.com/TeamUltroid/Ultroid/ >
# PLease read the GNU Affero General Public License in
# <https://www.github.com/TeamUltroid/Ultroid/blob/main/LICENSE/>.


"""
✘ Commands Available

• `{i}ugdrive <reply/file name>`
    Reply to file to upload on Google Drive.
    Add file name to upload on Google Drive.

• `{i}drivesearch <file name>`
    Search file name on Google Drive and get link.

• `{i}udir <directory name>`
    Upload a directory on Google Drive.

• `{i}gfolder`
    Link to your Google Drive Folder.
    If added then all uploaded files will be placed here.
"""


import asyncio
import os
import time
from datetime import datetime

from telethon import events

from . import *

TOKEN_FILE = "resources/auths/auth_token.txt"


@ultroid_cmd(
    pattern="ugdrive ?(.*)",
)
async def _(event):
    mone = await eor(event, get_string("com_1"))
    if not os.path.exists(TOKEN_FILE):
        return await eod(mone, get_string("gdrive_6").format(Var.BOT_USERNAME))
    input_str = event.pattern_match.group(1)
    required_file_name = None
    start = datetime.now()
    dddd = time.time()
    if event.reply_to_msg_id and not input_str:
        reply_message = await event.get_reply_message()
        try:
            downloaded_file_name = await event.client.download_media(
                reply_message,
                "resources/downloads",
                progress_callback=lambda d, t: asyncio.get_event_loop().create_task(
                    progress(
                        d,
                        t,
                        mone,
                        dddd,
                        "Downloading...",
                    ),
                ),
            )
        except Exception as e:
            return await eod(mone, str(e), time=10)
        end = datetime.now()
        ms = (end - start).seconds
        required_file_name = downloaded_file_name
        await mone.edit(
            "Downloaded to `{}` in {} seconds.".format(downloaded_file_name, ms)
        )
    elif input_str:
        input_str = input_str.strip()
        if os.path.exists(input_str):
            end = datetime.now()
            ms = (end - start).seconds
            required_file_name = input_str
            await mone.edit("Found `{}` in {} seconds.".format(input_str, ms))
        else:
            return await eod(
                mone, "File Not found in local server. Give me a file path :((", time=5
            )
    if required_file_name:
        http = authorize(TOKEN_FILE, None)
        file_name, mime_type = file_ops(required_file_name)
        try:
            g_drive_link = await upload_file(
                http,
                required_file_name,
                file_name,
                mime_type,
                mone,
                Redis("GDRIVE_FOLDER_ID"),
            )
            await mone.edit(get_string("gdrive_7").format(file_name, g_drive_link))
        except Exception as e:
            await mone.edit(f"Exception occurred while uploading to gDrive {e}")
    else:
        return await eod(mone, "`File Not found in local server.`", time=10)


@ultroid_cmd(
    pattern="drivesearch ?(.*)",
)
async def sch(event):
    if not os.path.exists(TOKEN_FILE):
        return await eod(event, get_string("gdrive_6").format(Var.BOT_USERNAME))
    http = authorize(TOKEN_FILE, None)
    input_str = event.pattern_match.group(1).strip()
    a = await eor(event, "Searching for {} in G-Drive.".format(input_str))
    if Redis("GDRIVE_FOLDER_ID") is not None:
        query = "'{}' in parents and (title contains '{}')".format(
            Redis("GDRIVE_FOLDER_ID"), input_str
        )
    else:
        query = "title contains '{}'".format(input_str)
    try:
        msg = await gsearch(http, query, input_str)
        return await a.edit(str(msg))
    except Exception as ex:
        return await a.edit(str(ex))


@ultroid_cmd(
    pattern="udir ?(.*)",
)
async def _(event):
    if not os.path.exists(TOKEN_FILE):
        return await eod(mone, get_string("gdrive_6").format(Var.BOT_USERNAME))
    input_str = event.pattern_match.group(1)
    if os.path.isdir(input_str):
        http = authorize(TOKEN_FILE, None)
        a = await eor(event, "Uploading `{}` to G-Drive...".format(input_str))
        dir_id = await create_directory(
            http,
            os.path.basename(os.path.abspath(input_str)),
            Redis("GDRIVE_FOLDER_ID"),
        )
        await DoTeskWithDir(http, input_str, event, dir_id)
        dir_link = "https://drive.google.com/folderview?id={}".format(dir_id)
        await eod(a, get_string("gdrive_7").format(input_str, dir_link))
    else:
        return await eod(event, f"Directory {input_str} does not seem to exist", time=5)


@ultroid_cmd(
    pattern="gfolder$",
)
async def _(event):
    if Redis("GDRIVE_FOLDER_ID"):
        folder_link = "https://drive.google.com/folderview?id=" + Redis(
            "GDRIVE_FOLDER_ID"
        )
        await eod(event, "`Here is Your G-Drive Folder link : `\n" + folder_link)
    else:
        await eod(event, "Set GDRIVE_FOLDER_ID with value of your folder id")


HELP.update({f"{__name__.split('.')[1]}": f"{__doc__.format(i=HNDLR)}"})
