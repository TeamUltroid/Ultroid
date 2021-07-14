# Ultroid - UserBot
# Copyright (C) 2021 TeamUltroid
#
# This file is a part of < https://github.com/TeamUltroid/Ultroid/ >
# PLease read the GNU Affero General Public License in
# <https://www.github.com/TeamUltroid/Ultroid/blob/main/LICENSE/>.

from . import *

# from .play import streamhandler


@asst.on_message(filters.command("skipvc") & filters.user(VC_AUTHS()) & ~filters.edited)
async def skiplife(_, message):
    mst = message.text.split(" ", maxsplit=1)
    try:
        chat = mst[1]
    except BaseException:
        chat = message.chat.id
    CallsClient.pause_stream(chat)
    # await streamhandler(_, message)
