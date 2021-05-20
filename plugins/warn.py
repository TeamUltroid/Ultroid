#Ultroid - UserBot
# Copyright (C) 2020 TeamUltroid
#
# This file is a part of < https://github.com/TeamUltroid/Ultroid/ >
# PLease read the GNU Affero General Public License in
# <https://www.github.com/TeamUltroid/Ultroid/blob/main/LICENSE/>.

"""
✘ Commands Available

•{i}warn

•{i}resetwarn

•{i}warns

•{i}setwarn

"""

from pyUltroid.functions.warn_db import *
from . import *

   
@ultroid_cmd(pattern="warn ?(.*)", groups_only=True)
async def warn(e):
    reply = await e.get_reply_message()
    if len(e.text) > 5:
        if not " " in e.text[5]:
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
            return await eor(e, "Reply To user")
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
        number , action = int(x.split()[0]), x.split()[1]
    except BaseException:
        number, action = 3, "ban"
    if ("ban", "kick", "mute") not in action:
        action = "ban"
    if count+1 >= number:
        if "ban" in action:
            try:
                await ultroid_bot.edit_permissions(e.chat_id, user, view_messages=False)
            except BaseException:
                return await eor(e, "`Something Went Wrong.`")
        elif "kick" in action:
            try:
                await ultroid_bot.kick_participant(e.chat_id, user)
            except BaseException:
                return await eor(e, "`Something Went Wrong.`")
        elif "mute" in action:
            try:
                await ultroid_bot.edit_permissions(e.chat_id, user, until_date=None, send_messages=False)
            except BaseException:
                return await eor(e, "`Something Went Wrong.`")
        reset_warn(e.chat_id, user)
        return await eor(e, "reason lauda lassna")
    add_warn(e.chat_id, user, count+1, r)
    await eor(e, f"**WARNING :** {count+1}/{number}\n\n**Be Careful !!!**\n\n**Reason** : {reason}")
 
@ultroid_cmd(pattern="resetwarn ?(.*)") 
async def rwarn(e):
    reply = await e.get_reply_message()
    if reply:
        user = reply.from_id.user_id
    else:
        try:
            user = e.text.split()[1]
            if user.startswith("@"):
                ok = await ultroid_bot.get_entity(user)
                user = ok.id
            else:
                user = int(user)
        except BaseException:
            return await eor(e, "Reply To user")
    reset_warn(e.chat_id, user)
    await eor(e, "Cleared All Warns.")
    
@ultroid_cmd(pattern="warns ?(.*)")
async def twarns(e):
    reply = await e.get_reply_message()
    if reply:
        user = reply.from_id.user_id
    else:
        try:
            user = e.text.split()[1]
            if user.startswith("@"):
                ok = await ultroid_bot.get_entity(user)
                user = ok.id
            else:
                user = int(user)
        except BaseException:
            return
    c, r = warns(e.chat_id, user)
    if c and r:
        r = r.split("|$|")
        text = ""
        for x in range(c):
            text += f"•**{x+1}.** {r[x]}\n"
        await eor(e, text)
        
        
@ultroid_cmd(pattern="setwarn ?(.*)")
async def warnset(e):
    ok = e.pattern_match.group(1)
    if not ok:
        return await eor(e, "stuff")
    if "|" in ok:
        try:
            number , action = int(x.split()[0]), x.split()[1]
        except BaseException:
            return await eor(e, "incorrect")
        if ("ban", "kick", "mute") not in action:
            return await eor(e, "stuff")
        udB.set("SETWARN", f"{number} {action}")
        return await eor(e, "succesx")
    else:
        await eor(e, "incorrect")
        
        
HELP.update({f"{__name__.split('.')[1]}": f"{__doc__.format(i=HNDLR)}"})        