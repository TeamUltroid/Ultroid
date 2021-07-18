# Ultroid - UserBot
# Copyright (C) 2021 TeamUltroid
#
# This file is a part of < https://github.com/TeamUltroid/Ultroid/ >
# PLease read the GNU Affero General Public License in
# <https://www.github.com/TeamUltroid/Ultroid/blob/main/LICENSE/>.
"""
✘ Commands Available -

• `{i}gban <reply user/ username>`
• `{i}ungban`
    Ban/Unban Globally.

• `{i}gstat <reply to user/userid/username>`
   Check if user is GBanned.

• `{i}listgban`
   List all GBanned users.

• `{i}gmute <reply user/ username>`
• `{i}ungmute`
    Mute/UnMute Globally.

• `{i}gkick <reply user/ username>`
    Globally Kick User.

• `{i}gcast <Message>`
    Globally Send that msg in all grps.

• `{i}gucast <Message>`
    Globally Send that msg in all Ur Chat Users.

• `{i} gblacklist <chat id/username/nothing (for current chat)`
   Add chat to blacklist and not send global broadcasts there.

• `{i} ungblacklist <chat id/username/nothing (for current chat)`
   Remove the chat from blacklist adn continue sending global broadcasts there.

•`{i}gpromote <reply to user> <channel/group/all> <rank>`
    globally promote user where you are admin.
    You can also set where To promote only groups or only channels or in all.
    Like. `gpromote group boss` ~ it promote repied user in all groups.
    Or. `gpromote @username all sar` ~ it promote the users in all group and channel.

•`{i}gdemote`
    Same function as gpromote.
"""
import os

from pyUltroid.functions.gban_mute_db import *
from pyUltroid.functions.gcast_blacklist_db import *
from telethon.tl.functions.channels import EditAdminRequest
from telethon.tl.functions.contacts import BlockRequest, UnblockRequest
from telethon.tl.types import ChatAdminRights

from . import *

_gpromote_rights = ChatAdminRights(
    add_admins=False,
    invite_users=True,
    change_info=False,
    ban_users=True,
    delete_messages=True,
    pin_messages=True,
)

_gdemote_rights = ChatAdminRights(
    add_admins=False,
    invite_users=False,
    change_info=False,
    ban_users=False,
    delete_messages=False,
    pin_messages=False,
)


@ultroid_cmd(
    pattern="gpromote ?(.*)",
)
async def _(e):
    if not e.out and not is_fullsudo(e.sender_id):
        return await eod(e, "`This Command Is Sudo Restricted.`")
    x = e.pattern_match.group(1)
    ultroid_bot = e.client
    if not x:
        return await eod(e, "`Incorrect Format`")
    user = await e.get_reply_message()
    if user:
        ev = await eor(e, "`Promoting Replied User Globally`")
        ok = e.text.split()
        key = "all"
        if len(ok) > 1:
            if ("group" in ok[1]) or ("channel" in ok[1]):
                key = ok[1]
        rank = "AdMin"
        if len(ok) > 2:
            rank = ok[2]
        c = 0
        if e.is_private:
            user.id = user.peer_id.user_id
        else:
            user.id = user.from_id.user_id
        async for x in e.client.iter_dialogs():
            if "group" in key.lower():
                if x.is_group:
                    try:
                        await e.client(
                            EditAdminRequest(
                                x.id,
                                user.id,
                                _gpromote_rights,
                                rank,
                            ),
                        )
                        c += 1
                    except BaseException:
                        pass
            elif "channel" in key.lower():
                if x.is_channel:
                    try:
                        await e.client(
                            EditAdminRequest(
                                x.id,
                                user.id,
                                _gpromote_rights,
                                rank,
                            ),
                        )
                        c += 1
                    except BaseException:
                        pass
            else:
                if x.is_group or x.is_channel:
                    try:
                        await e.client(
                            EditAdminRequest(
                                x.id,
                                user.id,
                                _gpromote_rights,
                                rank,
                            ),
                        )
                        c += 1
                    except Exception as er:
                        LOGS.info(er)
        return await eor(ev, f"Promoted The Replied Users in Total : {c} {key} chats")
    else:
        k = e.text.split()
        if not k[1]:
            return await eod(e, "`Give someone's username/id or replied to user.")
        user = k[1]
        if user.isdigit():
            user = int(user)
        try:
            name = await e.client.get_entity(user)
        except BaseException:
            return await eod(e, f"`No User Found Regarding {user}`")
        ev = await eor(e, f"`Promoting {name.first_name} globally.`")
        key = "all"
        if len(k) > 2:
            if ("group" in k[2]) or ("channel" in k[2]):
                key = k[2]
        rank = "AdMin"
        if len(k) > 3:
            rank = k[3]
        c = 0
        async for x in e.client.iter_dialogs():
            if "group" in key.lower():
                if x.is_group:
                    try:
                        await ultroid_bot(
                            EditAdminRequest(
                                x.id,
                                user,
                                _gpromote_rights,
                                rank,
                            ),
                        )
                        c += 1
                    except BaseException:
                        pass
            elif "channel" in key.lower():
                if x.is_channel:
                    try:
                        await ultroid_bot(
                            EditAdminRequest(
                                x.id,
                                user,
                                _gpromote_rights,
                                rank,
                            ),
                        )
                        c += 1
                    except BaseException:
                        pass
            else:
                if x.is_group or x.is_channel:
                    try:
                        await ultroid_bot(
                            EditAdminRequest(
                                x.id,
                                user,
                                _gpromote_rights,
                                rank,
                            ),
                        )
                        c += 1
                    except BaseException:
                        pass
        return await eor(ev, f"Promoted {name.first_name} in Total : {c} {key} chats.")


