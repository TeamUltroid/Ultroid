# Ultroid - UserBot
# Copyright (C) 2021 TeamUltroid
#
# This file is a part of < https://github.com/TeamUltroid/Ultroid/ >
# PLease read the GNU Affero General Public License in
# <https://www.github.com/TeamUltroid/Ultroid/blob/main/LICENSE/>.

from . import *


@asst.on_message(
    filters.command(["listvc", f"listvc@{vcusername}"])
    & filters.user(VC_AUTHS())
    & ~filters.edited
)
async def list_handler(_, message):
    await message.reply_text(f"{CallsClient.active_calls}")


@Client.on_message(filters.me & filters.command("listvc", HNDLR) & ~filters.edited)
async def llhnf(_, message):
    await message.edit_text(f"{CallsClient.active_calls}")


@asst.on_message(filters.command("queue") & filters.user(VC_AUTHS()) & ~filters.edited)
async def queuee(_, e):
    mst = e.text.split(" ", maxsplit=1)
    try:
        chat = (await Client.get_chat(mst[1])).id
    except BaseException:
        chat = e.chat.id
    txt = list_queue(chat)
    if txt:
        return await asst.send_message(e.chat.id, txt)
    await asst.send_message(e.chat.id, "No Queue")
