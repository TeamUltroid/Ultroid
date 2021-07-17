# Ultroid - UserBot
# Copyright (C) 2021 TeamUltroid
#
# This file is a part of < https://github.com/TeamUltroid/Ultroid/ >
# PLease read the GNU Affero General Public License in
# <https://www.github.com/TeamUltroid/Ultroid/blob/main/LICENSE/>.

from . import *


@asst.on_message(
    filters.command(["clearqueue", f"clearqueue@{vcusername}"])
    & filters.user(VC_AUTHS())
    & ~filters.edited
)
async def clear_queue(_, message):
    try:
        QUEUE.pop(message.chat.id)
    except KeyError:
        return await eor(message, "Queue Not Found !")
    # Todo - Clear Remaining Songs
    return await eor(message, "Cleared Queue...")


@Client.on_message(
    filters.outgoing & filters.command("clearqueue", HNDLR) & ~filters.edited
)
async def clearqueue_vc(_, message):
    await clear_queue(_, message)


@asst.on_message(
    filters.command(["queue", f"queue@{vcusername}"])
    & filters.user(VC_AUTHS())
    & ~filters.edited
)
async def queuee(_, e):
    mst = e.text.split(" ", maxsplit=1)
    try:
        chat = (await Client.get_chat(mst[1])).id
    except BaseException:
        chat = e.chat.id
    txt = list_queue(chat)
    if txt:
        return await eor(e, txt)
    await eor(e, "No Queue Found !")


@Client.on_message(filters.outgoing & filters.command("queue", HNDLR) & ~filters.edited)
async def queue_vc(_, message):
    await queuee(_, message)
