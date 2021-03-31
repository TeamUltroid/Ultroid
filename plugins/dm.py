# Ultroid - UserBot
# Copyright (C) 2020 TeamUltroid
#
# This file is a part of < https://github.com/TeamUltroid/Ultroid/ >
# PLease read the GNU Affero General Public License in
# <https://www.github.com/TeamUltroid/Ultroid/blob/main/LICENSE/>.
"""
✘ Commands Available -

• `{i}dm <username/id> <reply/type>`
    Direct Message the User.
"""

from . import *


@ultroid_cmd(pattern="dm ?(.*)")
async def dm(e):
    d = e.pattern_match.group(1)
    c = d.split(" ")
    chat_id = c[0]
    try:
        chat_id = int(chat_id)
    except BaseException:
        pass
    msg = ""
    masg = await e.get_reply_message()
    if e.reply_to_msg_id:
        await ultroid_bot.send_message(chat_id, masg)
        await eod(e, "`⚜️Message Delivered!`", time=4)
    for i in c[1:]:
        msg += i + " "
    if msg == "":
        return
    try:
        await ultroid_bot.send_message(chat_id, msg)
        await eod(e, "`⚜️Message Delivered!⚜️`", time=4)
    except BaseException:
        await eod(
            e,
            "{i}dm (username/id) (text)\n\n{i}dm (username/id) <reply to msg>",
            time=4,
        )


HELP.update({f"{__name__.split('.')[1]}": f"{__doc__.format(i=HNDLR)}"})
