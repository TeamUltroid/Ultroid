# Ultroid - UserBot
# Copyright (C) 2021 TeamUltroid
#
# This file is a part of < https://github.com/TeamUltroid/Ultroid/ >
# PLease read the GNU Affero General Public License in
# <https://www.github.com/TeamUltroid/Ultroid/blob/main/LICENSE/>.

from telethon import Button

from . import *


@vc_asst("vchelp")
async def helper(event):
    res = await event.client.inline_query(asst.me.username, "vchelp")
    try:
        await res[0].click(event.chat_id)
    except Exception as e:
        await eor(event, e)


@in_pattern("vchelp")
async def wiqhshd(e):
    builder = e.builder
    res = [
        await builder.article(
            title="Vc Help",
            text="**VCBot Help Menu**\n\n",
            buttons=Button.inline("Voice Chat Help", data="vc_helper"),
        )
    ]
    await e.answer(res)
