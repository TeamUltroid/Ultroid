# Ultroid - UserBot
# Copyright (C) 2021 TeamUltroid
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

• `{i}listdrive`
    List all GDrive files.

• `{i}gfolder`
    Link to your Google Drive Folder.
    If added then all uploaded files will be placed here.
"""

import os
import time
from datetime import datetime

from pyUltroid.functions.gdrive import (
    DoTeskWithDir,
    authorize,
    create_directory,
    file_ops,
    gsearch,
    list_files,
    upload_file,
)

from . import Redis, asst, downloader, eod, eor, get_string, ultroid_cmd

TOKEN_FILE = "resources/auths/auth_token.txt"


@ultroid_cmd(
    pattern="listdrive$",
)
async def files(event):
    if not os.path.exists(TOKEN_FILE):
        return await eor(event, get_string("gdrive_6").format(asst.me.username), time=5)
    http = authorize(TOKEN_FILE, None)
    await eor(event, list_files(http))


@ultroid_cmd(
    pattern="ugdrive ?(.*)",
)
async def _(event):
    mone = await eor(event, get_string("com_1"))
    if not os.path.exists(TOKEN_FILE):
        return await eor(mone, get_string("gdrive_6").format(asst.me.username), time=5)
    input_str = event.pattern_match.group(1)
    required_file_name = None
    start = datetime.now()
    dddd = time.time()
    if event.reply_to_msg_id and not input_str:
        reply_message = await event.get_reply_message()
        try:
            downloaded_file_name = await downloader(
                "resources/downloads/" + reply_message.file.name,
                reply_message.media.document,
                mone,
                dddd,
                get_string("com_5"),
            )
            filename = downloaded_file_name.name
        except TypeError:
            filename = await event.client.download_media(
                "resources/downloads", reply_message.media
            )
        except Exception as e:
            return await eor(mone, str(e), time=10)
        end = datetime.now()
        ms = (end - start).seconds
        required_file_name = filename
        await mone.edit(
            f"Downloaded to `{filename}` in {ms} seconds.",
        )
    elif input_str:
        input_str = input_str.strip()
        if os.path.exists(input_str):
            end = datetime.now()
            ms = (end - start).seconds
            required_file_name = input_str
            await mone.edit(f"Found `{required_file_name}` in {ms} seconds.")
        else:
            return await eod(
                mone,
                "File Not found in local server. Give me a file path :((",
                time=5,
            )
    if not required_file_name:
        return await eor(mone, "`File Not found in local server.`", time=10)

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


@ultroid_cmd(
    pattern="drivesearch ?(.*)",
)
async def sch(event):
    if not os.path.exists(TOKEN_FILE):
        return await eor(event, get_string("gdrive_6").format(asst.me.username), time=5)
    http = authorize(TOKEN_FILE, None)
    input_str = event.pattern_match.group(1).strip()
    a = await eor(event, f"Searching for {input_str} in G-Drive.")
    if Redis("GDRIVE_FOLDER_ID") is not None:
        query = "'{}' in parents and (title contains '{}')".format(
            Redis("GDRIVE_FOLDER_ID"),
            input_str,
        )
    else:
        query = f"title contains '{input_str}'"
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
        return await eor(event, get_string("gdrive_6").format(asst.me.username), time=5)
    input_str = event.pattern_match.group(1)
    if not os.path.isdir(input_str):
        return await eor(event, f"Directory {input_str} does not seem to exist", time=5)

    http = authorize(TOKEN_FILE, None)
    a = await eor(event, f"Uploading `{input_str}` to G-Drive...")
    dir_id = await create_directory(
        http,
        os.path.basename(os.path.abspath(input_str)),
        Redis("GDRIVE_FOLDER_ID"),
    )
    await DoTeskWithDir(http, input_str, event, dir_id)
    dir_link = f"https://drive.google.com/folderview?id={dir_id}"
    await eor(a, get_string("gdrive_7").format(input_str, dir_link), time=5)


@ultroid_cmd(
    pattern="gfolder$",
)
async def _(event):
    if Redis("GDRIVE_FOLDER_ID"):
        folder_link = "https://drive.google.com/folderview?id=" + Redis(
            "GDRIVE_FOLDER_ID",
        )
        await eor(
            event, "`Here is Your G-Drive Folder link : `\n" + folder_link, time=5
        )
    else:
        await eor(event, "Set GDRIVE_FOLDER_ID with value of your folder id", time=5)
