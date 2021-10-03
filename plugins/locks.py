# Ultroid - UserBot
# Copyright (C) 2021 TeamUltroid
#
# This file is a part of < https://github.com/TeamUltroid/Ultroid/ >
# PLease read the GNU Affero General Public License in
# <https://www.github.com/TeamUltroid/Ultroid/blob/main/LICENSE/>.
"""
✘ Commands Available -

• `{i}lock <msgs/media/sticker/gif/games/inlines/polls/invites/pin/changeinfo>`
    Lock the Used Setting in Used Group.

• `{i}unlock <msgs/media/sticker/gif/games/inlines/polls/invites/pin/changeinfo>`
    UNLOCK the Used Setting in Used Group.

"""
from pyUltroid.functions.admins import lock_unlock
from telethon.tl.functions.messages import EditChatDefaultBannedRightsRequest

from . import eor, ultroid_cmd


@ultroid_cmd(
    pattern="(un|)lock ?(.*)",
    groups_only=True,
    admins_only=True,
    type=["official", "manager"],
)
async def unlckho(e):
    mat = e.pattern_match.group(2)
    if not mat:
        return await eor(e, "`Give some Proper Input..`", time=5)
    lock = True
    text = "Locked"
    if e.text[1:].startswith("un"):
        lock = False
        text = "Unlocked"
    ml = lock_unlock(mat, lock=lock)
    if not ml:
        return await eor(e, "`Incorrect Input`", time=5)
    await e.client(EditChatDefaultBannedRightsRequest(e.chat_id, ml))
    await eor(e, f"{text} - `{mat}` ! ")
