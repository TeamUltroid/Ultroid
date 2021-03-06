# Ultroid - UserBot
# Copyright (C) 2020 TeamUltroid
#
# This file is a part of < https://github.com/TeamUltroid/Ultroid/ >
# PLease read the GNU Affero General Public License in
# <https://www.github.com/TeamUltroid/Ultroid/blob/main/LICENSE/>.

"""
✘ Commands Available -

• `{i}tagall`
    Tag All Members of chat.

• `{i}tagadmins`
    Tag Admins of that chat.

• `{i}tagowner`
    Tag Owner of that chat
    
• `{i}tagbots`
    Tag Bots of that chat.

• `{i}tagrec`
    Tag recently Active Members.

• `{i}tagon`
    Tag online Members(work only if privacy off).

• `{i}tagoff`
    Tag Offline Members(work only if privacy off).
"""

from telethon.tl.types import ChannelParticipantAdmin as admin
from telethon.tl.types import ChannelParticipantCreator as owner
from telethon.tl.types import UserStatusOffline as off
from telethon.tl.types import UserStatusOnline as onn
from telethon.tl.types import UserStatusRecently as rec
from telethon.utils import get_display_name
import asyncio
from . import *


@ultroid_cmd(
    pattern="tag(on|off|all|bots|rec|admins|owner)?(.*)",
    groups_only=True,
)
async def _(e):
    await e.delete()
    okk = e.text
    lll = e.pattern_match.group(2)
    users = 0
    o = 0
    nn = 0
    rece = 0
    chat = await e.get_input_chat()
    if lll:
        xx = f"{lll}"
    else:
        xx = ""
    async for bb in e.client.iter_participants(chat):
        users = users + 1
        x = bb.status
        y = bb.participant
        if isinstance(x, onn):
            o = o + 1
            if "on" in okk:
                xx += f"\n[{get_display_name(bb)}](tg://user?id={bb.id})"
        if isinstance(x, off):
            nn = nn + 1
            if "off" in okk:
                if not (bb.bot or bb.deleted):
                    xx += f"\n[{get_display_name(bb)}](tg://user?id={bb.id})"
        if isinstance(x, rec):
            rece = rece + 1
            if "rec" in okk:
                if not (bb.bot or bb.deleted):
                    xx += f"\n[{get_display_name(bb)}](tg://user?id={bb.id})"
        if isinstance(y, owner):
            if "admin" or "owner" in okk:
                xx += f"\n꧁[{get_display_name(bb)}](tg://user?id={bb.id})꧂"
        if isinstance(y, admin):
            if "admin" in okk:
                if not bb.deleted:
                    xx += f"\n[{get_display_name(bb)}](tg://user?id={bb.id})"
        if "all" in okk:
            if not (bb.bot or bb.deleted):
                xx += f"\n[{get_display_name(bb)}](tg://user?id={bb.id})"
        if "bot" in okk:
            if bb.bot:
                xx += f"\n[{get_display_name(bb)}](tg://user?id={bb.id})"
    if len(xx) > 4096:
        limits = 4096
        ladybug = [xx[miracul:miracul+limits] for miracul in range(0, len(xx), limits)]#sh1vam
        for miracul in ladybug:
            chatnoir = f"**{lll}** \n{miracul}"
            await asyncio.sleep(0.7)
            await e.client.send_message(event.chat_id, chatnoir)
            
    else:
        await e.client.send_message(e.chat_id, xx)
        


HELP.update({f"{__name__.split('.')[1]}": f"{__doc__.format(i=HNDLR)}"})
