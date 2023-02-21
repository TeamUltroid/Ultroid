# credit https://t.me/I_m_FlaSh

"""
✘ Commands Available -
• `{i}totalmsgs`
    Returns your total msg count in current chat

• `{i}totalmsgs [username]/<reply>`
    Returns total msg count of user in current chat
"""

from telethon.utils import get_display_name

from . import *


@ultroid_cmd(pattern="totalmsgs ?(.*)")
async def _(e):
    match = e.pattern_match.group(1)
    if match:
        user = match
    elif e.is_reply:
        user = (await e.get_reply_message()).sender_id
    else:
        user = "me"
    try:
        a = await e.client.get_messages(e.chat_id, limit=0, from_user=user)
    except Exception as er:
        return await e.eor(str(er))
    user = await e.client.get_entity(user)
    await e.eor(f"Total msgs of `{get_display_name(user)}` here = {a.total}")