@ultroid_cmd(
    pattern="gdemote ?(.*)",
)
async def _(e):
    if not e.out and not is_fullsudo(e.sender_id):
        return await eod(e, "`This Command Is Sudo Restricted.`")
    x = e.pattern_match.group(1)
    ultroid_bot = e.client
    if not x:
        return await eod(e, "`Incorrect Format`")
    user = await e.get_reply_message()
    if user:
        if e.is_private:
            user.id = user.peer_id.user_id
        else:
            user.id = user.from_id.user_id
        ev = await eor(e, "`Demoting Replied User Globally`")
        ok = e.text.split()
        key = "all"
        if len(ok) > 1:
            if ("group" in ok[1]) or ("channel" in ok[1]):
                key = ok[1]
        rank = "Not AdMin"
        c = 0
        async for x in e.client.iter_dialogs():
            if "group" in key.lower():
                if x.is_group:
                    try:
                        await ultroid_bot(
                            EditAdminRequest(
                                x.id,
                                user.id,
                                _gdemote_rights,
                                rank,
                            ),
                        )
                        c += 1
                    except BaseException:
                        pass
            elif "channel" in key.lower():
                if x.is_channel:
                    try:
                        await ultroid_bot(
                            EditAdminRequest(
                                x.id,
                                user.id,
                                _gdemote_rights,
                                rank,
                            ),
                        )
                        c += 1
                    except BaseException:
                        pass
            else:
                if x.is_group or x.is_channel:
                    try:
                        await ultroid_bot(
                            EditAdminRequest(
                                x.id,
                                user.id,
                                _gdemote_rights,
                                rank,
                            ),
                        )
                        c += 1
                    except BaseException:
                        pass
        return await eor(ev, f"Demoted The Replied Users in Total : {c} {key} chats")
    else:
        k = e.text.split()
        if not k[1]:
            return await eod(e, "`Give someone's username/id or replied to user.")
        user = k[1]
        if user.isdigit():
            user = int(user)
        try:
            name = await ultroid_bot.get_entity(user)
        except BaseException:
            return await eod(e, f"`No User Found Regarding {user}`")
        ev = await eor(e, f"`Demoting {name.first_name} globally.`")
        key = "all"
        if len(k) > 2:
            if ("group" in k[2]) or ("channel" in k[2]):
                key = k[2]
        rank = "Not AdMin"
        c = 0
        async for x in ultroid_bot.iter_dialogs():
            if "group" in key.lower():
                if x.is_group:
                    try:
                        await ultroid_bot(
                            EditAdminRequest(
                                x.id,
                                user,
                                _gdemote_rights,
                                rank,
                            ),
                        )
                        c += 1
                    except BaseException:
                        pass
            elif "channel" in key.lower():
                if x.is_channel:
                    try:
                        await ultroid_bot(
                            EditAdminRequest(
                                x.id,
                                user,
                                _gdemote_rights,
                                rank,
                            ),
                        )
                        c += 1
                    except BaseException:
                        pass
            else:
                if x.is_group or x.is_channel:
                    try:
                        await ultroid_bot(
                            EditAdminRequest(
                                x.id,
                                user,
                                _gdemote_rights,
                                rank,
                            ),
                        )
                        c += 1
                    except BaseException:
                        pass
        return await eor(ev, f"Demoted {name.first_name} in Total : {c} {key} chats.")


