# Ultroid - UserBot
# Copyright (C) 2020 TeamUltroid
#
# This file is a part of < https://github.com/TeamUltroid/Ultroid/ >
# PLease read the GNU Affero General Public License in
# <https://www.github.com/TeamUltroid/Ultroid/blob/main/LICENSE/>.

"""
✘ Commands Available -

• `{i}ul <path/to/file>`
    Upload file to telegram chat.

• `{i}dl <filename(optional)>`
    Reply to file to download.

"""

import asyncio
import time
from datetime import datetime as dt

from . import *


@ultroid_cmd(
    pattern="dl ?(.*)",
)
async def download(event):
    if not event.is_reply:
        return await eor(event, "`Reply to a Media Message`")
    xx = await eor(event, get_string("com_1"))
    kk = event.pattern_match.group(1)
    s = dt.now()
    k = time.time()
    if event.reply_to_msg_id:
        ok = await event.get_reply_message()
        if not ok.media:
            return await eod(xx, get_string("udl_1"), time=5)
        file = a.media.document
        filename = a.file.name
        try:
            with open(filename, "wb") as fk:
                await download_file(
                    client= event.client,
                    location=file,
                    out=fk,
                    progress_callback=lambda d, t: asyncio.get_event_loop().create_task(
                        progress(
                            d,
                            t,
                            xx,
                            c,
                            "Downloading...",
                            ),
                        ),
                    )
        except Exception as ex:
            return await eod(xx, "`" + str(ex) + "`", time=5)
    e = datetime.now()
    t = time_formatter(((e - s).seconds) * 1000)
    if t:
        await eor(xx, get_string("udl_2").format(o, t))
    else:
        await eor(xx, f"Downloaded `{o}` in `0 second(s)`")


@ultroid_cmd(
    pattern="ul ?(.*)",
)
async def download(event):
    xx = await eor(event, get_string("com_1"))
    kk = event.pattern_match.group(1)
    s = dt.now()
    tt = time.time()
    if not kk:
        return await eod(xx, get_string("udl_3"))
    else:
        try:
            x = await event.client.send_file(
                event.chat_id,
                kk,
                caption=kk,
                force_document=True,
                thumb="resources/extras/logo_rdm.png",
                progress_callback=lambda d, t: asyncio.get_event_loop().create_task(
                    progress(
                        d,
                        t,
                        xx,
                        tt,
                        "Uploading...",
                        file_name=kk,
                    ),
                ),
            )
        except ValueError as ve:
            return await eod(xx, str(ve))
        except BaseException:
            try:
                await ultroid_bot.send_message(event.chat_id, kk)
                return await kk.delete()
            except BaseException:
                pass
    e = datetime.now()
    t = time_formatter(((e - s).seconds) * 1000)
    try:
        await x.edit(f"`{kk}`\nTime Taken: `{t}`")
    except BaseException:
        pass
    if t:
        await eor(xx, f"Uploaded `{kk}` in `{t}`", time=5)
    else:
        await eor(xx, f"Uploaded `{kk}` in `0 second(s)`")


HELP.update({f"{__name__.split('.')[1]}": f"{__doc__.format(i=HNDLR)}"})
