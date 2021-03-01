# Ultroid - UserBot
# Copyright (C) 2020 TeamUltroid
#
# This file is a part of < https://github.com/TeamUltroid/Ultroid/ >
# PLease read the GNU Affero General Public License in
# <https://www.github.com/TeamUltroid/Ultroid/blob/main/LICENSE/>.

"""
✘ Commands Available -

• `{i}gban <reply user/ username>`
    Globally Ban User.

• `{i}ungban <reply user/ username>`
    Unban Globally.

• `{i}gcast <Message>`
    Globally Send that msg in all grps.
"""

from telethon import events
from . import *


@ultroid_cmd(pattern="ungban ?(.*)")
async def _(e):
    xx = await eor(e, "`UnGbanning...`")
    if e.reply_to_msg_id:
        userid = (await e.get_reply_message()).sender_id
    elif e.pattern_match.group(1):
        if (e.pattern_match.group(1)).isdigit():
            try:
                userid = (await e.client.get_entity(int(e.pattern_match.group(1)))).id
            except ValueError as err:
                return await eod(xx, f"{str(err)}", time=5)
        else:
            try:
                userid = (await e.client.get_entity(str(e.pattern_match.group(1)))).id
            except ValueError as err:
                return await eod(xx, f"{str(err)}", time=5)
    else:
        return await eod(xx, "`Reply to some msg or add their id.`", tome=5)
    name = (await e.client.get_entity(userid)).first_name
    chats = 0
    if not is_gbanned(userid):
        return await eod(xx, "`User is not gbanned.`", time=3)
    async for ggban in e.client.iter_dialogs():
        if ggban.is_group or ggban.is_channel:
            try:
                await e.client.edit_permissions(ggban.id, userid, view_messages=True)
                chats += 1
            except:
                pass
    ungban(userid)
    await xx.edit(
        f"`Ungbanned` [{name}](tg://user?id={userid}) `in {chats} chats.\nRemoved from gbanwatch.`"
    )


@ultroid_cmd(pattern="gban ?(.*)")
async def _(e):
    xx = await eor(e, "`Gbanning...`")
    if e.reply_to_msg_id:
        userid = (await e.get_reply_message()).sender_id
    elif e.pattern_match.group(1):
        if (e.pattern_match.group(1)).isdigit():
            try:
                userid = (await e.client.get_entity(int(e.pattern_match.group(1)))).id
            except ValueError as err:
                return await eod(xx, f"{str(err)}", time=5)
        else:
            try:
                userid = (await e.client.get_entity(str(e.pattern_match.group(1)))).id
            except ValueError as err:
                return await eod(xx, f"{str(err)}", time=5)
    else:
        return await eod(xx, "`Reply to some msg or add their id.`", tome=5)
    name = (await e.client.get_entity(userid)).first_name
    chats = 0
    if userid == ultroid_bot.uid:
        return await eod(xx, "`I can't gban myself.`", time=3)
    if str(userid) in DEVLIST:
        return await eod(xx, "`I can't gban my Developers.`", time=3)
    if str(userid) in (Redis("SUDOS")).split(" "):
        return await eod(xx, "`I can't gban a sudo user.`", time=3)
    if is_gbanned(userid):
        return await eod(
            xx, "`User is already gbanned and added to gbanwatch.`", time=4
        )
    async for ggban in e.client.iter_dialogs():
        if ggban.is_group or ggban.is_channel:
            try:
                await e.client.edit_permissions(ggban.id, userid, view_messages=False)
                chats += 1
            except:
                pass
    gban(userid)
    await xx.edit(
        f"`Gbanned` [{name}](tg://user?id={userid}) `in {chats} chats.\nAdded to gbanwatch.`"
    )


@ultroid_cmd(pattern="gcast ?(.*)")
async def gcast(event):
    xx = event.pattern_match.group(1)
    if not xx:
        return eor(event, "`Give some text to Globally Broadcast`")
    tt = event.text
    msg = tt[5:]
    kk = await eor(event, "`Globally Broadcasting Msg...`")
    async for x in borg.iter_dialogs():
        er = 0
        done = 0
        if x.is_group:
            chat = x.id
            try:
                await ultroid_bot.send_message(chat, msg)
                done += 1
            except:
                er += 1
                pass
    await kk.edit(f"Done in {done} chats, error in {er} chat(s)")


@ultroid_bot.on(events.ChatAction)
async def _(e):
    if e.user_joined or e.added_by:
        user = await e.get_user()
        chat = await e.get_chat()
        if is_gbanned(str(user.id)):
            if chat.admin_rights.ban_users:
                try:
                    await e.client.edit_permissions(
                        chat.id, user.id, view_messages=False
                    )
                    gban_watch = f"`Gbanned User` [{user.first_name}](tg://user?id={user.id}) `Spotted\n"
                    gban_watch += f"Banned Successfully`"
                except:
                    pass
            else:
                gban_watch = (
                    f"@admins `Gbanned user` [{user.first_name}]({user.id}) `Spotted.`"
                )
            await e.reply(gban_watch)


HELP.update({f"{__name__.split('.')[1]}": f"{__doc__.format(i=Var.HNDLR)}"})
