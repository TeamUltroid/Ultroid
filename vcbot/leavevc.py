# Ultroid - UserBot
# Copyright (C) 2021 TeamUltroid
#
# This file is a part of < https://github.com/TeamUltroid/Ultroid/ >
# PLease read the GNU Affero General Public License in
# <https://www.github.com/TeamUltroid/Ultroid/blob/main/LICENSE/>.

from . import *


@asst.on_message(filters.command(["leavevc",f"leavevc@{vcusername}"]) & filters.user(AUTH) & ~filters.edited)
async def leavehandler(_, message):
    spli = message.text.split(" ", maxsplit=1)
    try:
        chat = spli[1]
    except IndexError:
        chat = message.chat.id
    await eor(message, "`Left Vc...`")
    CallsClient.leave_group_call(chat)


@Client.on_message(filters.me & filters.command("leavevc", HNDLR) & ~filters.edited)
async def lhandler(_, message):
    await leavehandler(_, message)