@ultroid_cmd(
    pattern="ungban ?(.*)",
)
async def _(e):
    xx = await eor(e, "`UnGbanning...`")
    if e.reply_to_msg_id:
        userid = (await e.get_reply_message()).sender_id
    elif e.pattern_match.group(1):
        userid = await get_user_id(e.pattern_match.group(1))
    elif e.is_private:
        userid = (await e.get_chat()).id
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
    try:
        ungban(userid)
        delete_gban_reason(userid)
        await e.client(UnblockRequest(int(userid)))
    except Exception as ex:
        return await eor(xx, str(ex))
    await xx.edit(
        f"`Ungbanned` [{name}](tg://user?id={userid}) `in {chats} chats.\nRemoved from gbanwatch.`",
    )


@ultroid_cmd(
    pattern="gban ?(.*)",
)
async def _(e):
    if not e.out and not is_fullsudo(e.sender_id):
        return await eor(e, "`This Command Is Sudo Restricted.`")
    xx = await eor(e, "`Gbanning...`")
    reason = ""
    if e.reply_to_msg_id:
        userid = (await e.get_reply_message()).sender_id
        try:
            reason = e.text.split(" ", maxsplit=1)[1]
        except IndexError:
            reason = ""
    elif e.pattern_match.group(1):
        usr = e.text.split(" ", maxsplit=2)[1]
        userid = await get_user_id(usr)
        try:
            reason = e.text.split(" ", maxsplit=2)[2]
        except IndexError:
            reason = ""
    elif e.is_private:
        userid = (await e.get_chat()).id
        try:
            reason = e.text.split(" ", maxsplit=1)[1]
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
    try:
        gban(userid)
        add_gban_reason(userid, reason)
        await e.client(BlockRequest(int(userid)))
    except Exception as ex:
        return await eor(xx, str(ex))
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
    async for x in event.client.iter_dialogs():
        if x.is_group:
            chat = x.id
            if not is_gblacklisted(chat):
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
    async for x in event.client.iter_dialogs():
        if x.is_user and not x.entity.bot:
            chat = x.id
            if not is_gblacklisted(chat):
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
    if e.reply_to_msg_id:
        userid = (await e.get_reply_message()).sender_id
    elif e.pattern_match.group(1):
        userid = await get_user_id(e.pattern_match.group(1))
    elif e.is_private:
        userid = (await e.get_chat()).id
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
                await e.client.kick_participant(gkick.id, userid)
                chats += 1
            except BaseException:
                pass
    await xx.edit(f"`Gkicked` [{name}](tg://user?id={userid}) `in {chats} chats.`")


@ultroid_cmd(
    pattern="gmute ?(.*)",
)
async def _(e):
    if not e.out and not is_fullsudo(e.sender_id):
        return await eor(e, "`This Command Is Sudo Restricted.`")
    xx = await eor(e, "`Gmuting...`")
    if e.reply_to_msg_id:
        userid = (await e.get_reply_message()).sender_id
    elif e.pattern_match.group(1):
        userid = await get_user_id(e.pattern_match.group(1))
    elif e.is_private:
        userid = (await e.get_chat()).id
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
    if e.reply_to_msg_id:
        userid = (await e.get_reply_message()).sender_id
    elif e.pattern_match.group(1):
        userid = await get_user_id(e.pattern_match.group(1))
    elif e.is_private:
        userid = (await e.get_chat()).id
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


@ultroid_cmd(
    pattern="listgban",
)
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
        msg += f"**User**: {name}\n"
        reason = get_gban_reason(i)
        if reason is not None or "":
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
            message=f"List of users GBanned by [{OWNER_NAME}](tg://user?id={OWNER_ID})",
        )
        os.remove("gbanned.txt")
        await x.delete()
    else:
        await x.edit(gbanned_users)


@ultroid_cmd(
    pattern="gstat ?(.*)",
)
async def gstat_(e):
    xx = await eor(e, get_string("com_1"))
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
    msg = "**" + name + " is "
    is_banned = is_gbanned(userid)
    reason = get_gban_reason(userid)
    if is_banned:
        msg += "Globally Banned"
        if reason:
            msg += f" with reason** `{reason}`"
        else:
            msg += ".**"
    else:
        msg += "not Globally Banned.**"
    await xx.edit(msg)


@ultroid_cmd(pattern="gblacklist")
async def blacklist_(event):
    await gblacker(event, "add")


@ultroid_cmd(pattern="ungblacklist")
async def ungblacker(event):
    await glacker(event, "remove")


async def gblacker(event, type_):
    chat = (await event.get_chat()).id
    try:
        chat = int(event.text.split(" ", 1)[1])
    except IndexError:
        pass
    try:
        chat_id = (await ultroid.get_entity(chat)).id
    except Exception as e:
        return await eor(event, "**ERROR**\n`{}`".format(str(e)))
    if type_ == "add":
        add_gblacklist(chat_id)
    elif type_ == "remove":
        rem_gblacklist(chat_id)
    await eor(event, "Global Broadcasts: \n{}ed {}".format(type_, chat))
