from . import *


@ultroid_cmd(pattern="dkick", type=["manager", "official"])
async def dowj(e):
    if e.is_reply:
        replied = await e.get_reply_message()
        user = (await replied.get_sender()).id
    else:
        return await eor(e, "Reply to a message...")
    try:
        await replied.delete()
        await e.client.kick_participant(e.chat_id, user)
        await eor(e, "Kicked Successfully!")
    except Exception as E:
        await eor(e, str(E))


@ultroid_cmd(pattern="dban", type=["manager", "official"])
async def dowj(e):
    if e.is_reply:
        replied = await e.get_reply_message()
        user = (await replied.get_sender()).id
    else:
        return await eor(e, "Reply to a message...")
    try:
        await replied.delete()
        await e.client.edit_permissions(e.chat_id, user, view_messages=False)
        await eor(e, "Banned Successfully!")
    except Exception as E:
        await eor(e, str(E))


@ultroid_cmd(pattern="dmute", type=["manager", "official"])
async def dowj(e):
    if e.is_reply:
        replied = await e.get_reply_message()
        user = (await replied.get_sender()).id
    else:
        return await eor(e, "Reply to a message...")
    try:
        await replied.delete()
        await e.client.edit_permissions(e.chat_id, user, send_messages=False)
        await eor(e, "Muted Successfully!")
    except Exception as E:
        await eor(e, str(E))
