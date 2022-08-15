# Ultroid - UserBot
# Copyright (C) 2021-2022 TeamUltroid
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
from telethon.tl.functions.messages import EditChatDefaultBannedRightsRequest

from pyUltroid.fns.admins import lock_unlock

from . import ultroid_cmd


@ultroid_cmd(
    pattern="(un|)lock( (.*)|$)", admins_only=True, manager=True, require="change_info"
)
async def un_lock(e):
    mat = e.pattern_match.group(2).strip()
    if not mat:
        return await e.eor("`Give some Proper Input..`", time=5)
    lock = e.pattern_match.group(1) == ""
    ml = lock_unlock(mat, lock)
    if not ml:
        return await e.eor("`Incorrect Input`", time=5)
    msg = "Locked" if lock else "Unlocked"
    try:
        await e.client(EditChatDefaultBannedRightsRequest(e.chat_id, ml))
    except Exception as er:
        return await e.eor(str(er))
    await e.eor(f"**{msg}** - `{mat}` ! ")
