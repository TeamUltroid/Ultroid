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

• `{i}save <filename.ext>`
    Reply to a text msg to save it in a file.

• `{i}open`
    Reply to a file to reveal it's text.
"""

import asyncio
import os
import time
from datetime import datetime as dt

from . import *

opn = []


@ultroid_cmd(
    pattern="dl ?(.*)",
)
async def download(event):
    xx = await eor(event, get_string("com_1"))
    kk = event.pattern_match.group(1)
    s = dt.now()
    k = time.time()
    if event.reply_to_msg_id:
        ok = await event.get_reply_message()
        if not ok.media:
            return await eod(xx, get_string("udl_1"), time=5)
        else:
            if not kk:
                d = "resources/downloads/"
                o = await event.client.download_media(
                    ok,
                    d,
                    progress_callback=lambda d, t: asyncio.get_event_loop().create_task(
                        progress(
                            d,
                            t,
                            xx,
                            k,
                            "Downloading...",
                        )
                    ),
                )
            else:
                d = f"resources/downloads/{kk}"
                o = await event.client.download_media(
                    ok,
                    d,
                    progress_callback=lambda d, t: asyncio.get_event_loop().create_task(
                        progress(
                            d,
                            t,
                            xx,
                            k,
                            "Downloading...",
                            file_name=d,
                        )
                    ),
                )
    e = datetime.now()
    t = time_formatter(((e - s).seconds) * 1000)
    await eod(xx, get_string("udl_2").format(o, t))


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
                progress_callback=lambda d, t: asyncio.get_event_loop().create_task(
                    progress(
                        d,
                        t,
                        xx,
                        tt,
                        "Uploading...",
                        file_name=kk,
                    )
                ),
            )
        except ValueError as ve:
            return await eod(xx, str(ve))
    e = datetime.now()
    t = time_formatter(((e - s).seconds) * 1000)
    try:
        await x.edit(f"`{kk}`\nTime Taken: `{t}`")
    except BaseException:
        pass
    await eod(xx, f"Uploaded `{kk}` in `{t}`", time=5)


@ultroid_cmd(
    pattern="save",
)
async def _(event):
    input_str = event.text[6:]
    xx = await eor(event, get_string("com_1"))
    if event.reply_to_msg_id:
        a = await event.get_reply_message()
        if not a.message:
            return await xx.edit("`Reply to a message`")
        else:
            b = open(input_str, "w")
            b.write(str(a.message))
            b.close()
            await xx.edit(f"**Packing into** `{input_str}`")
            await asyncio.sleep(2)
            await xx.edit(f"**Uploading** `{input_str}`")
            await asyncio.sleep(2)
            await event.client.send_file(event.chat_id, input_str)
            await xx.delete()
            os.remove(input_str)


@ultroid_cmd(
    pattern="open$",
)
async def _(event):
    xx = await eor(event, get_string("com_1"))
    if event.reply_to_msg_id:
        a = await event.get_reply_message()
        if a.media:
            b = await a.download_media()
            c = open(b, "r")
            d = c.read()
            c.close()
            n = 4096
            for bkl in range(0, len(d), n):
                opn.append(d[bkl : bkl + n])
            for bc in opn:
                await event.client.send_message(
                    event.chat_id,
                    f"```{bc}```",
                    reply_to=event.reply_to_msg_id,
                )
            await event.delete()
            opn.clear()
            os.remove(b)
            await xx.delete()
        else:
            return await eod(xx, "`Reply to a readable file`", time=10)
    else:
        return await eod(xx, "`Reply to a readable file`", time=10)


HELP.update({f"{__name__.split('.')[1]}": f"{__doc__.format(i=HNDLR)}"})
