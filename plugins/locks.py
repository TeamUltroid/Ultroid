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
from telethon.tl.types import ChatBannedRights
from .. import ultroid_cmd


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



def lock_unlock(query, lock=True):
    """
    `Used in locks plugin`
     Is there any better way to do this?
    """
    rights = ChatBannedRights(None)
    _do = lock
    if query == "msgs":
        for i in ["send_messages", "invite_users", "pin_messages" "change_info"]:
            setattr(rights, i, _do)
    elif query == "media":
        setattr(rights, "send_media", _do)
    elif query == "sticker":
        setattr(rights, "send_stickers", _do)
    elif query == "gif":
        setattr(rights, "send_gifs", _do)
    elif query == "games":
        setattr(rights, "send_games", _do)
    elif query == "inline":
        setattr(rights, "send_inline", _do)
    elif query == "polls":
        setattr(rights, "send_polls", _do)
    elif query == "invites":
        setattr(rights, "invite_users", _do)
    elif query == "pin":
        setattr(rights, "pin_messages", _do)
    elif query == "changeinfo":
        setattr(rights, "change_info", _do)
    else:
        return None
    return rights


# ---------------- END ---------------- #
