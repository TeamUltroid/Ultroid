# Ultroid - UserBot
# Copyright (C) 2020 TeamUltroid
#
# This file is a part of < https://github.com/TeamUltroid/Ultroid/ >
# PLease read the GNU Affero General Public License in
# <https://www.github.com/TeamUltroid/Ultroid/blob/main/LICENSE/>.

"""

✘ Commands Available -

•`{i}glitch <replt to media>`
    gives a glitchy gif.

"""
import asyncio
import os

from . import *



@ultroid_cmd(pattern="glitch$")
async def _(e):
    reply = await e.get_reply_message()
    if not reply.media:
        return await eor(e, "reply to any media")
    xx = await eor(e, "`Gliching...`")
    ok = await bot.download_media(reply.media)
    cmd = f"glitch_me gif --line_count 200 -f 10 -d 50 '{ok}' ult.gif"
    process = await asyncio.create_subprocess_shell(
        cmd,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )
    stdout, stderr = await process.communicate()
    await ultroid_bot.send_file(
        e.chat_id, "ult.gif", force_document=False, reply_to=reply
    )
    await xx.delete()
    os.remove(ok)
    os.remove("ult.gif")


HELP.update({f"{__name__.split('.')[1]}": f"{__doc__.format(i=HNDLR)}"})
