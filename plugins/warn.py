# Ultroid - UserBot
# Copyright (C) 2021 TeamUltroid
#
# This file is a part of < https://github.com/TeamUltroid/Ultroid/ >
# PLease read the GNU Affero General Public License in
# <https://www.github.com/TeamUltroid/Ultroid/blob/main/LICENSE/>.

"""
✘ Commands Available

•`{i}warn <reply to user> <reason>`
    Gives Warn.

•`{i}resetwarn <reply to user>`
    To reset All Warns.

•`{i}warns <reply to user>`
   To Get List of Warnings of a user.

•`{i}setwarn <warn count> | <ban/mute/kick>`
   Set Number in warn count for warnings
   After putting " | " mark put action like ban/mute/kick
   Its Default 3 kick
   Example : `setwarn 5 | mute`

"""

from pyUltroid.functions.warn_db import *
from telethon.utils import get_display_name

from . import *


@ultroid_cmd(pattern="warn ?(.*)", groups_only=True, admins_only=True)
async def warn(e):
    ultroid_bot = e.client
    reply = await e.get_reply_message()
    if len(e.text) > 5:
        if " " not in e.text[5]:
            return
    if reply:
        user = reply.from_id.user_id
        reason = "unknown"
        if e.pattern_match.group(1):
            reason = e.text[5:]
    else:
        try:
            user = e.text.split()[1]
            if user.startswith("@"):
                ok = await ultroid_bot.get_entity(user)
                user = ok.id
            else:
                user = int(user)
        except BaseException:
            return await eod(e, "Reply To A User")
        try:
            reason = e.text.split(maxsplit=2)[-1]
        except BaseException:
            reason = "unknown"
    count, r = warns(e.chat_id, user)
    if not r:
        r = reason
    else:
        r = r + "|$|" + reason
    try:
        x = udB.get("SETWARN")
        number, action = int(x.split()[0]), x.split()[1]
    except BaseException:
        number, action = 3, "kick"
    if ("ban" or "kick" or "mute") not in action:
        action = "kick"
    if count + 1 >= number:
        if "ban" in action:
            try:
                await ultroid_bot.edit_permissions(e.chat_id, user, view_messages=False)
            except BaseException:
                return await eod(e, "`Something Went Wrong.`")
        elif "kick" in action:
            try:
                await ultroid_bot.kick_participant(e.chat_id, user)
            except BaseException:
                return await eod(e, "`Something Went Wrong.`")
        elif "mute" in action:
            try:
                await ultroid_bot.edit_permissions(
                    e.chat_id, user, until_date=None, send_messages=False
                )
            except BaseException:
                return await eod(e, "`Something Went Wrong.`")
        add_warn(e.chat_id, user, count + 1, r)
        c, r = warns(e.chat_id, user)
        ok = await ultroid_bot.get_entity(user)
        user = f"[{get_display_name(ok)}](tg://user?id={ok.id})"
        r = r.split("|$|")
        text = f"User {user} Got {action} Due to {count+1} Warns.\n\n"
        for x in range(c):
            text += f"•**{x+1}.** {r[x]}\n"
        await eor(e, text)
        return reset_warn(e.chat_id, ok.id)
    add_warn(e.chat_id, user, count + 1, r)
    ok = await ultroid_bot.get_entity(user)
    user = f"[{get_display_name(ok)}](tg://user?id={ok.id})"
    await eor(
        e,
        f"**WARNING :** {count+1}/{number}\n**To :**{user}\n**Be Careful !!!**\n\n**Reason** : {reason}",
    )


@ultroid_cmd(pattern="resetwarn ?(.*)", groups_only=True, admins_only=True)
async def rwarn(e):
    reply = await e.get_reply_message()
    if reply:
        user = reply.from_id.user_id
    else:
        try:
            user = e.text.split()[1]
            if user.startswith("@"):
                ok = await e.client.get_entity(user)
                user = ok.id
            else:
                user = int(user)
        except BaseException:
            return await eor(e, "Reply To user")
    reset_warn(e.chat_id, user)
    ok = await e.client.get_entity(user)
    user = f"[{get_display_name(ok)}](tg://user?id={ok.id})"
    await eor(e, f"Cleared All Warns of {user}.")


@ultroid_cmd(pattern="warns ?(.*)", groups_only=True, admins_only=True)
async def twarns(e):
    reply = await e.get_reply_message()
    if reply:
        user = reply.from_id.user_id
    else:
        try:
            user = e.text.split()[1]
            if user.startswith("@"):
                ok = await e.client.get_entity(user)
                user = ok.id
            else:
                user = int(user)
        except BaseException:
            return await eod(e, "Reply To A User")
    c, r = warns(e.chat_id, user)
    if c and r:
        ok = await e.client.get_entity(user)
        user = f"[{get_display_name(ok)}](tg://user?id={ok.id})"
        r = r.split("|$|")
        text = f"User {user} Got {c} Warns.\n\n"
        for x in range(c):
            text += f"•**{x+1}.** {r[x]}\n"
        await eor(e, text)
    else:
        await eor(e, "`No Warnings`")


@ultroid_cmd(pattern="setwarn ?(.*)")
async def warnset(e):
    ok = e.pattern_match.group(1)
    if not ok:
        return await eor(e, "stuff")
    if "|" in ok:
        try:
            number, action = int(ok.split()[0]), ok.split()[1]
        except BaseException:
            return await eod(e, "`Incorrect Format`")
        if ("ban" or "kick" or "mute") not in action:
            return await eod(e, "`Only mute / ban / kick option suported`")
        udB.set("SETWARN", f"{number} {action}")
        return await eor(
            e, f"Done Your Warn Count is now {number} and Action is {action}"
        )
    else:
        await eod(e, "`Incorrect Format`")
