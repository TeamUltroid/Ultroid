from . import *


@asst_cmd("ban")
async def banhammer(event):
    x = await event.get_reply_message()
    if x is None:
        return await event.edit("Please reply to someone to ban him.")
    if x.fwd_from:
        target = x.fwd_from.from_id.user_id
    else:
        # this is a weird way of doing it
        return
    if not is_blacklisted(target):
        blacklist_user(target)
        await asst.send_message(event.chat_id, f"#BAN\nUser - {target}")
        await asst.send_message(
            target,
            "`GoodBye! You have been banned.`\n**Further messages you send will not be forwarded.**",
        )
    else:
        return await asst.send_message(event.chat_id, f"User is already banned!")


@asst_cmd("unban")
async def banhammer(event):
    x = await event.get_reply_message()
    if x is None:
        return await event.edit("Please reply to someone to ban him.")
    if x.fwd_from:
        target = x.fwd_from.from_id.user_id
    else:
        # this is a weird way of doing it
        return
    if is_blacklisted(target):
        rem_blacklist(target)
        await asst.send_message(event.chat_id, f"#UNBAN\nUser - {target}")
        await asst.send_message(target, "`Congrats! You have been unbanned.`")
    else:
        return await asst.send_message(event.chat_id, f"User was never banned!")
