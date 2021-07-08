# Ultroid - UserBot
# Copyright (C) 2021 TeamUltroid
#
# This file is a part of < https://github.com/TeamUltroid/Ultroid/ >
# PLease read the GNU Affero General Public License in
# <https://www.github.com/TeamUltroid/Ultroid/blob/main/LICENSE/>.
"""
✘ Commands Available -

• `{i}lock <msgs/media/sticker/gif/games/inline/polls/invites/pin/changeinfo>`
    Lock the Used Setting in Used Group.

• `{i}unlock <msgs/media/sticker/gif/games/inline/polls/invites/pin/changeinfo>`
    UNLOCK the Used Setting in Used Group.

"""
from pyUltroid.functions.all import lucks
from pyUltroid.functions.all import unlucks
from telethon.tl.functions.messages import EditChatDefaultBannedRightsRequest

from . import *


@ultroid_cmd(
    pattern="lock ?(.*)",
    groups_only=True,
    admins_only=True,
    type=["official", "manager"],
)
async def lockho(e):
    mat = e.pattern_match.group(1)
    if not mat:
        return await eod(e, "`What to Lock  ?`")
    try:
        ml = lucks(mat)
    except BaseException:
        return await eod(e, "`Incorrect Input`")
    await e.client(EditChatDefaultBannedRightsRequest(e.chat_id, ml))
    await eor(e, f"Locked - `{mat}` ! ")


@ultroid_cmd(
    pattern="unlock ?(.*)",
    groups_only=True,
    admins_only=True,
    type=["official", "manager"],
)
async def unlckho(e):
    mat = e.pattern_match.group(1)
    if not mat:
        return await eod(e, "`What to Lock  ?`")
    try:
        ml = unlucks(mat)
    except BaseException:
        return await eod(e, "`Incorrect Input`")
    await e.client(EditChatDefaultBannedRightsRequest(e.chat_id, ml))
    await eor(e, f"Unlocked - `{mat}` ! ")
