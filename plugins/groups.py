# Ultroid - UserBot
# Copyright (C) 2020 TeamUltroid
#
# This file is a part of < https://github.com/TeamUltroid/Ultroid/ >
# PLease read the GNU Affero General Public License in
# <https://www.github.com/TeamUltroid/Ultroid/blob/main/LICENSE/>.

"""
✘ Commands Available -

• `{i}unbanall`
    Unban all Members of a group.

• `{i}rmusers`
    Remove users specifically.
"""


from telethon import events
from telethon.tl import functions, types
from telethon.tl.types import (ChannelParticipantsKicked, ChatBannedRights,
                               UserStatusEmpty, UserStatusLastMonth,
                               UserStatusLastWeek, UserStatusOffline,
                               UserStatusOnline, UserStatusRecently)

from . import *


@ultroid_cmd(
    pattern="unbanall$",
    groups_only=True,
)
async def _(event):
    xx = await eor(event, "Searching Participant Lists.")
    p = 0
    (await event.get_chat()).title
    async for i in event.client.iter_participants(
        event.chat_id, filter=ChannelParticipantsKicked, aggressive=True
    ):
        try:
            await event.client.edit_permissions(event.chat_id, i, view_messages=True)
            p += 1
        except:
            pass
    await eod(xx, "{title}: {p} unbanned")


@ultroid_cmd(
    pattern="rmusers ?(.*)",
    groups_only=True,
)
async def _(event):
    xx = await eor(event, "Searching Participant Lists.")
    input_str = event.pattern_match.group(1)
    if input_str:
        chat = await event.get_chat()
        if not (chat.admin_rights or chat.creator):
            return await eod(xx, "`You aren't an admin here!`", time=5)
    p = 0
    b = 0
    c = 0
    d = 0
    m = 0
    n = 0
    y = 0
    w = 0
    o = 0
    q = 0
    r = 0
    async for i in event.client.iter_participants(event.chat_id):
        p += 1
        rights = ChatBannedRights(
            until_date=None,
            view_messages=True,
        )
        if isinstance(i.status, UserStatusEmpty):
            y += 1
            if "empty" in input_str:
                try:
                    await event.client(
                        functions.channels.EditBannedRequest(event.chat_id, i, rights)
                    )
                    c += 1
                    y -= 1
                except:
                    pass
        if isinstance(i.status, UserStatusLastMonth):
            m += 1
            if "month" in input_str:
                try:
                    await event.client(
                        functions.channels.EditBannedRequest(event.chat_id, i, rights)
                    )
                    c += 1
                    m -= 1
                except:
                    pass
        if isinstance(i.status, UserStatusLastWeek):
            w += 1
            if "week" in input_str:
                try:
                    await event.client(
                        functions.channels.EditBannedRequest(event.chat_id, i, rights)
                    )
                    c += 1
                    w -= 1
                except:
                    pass
        if isinstance(i.status, UserStatusOffline):
            o += 1
            if "offline" in input_str:
                try:
                    await event.client(
                        functions.channels.EditBannedRequest(event.chat_id, i, rights)
                    )
                    c += 1
                    o -= 1
                except:
                    pass
        if isinstance(i.status, UserStatusOnline):
            q += 1
            if "online" in input_str:
                try:
                    await event.client(
                        functions.channels.EditBannedRequest(event.chat_id, i, rights)
                    )
                    c += 1
                    q -= 1
                except:
                    pass
        if isinstance(i.status, UserStatusRecently):
            r += 1
            if "recently" in input_str:
                try:
                    await event.client(
                        functions.channels.EditBannedRequest(event.chat_id, i, rights)
                    )
                    c += 1
                    r -= 1
                except:
                    pass
        if i.bot:
            b += 1
            if "bot" in input_str:
                try:
                    await event.client(
                        functions.channels.EditBannedRequest(event.chat_id, i, rights)
                    )
                    c += 1
                    b -= 1
                except:
                    pass
        elif i.deleted:
            d += 1
            if "deleted" in input_str:
                try:
                    await event.client(
                        functions.channels.EditBannedRequest(event.chat_id, i, rights)
                    )
                    c += 1
                    d -= 1
                except:
                    pass
        elif i.status is None:
            n += 1
            if "none" in input_str:
                try:
                    await event.client(
                        functions.channels.EditBannedRequest(event.chat_id, i, rights)
                    )
                    c += 1
                    n -= 1
                except:
                    pass
    required_string = ""
    if input_str:
        required_string += f"**>> Kicked** `{c} / {p}` **users**\n\n"
        required_string += f"  **••Deleted Accounts••** `{d}`\n"
        required_string += f"  **••UserStatusEmpty••** `{y}`\n"
        required_string += f"  **••UserStatusLastMonth••** `{m}`\n"
        required_string += f"  **••UserStatusLastWeek••** `{w}`\n"
        required_string += f"  **••UserStatusOffline••** `{o}`\n"
        required_string += f"  **••UserStatusOnline••** `{q}`\n"
        required_string += f"  **••UserStatusRecently••** `{r}`\n"
        required_string += f"  **••Bots••** `{b}`\n"
        required_string += f"  **••None••** `{n}`\n"
    else:
        required_string += f"**>> Total** `{p}` **users**\n\n"
        required_string += f"  `{HNDLR}rmusers deleted`  **••**  `{d}`\n"
        required_string += f"  `{HNDLR}rmusers empty`  **••**  `{y}`\n"
        required_string += f"  `{HNDLR}rmusers month`  **••**  `{m}`\n"
        required_string += f"  `{HNDLR}rmusers week`  **••**  `{w}`\n"
        required_string += f"  `{HNDLR}rmusers offline`  **••**  `{o}`\n"
        required_string += f"  `{HNDLR}rmusers online`  **••**  `{q}`\n"
        required_string += f"  `{HNDLR}rmusers recently`  **••**  `{r}`\n"
        required_string += f"  `{HNDLR}rmusers bot`  **••**  `{b}`\n"
        required_string += f"  `{HNDLR}rmusers none`  **••**  `{n}`\n\n"
        required_string += f"**••Empty**  `Name with deleted Account`\n"
        required_string += f"**••None**  `Last Seen A Long Time Ago`\n"
    await eod(xx, required_string)


HELP.update({f"{__name__.split('.')[1]}": f"{__doc__.format(i=HNDLR)}"})
