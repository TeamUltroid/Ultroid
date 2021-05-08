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

• `{i}listgban`
   List all GBanned users.

• `{i}gmute <reply user/ username>`
    Globally Mute the User.

• `{i}ungmute <reply user/ username>`
    UnMute Globally.

• `{i}gkick <reply user/ username>`
    Globally Kick User.

• `{i}gcast <Message>`
    Globally Send that msg in all grps.

• `{i}gucast <Message>`
    Globally Send that msg in all Ur Chat Users.
"""

import os

from telethon import events

from . import *


@ultroid_cmd(
    pattern="ungban ?(.*)",
)
async def _(e):
    xx = await eor(e, "`UnGbanning...`")
    if e.is_private:
        userid = (await e.get_chat()).id
    elif e.reply_to_msg_id:
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
        return await eod(xx, "`Reply to some msg or add their id.`", time=5)
    name = (await e.client.get_entity(userid)).first_name
    chats = 0
    if not is_gbanned(userid):
        return await eod(xx, "`User is not gbanned.`", time=3)
    async for ggban in e.client.iter_dialogs():
        if ggban.is_group or ggban.is_channel:
            try:
                await e.client.edit_permissions(ggban.id, userid, view_messages=True)
                chats += 1
            except BaseException:
                pass
    ungban(userid)
    delete_gban_reason(userid)
    await xx.edit(
        f"`Ungbanned` [{name}](tg://user?id={userid}) `in {chats} chats.\nRemoved from gbanwatch.`",
    )


@ultroid_cmd(
    pattern="gban ?(.*)",
)
async def _(e):
    xx = await eor(e, "`Gbanning...`")
    reason = ""
    if e.is_private:
        userid = (await e.get_chat()).id
        try:
            reason = e.text.split(" ", maxsplit=1)[1]
        except IndexError:
            reason = ""
    elif e.reply_to_msg_id:
        userid = (await e.get_reply_message()).sender_id
        try:
            reason = e.text.split(" ", maxsplit=1)[1]
        except IndexError:
            reason = ""
    elif e.pattern_match.group(1):
        usr = e.text.split(" ", maxsplit=2)[1]
        if (e.pattern_match.group(1)).isdigit():
            try:
                userid = (await e.client.get_entity(int(usr))).id
            except ValueError as err:
                return await eod(xx, f"{str(err)}", time=5)
        else:
            try:
                userid = (await e.client.get_entity(str(usr))).id
            except ValueError as err:
                return await eod(xx, f"{str(err)}", time=5)
        try:
            reason = e.text.split(" ", maxsplit=2)[2]
        except IndexError:
            reason = ""
    else:
        return await eod(xx, "`Reply to some msg or add their id.`", tome=5)
    name = (await e.client.get_entity(userid)).first_name
    chats = 0
    if userid == ultroid_bot.uid:
        return await eod(xx, "`I can't gban myself.`", time=3)
    if str(userid) in DEVLIST:
        return await eod(xx, "`I can't gban my Developers.`", time=3)
    if is_gbanned(userid):
        return await eod(
            xx,
            "`User is already gbanned and added to gbanwatch.`",
            time=4,
        )
    async for ggban in e.client.iter_dialogs():
        if ggban.is_group or ggban.is_channel:
            try:
                await e.client.edit_permissions(ggban.id, userid, view_messages=False)
                chats += 1
            except BaseException:
                pass
    gban(userid)
    add_gban_reason(userid, reason)
    gb_msg = f"**#Gbanned** [{name}](tg://user?id={userid}) `in {chats} chats and added to gbanwatch!`"
    if reason != "":
        gb_msg += f"\n**Reason** - {reason}"
    await xx.edit(gb_msg)


@ultroid_cmd(
    pattern="gcast ?(.*)",
)
async def gcast(event):
    if not event.out and not is_fullsudo(event.sender_id):
        return await eor(event, "`This Command Is Sudo Restricted.`")
    xx = event.pattern_match.group(1)
    if not xx:
        return eor(event, "`Give some text to Globally Broadcast`")
    tt = event.text
    msg = tt[6:]
    kk = await eor(event, "`Globally Broadcasting Msg...`")
    er = 0
    done = 0
    async for x in ultroid_bot.iter_dialogs():
        if x.is_group:
            chat = x.id
            try:
                done += 1
                await ultroid_bot.send_message(chat, msg)
            except BaseException:
                er += 1
    await kk.edit(f"Done in {done} chats, error in {er} chat(s)")


@ultroid_cmd(
    pattern="gucast ?(.*)",
)
async def gucast(event):
    if not event.out and not is_fullsudo(event.sender_id):
        return await eor(event, "`This Command Is Sudo Restricted.`")
    xx = event.pattern_match.group(1)
    if not xx:
        return eor(event, "`Give some text to Globally Broadcast`")
    tt = event.text
    msg = tt[7:]
    kk = await eor(event, "`Globally Broadcasting Msg...`")
    er = 0
    done = 0
    async for x in ultroid_bot.iter_dialogs():
        if x.is_user and not x.entity.bot:
            chat = x.id
            try:
                done += 1
                await ultroid_bot.send_message(chat, msg)
            except BaseException:
                er += 1
    await kk.edit(f"Done in {done} chats, error in {er} chat(s)")


@ultroid_cmd(
    pattern="gkick ?(.*)",
)
async def gkick(e):
    xx = await eor(e, "`Gkicking...`")
    if e.is_private:
        userid = (await e.get_chat()).id
    elif e.reply_to_msg_id:
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
        return await eod(xx, "`Reply to some msg or add their id.`", time=5)
    name = (await e.client.get_entity(userid)).first_name
    chats = 0
    if userid == ultroid_bot.uid:
        return await eod(xx, "`I can't gkick myself.`", time=3)
    if str(userid) in DEVLIST:
        return await eod(xx, "`I can't gkick my Developers.`", time=3)
    async for gkick in e.client.iter_dialogs():
        if gkick.is_group or gkick.is_channel:
            try:
                await ultroid_bot.kick_participant(gkick.id, userid)
                chats += 1
            except BaseException:
                pass
    await xx.edit(f"`Gkicked` [{name}](tg://user?id={userid}) `in {chats} chats.`")


@ultroid_cmd(
    pattern="gmute ?(.*)",
)
async def _(e):
    xx = await eor(e, "`Gmuting...`")
    if e.is_private:
        userid = (await e.get_chat()).id
    elif e.reply_to_msg_id:
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
        return await eod(xx, "`I can't gmute myself.`", time=3)
    if str(userid) in DEVLIST:
        return await eod(xx, "`I can't gmute my Developers.`", time=3)
    if is_gmuted(userid):
        return await eod(xx, "`User is already gmuted.`", time=4)
    async for onmute in e.client.iter_dialogs():
        if onmute.is_group:
            try:
                await e.client.edit_permissions(onmute.id, userid, send_messages=False)
                chats += 1
            except BaseException:
                pass
    gmute(userid)
    await xx.edit(f"`Gmuted` [{name}](tg://user?id={userid}) `in {chats} chats.`")


@ultroid_cmd(
    pattern="ungmute ?(.*)",
)
async def _(e):
    xx = await eor(e, "`UnGmuting...`")
    if e.is_private:
        userid = (await e.get_chat()).id
    elif e.reply_to_msg_id:
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
        return await eod(xx, "`Reply to some msg or add their id.`", time=5)
    name = (await e.client.get_entity(userid)).first_name
    chats = 0
    if not is_gmuted(userid):
        return await eod(xx, "`User is not gmuted.`", time=3)
    async for hurr in e.client.iter_dialogs():
        if hurr.is_group:
            try:
                await e.client.edit_permissions(hurr.id, userid, send_messages=True)
                chats += 1
            except BaseException:
                pass
    ungmute(userid)
    await xx.edit(f"`Ungmuted` [{name}](tg://user?id={userid}) `in {chats} chats.`")


@ultroid_bot.on(events.ChatAction)
async def _(e):
    if e.user_joined or e.added_by:
        user = await e.get_user()
        chat = await e.get_chat()
        if is_gbanned(str(user.id)):
            if chat.admin_rights:
                try:
                    await e.client.edit_permissions(
                        chat.id,
                        user.id,
                        view_messages=False,
                    )
                    reason = get_gban_reason(user.id)
                    gban_watch = f"#GBanned_User Joined.\n\n**User** - [{user.first_name}](tg://user?id={user.id})\n"
                    if reason is not None:
                        gban_watch += f"**Reason**: {reason}\n\n"
                    gban_watch += f"`User Banned.`"
                    await e.reply(gban_watch)
                except BaseException:
                    pass


@ultroid_cmd(pattern="listgban")
async def list_gengbanned(event):
    users = gbanned_user()
    x = await eor(event, get_string("com_1"))
    msg = ""
    if not udB.get("GBAN"):
        return await x.edit("`You haven't GBanned anyone!`")
    for i in users:
        try:
            name = (await ultroid.get_entity(int(i))).first_name
        except BaseException:
            name = i
        msg += "**User**: " + name + "\n"
        reason = get_gban_reason(i)
        if reason is not None:
            msg += f"**Reason**: {reason}\n\n"
        else:
            msg += "\n"
    gbanned_users = f"**List of users GBanned by {OWNER_NAME}**:\n\n{msg}"
    if len(gbanned_users) > 4096:
        f = open("gbanned.txt", "w")
        f.write(gbanned_users.replace("`", "").replace("*", ""))
        f.close()
        await x.reply(
            file="gbanned.txt",
            caption=f"List of users GBanned by [{OWNER_NAME}](tg://user?id={OWNER_ID})",
        )
        os.remove("gbanned.txt")
        await x.delete()
    else:
        await x.edit(gbanned_users)


HELP.update({f"{__name__.split('.')[1]}": f"{__doc__.format(i=HNDLR)}"})
