# Ultroid - UserBot
# Copyright (C) 2021-2022 TeamUltroid
#
# This file is a part of < https://github.com/TeamUltroid/Ultroid/ >
# PLease read the GNU Affero General Public License in
# <https://www.github.com/TeamUltroid/Ultroid/blob/main/LICENSE/>.

"""
✘ Commands Available -

• `{i}startvc`
    Start Group Call in a group.

• `{i}stopvc`
    Stop Group Call in a group.

• `{i}vctitle <title>`
    Change the title Group call.

• `{i}vcinvite`
    Invite all members of group in Group Call.
    (You must be joined)
"""


import contextlib
from telethon.tl.functions.channels import GetFullChannelRequest as getchat
from telethon.tl.functions.phone import CreateGroupCallRequest as startvc
from telethon.tl.functions.phone import DiscardGroupCallRequest as stopvc
from telethon.tl.functions.phone import EditGroupCallTitleRequest as settitle
from telethon.tl.functions.phone import GetGroupCallRequest as getvc
from telethon.tl.functions.phone import InviteToGroupCallRequest as invitetovc

from .. import get_string, ultroid_cmd, LOGS


async def get_call(event):
    mm = await event.client(getchat(event.chat_id))
    if mm.full_chat.call:
        xx = await event.client(getvc(mm.full_chat.call, limit=1))
        return xx.call


def user_list(l, n):
    for i in range(0, len(l), n):
        yield l[i : i + n]


@ultroid_cmd(
    pattern="stopvc$",
    admins_only=True,
    groups_only=True,
)
async def _(e):
    try:
        if call := await get_call(e):
            await e.client(stopvc(call))
            return await e.eor(get_string("vct_4"))
        await e.eor("`Voice call is not active.`")
    except Exception as ex:
        LOGS.exception(ex)
        await e.eor(f"`{ex}`")


@ultroid_cmd(
    pattern="vcinvite$",
    groups_only=True,
)
async def _(e):
    ok = await e.eor(get_string("vct_3"))
    users = []
    z = 0
    async for x in e.client.iter_participants(e.chat_id):
        if not x.bot:
            users.append(x.id)
    hmm = list(user_list(users, 6))
    call = await get_call(e)
    if not call:
        return await e.eor("`Voice Call is not active.`")
    for p in hmm:
        with contextlib.suppress(BaseException):
            await e.client(invitetovc(call=call, users=p))
            z += len(p)
    await ok.edit(get_string("vct_5").format(z))


@ultroid_cmd(
    pattern="startvc$",
    admins_only=True,
    groups_only=True,
)
async def _(e):
    try:
        await e.client(startvc(e.chat_id))
        await e.eor(get_string("vct_1"))
    except Exception as ex:
        LOGS.exception(ex)
        await e.eor(f"`{ex}`")


@ultroid_cmd(
    pattern="vctitle(?: |$)(.*)",
    admins_only=True,
    groups_only=True,
)
async def _(e):
    title = e.pattern_match.group(1).strip()
    if not title:
        return await e.eor(get_string("vct_6"), time=5)
    call = await get_call(e)
    if not call:
        return await e.eor("`Voice Call is not active.`")
    try:
        await e.client(settitle(call=call, title=title.strip()))
        await e.eor(get_string("vct_2").format(title))
    except Exception as ex:
        await e.eor(f"`{ex}`")
