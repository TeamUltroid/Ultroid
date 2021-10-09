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

• `{i}gcast <Message> or <reply>`
    Globally Send that msg in all grps.

• `{i}gadmincast <Message> or <reply>`
    Globally Send that msg in grps where you are admin.

• `{i}gucast <Message> or <reply>`
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

from pyUltroid.dB import DEVLIST
from pyUltroid.dB.gban_mute_db import (
    gban,
    gmute,
    is_gbanned,
    is_gmuted,
    list_gbanned,
    ungban,
    ungmute,
)
from pyUltroid.dB.gcast_blacklist_db import (
    add_gblacklist,
    is_gblacklisted,
    rem_gblacklist,
)
from pyUltroid.functions.tools import create_tl_btn, format_btn, get_msg_button
from telethon.tl.functions.channels import EditAdminRequest
from telethon.tl.functions.contacts import BlockRequest, UnblockRequest
from telethon.tl.types import ChatAdminRights

from . import (
    HNDLR,
    LOGS,
    NOSPAM_CHAT,
    OWNER_ID,
    OWNER_NAME,
    eod,
    eor,
    get_string,
    get_user_id,
    ultroid_bot,
    ultroid_cmd,
)
from ._inline import something

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


@ultroid_cmd(pattern="gpromote ?(.*)", fullsudo=True)
async def _(e):
    x = e.pattern_match.group(1)
    ultroid_bot = e.client
    if not x:
        return await eor(e, get_string("schdl_2"), time=5)
    user = await e.get_reply_message()
    if user:
        ev = await eor(e, "`Promoting Replied User Globally`")
        ok = e.text.split()
        key = "all"
        if len(ok) > 1 and (("group" in ok[1]) or ("channel" in ok[1])):
            key = ok[1]
        rank = ok[2] if len(ok) > 2 else "AdMin"
        c = 0
        user.id = user.peer_id.user_id if e.is_private else user.from_id.user_id
        async for x in e.client.iter_dialogs():
            if (
                "group" in key.lower()
                and x.is_group
                or "group" not in key.lower()
                and "channel" in key.lower()
                and x.is_channel
            ):
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
            elif (
                ("group" not in key.lower() or x.is_group)
                and (
                    "group" in key.lower()
                    or "channel" not in key.lower()
                    or x.is_channel
                )
                and (
                    "group" in key.lower()
                    or "channel" in key.lower()
                    or x.is_group
                    or x.is_channel
                )
            ):
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
        await eor(ev, f"Promoted The Replied Users in Total : {c} {key} chats")
    else:
        k = e.text.split()
        if not k[1]:
            return await eor(
                e, "`Give someone's username/id or replied to user.", time=5
            )
        user = k[1]
        if user.isdigit():
            user = int(user)
        try:
            name = await e.client.get_entity(user)
        except BaseException:
            return await eor(e, f"`No User Found Regarding {user}`", time=5)
        ev = await eor(e, f"`Promoting {name.first_name} globally.`")
        key = "all"
        if len(k) > 2 and (("group" in k[2]) or ("channel" in k[2])):
            key = k[2]
        rank = k[3] if len(k) > 3 else "AdMin"
        c = 0
        async for x in e.client.iter_dialogs():
            if (
                "group" in key.lower()
                and x.is_group
                or "group" not in key.lower()
                and "channel" in key.lower()
                and x.is_channel
                or "group" not in key.lower()
                and "channel" not in key.lower()
                and (x.is_group or x.is_channel)
            ):
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
        await eor(ev, f"Promoted {name.first_name} in Total : {c} {key} chats.")


@ultroid_cmd(pattern="gdemote ?(.*)", fullsudo=True)
async def _(e):
    x = e.pattern_match.group(1)
    ultroid_bot = e.client
    if not x:
        return await eor(e, get_string("schdl_2"), time=5)
    user = await e.get_reply_message()
    if user:
        user.id = user.peer_id.user_id if e.is_private else user.from_id.user_id
        ev = await eor(e, "`Demoting Replied User Globally`")
        ok = e.text.split()
        key = "all"
        if len(ok) > 1 and (("group" in ok[1]) or ("channel" in ok[1])):
            key = ok[1]
        rank = "Not AdMin"
        c = 0
        async for x in e.client.iter_dialogs():
            if (
                "group" in key.lower()
                and x.is_group
                or "group" not in key.lower()
                and "channel" in key.lower()
                and x.is_channel
                or "group" not in key.lower()
                and "channel" not in key.lower()
                and (x.is_group or x.is_channel)
            ):
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
        await eor(ev, f"Demoted The Replied Users in Total : {c} {key} chats")
    else:
        k = e.text.split()
        if not k[1]:
            return await eor(
                e, "`Give someone's username/id or replied to user.", time=5
            )
        user = k[1]
        if user.isdigit():
            user = int(user)
        try:
            name = await ultroid_bot.get_entity(user)
        except BaseException:
            return await eor(e, f"`No User Found Regarding {user}`", time=5)
        ev = await eor(e, f"`Demoting {name.first_name} globally.`")
        key = "all"
        if len(k) > 2 and (("group" in k[2]) or ("channel" in k[2])):
            key = k[2]
        rank = "Not AdMin"
        c = 0
        async for x in ultroid_bot.iter_dialogs():
            if (
                "group" in key.lower()
                and x.is_group
                or "group" not in key.lower()
                and "channel" in key.lower()
                and x.is_channel
                or "group" not in key.lower()
                and "channel" not in key.lower()
                and (x.is_group or x.is_channel)
            ):
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
        await eor(ev, f"Demoted {name.first_name} in Total : {c} {key} chats.")


@ultroid_cmd(pattern="ungban ?(.*)", fullsudo=True)
async def _(e):
    xx = await eor(e, "`UnGbanning...`")
    if e.reply_to_msg_id:
        userid = (await e.get_reply_message()).sender_id
    elif e.pattern_match.group(1):
        userid = await get_user_id(e.pattern_match.group(1))
    elif e.is_private:
        userid = e.chat_id
    else:
        return await eor(xx, "`Reply to some msg or add their id.`", time=5)
    try:
        name = (await e.client.get_entity(userid)).first_name
    except BaseException:
        userid = int(userid)
        name = str(userid)
    chats = 0
    async for ggban in e.client.iter_dialogs():
        if ggban.is_group or ggban.is_channel:
            try:
                await e.client.edit_permissions(ggban.id, userid, view_messages=True)
                chats += 1
            except BaseException:
                pass
    ungban(userid)
    try:
        await e.client(UnblockRequest(int(userid)))
    except BaseException:
        pass
    await xx.edit(
        f"`Ungbanned` [{name}](tg://user?id={userid}) `in {chats} common chats.\nRemoved from gbanwatch.`",
    )


@ultroid_cmd(pattern="gban ?(.*)", fullsudo=True)
async def _(e):
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
        userid = e.chat_id
        try:
            reason = e.text.split(" ", maxsplit=1)[1]
        except IndexError:
            reason = ""
    else:
        return await eor(xx, "`Reply to some msg or add their id.`", tome=5, time=5)
    try:
        name = (await e.client.get_entity(userid)).first_name
    except BaseException:
        userid = int(userid)
        name = str(userid)
    chats = 0
    if userid == ultroid_bot.uid:
        return await eor(xx, "`I can't gban myself.`", time=3)
    if userid in DEVLIST:
        return await eor(xx, "`I can't gban my Developers.`", time=3)
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
    gban(userid, reason)
    try:
        await e.client(BlockRequest(int(userid)))
    except BaseException:
        pass
    gb_msg = f"**#Gbanned** [{name}](tg://user?id={userid}) `in {chats} common chats and added to gbanwatch!`"
    if reason:
        gb_msg += f"\n**Reason** - {reason}"
    await xx.edit(gb_msg)


@ultroid_cmd(pattern="g(admin|)cast ?(.*)", fullsudo=True)
async def gcast(event):
    text, btn, reply = "", None, None
    xx = event.pattern_match.group(2)
    if xx:
        msg, btn = get_msg_button(event.text.split(maxsplit=1)[1])
    elif event.is_reply:
        reply = await event.get_reply_message()
        msg = reply.text
        if reply.buttons:
            btn = format_btn(reply.buttons)
        else:
            msg, btn = get_msg_button(msg)
    else:
        return await eor(
            event, "`Give some text to Globally Broadcast or reply a message..`"
        )

    kk = await eor(event, "`Globally Broadcasting Msg...`")
    er = 0
    done = 0
    err = ""
    async for x in event.client.iter_dialogs():
        if x.is_group:
            chat = x.entity.id
            if (
                not is_gblacklisted(chat)
                and int("-100" + str(chat)) not in NOSPAM_CHAT
                and (
                    event.text[2:7] != "admin"
                    or (x.entity.admin_rights or x.entity.creator)
                )
            ):
                try:
                    if btn:
                        bt = create_tl_btn(btn)
                        await something(
                            event,
                            msg,
                            reply.media if reply else None,
                            bt,
                            chat=chat,
                            reply=False,
                        )
                    else:
                        await event.client.send_message(
                            chat, msg, file=reply.media if reply else None
                        )
                    done += 1
                except Exception as h:
                    err += "• " + str(h) + "\n"
                    er += 1
    text += f"Done in {done} chats, error in {er} chat(s)"
    if err != "":
        open("gcast-error.log", "w+").write(err)
        text += f"\nYou can do `{HNDLR}ul gcast-error.log` to know error report."
    await kk.edit(text)


@ultroid_cmd(pattern="gucast ?(.*)", fullsudo=True)
async def gucast(event):
    msg, btn, reply = "", None, None
    xx = event.pattern_match.group(1)
    if xx:
        msg, btn = get_msg_button(event.text.split(maxsplit=1)[1])
    elif event.is_reply:
        reply = await event.get_reply_message()
        msg = reply.text
        if reply.buttons:
            btn = format_btn(reply.buttons)
        else:
            msg, btn = get_msg_button(msg)
    else:
        return await eor(
            event, "`Give some text to Globally Broadcast or reply a message..`"
        )
    kk = await eor(event, "`Globally Broadcasting Msg...`")
    er = 0
    done = 0
    async for x in event.client.iter_dialogs():
        if x.is_user and not x.entity.bot:
            chat = x.id
            if not is_gblacklisted(chat):
                try:
                    if btn:
                        bt = create_tl_btn(btn)
                        await something(
                            event,
                            msg,
                            reply.media if reply else None,
                            bt,
                            chat=chat,
                            reply=False,
                        )
                    else:
                        await event.client.send_message(
                            chat, msg, file=reply.media if reply else None
                        )
                    done += 1
                except BaseException:
                    er += 1
    await kk.edit(f"Done in {done} chats, error in {er} chat(s)")


@ultroid_cmd(pattern="gkick ?(.*)", fullsudo=True)
async def gkick(e):
    xx = await eor(e, "`Gkicking...`")
    if e.reply_to_msg_id:
        userid = (await e.get_reply_message()).sender_id
    elif e.pattern_match.group(1):
        userid = await get_user_id(e.pattern_match.group(1))
    elif e.is_private:
        userid = (await e.get_chat()).id
    else:
        return await eor(xx, "`Reply to some msg or add their id.`", time=5)
    name = (await e.client.get_entity(userid)).first_name
    chats = 0
    if userid == ultroid_bot.uid:
        return await eor(xx, "`I can't gkick myself.`", time=3)
    if userid in DEVLIST:
        return await eor(xx, "`I can't gkick my Developers.`", time=3)
    async for gkick in e.client.iter_dialogs():
        if gkick.is_group or gkick.is_channel:
            try:
                await e.client.kick_participant(gkick.id, userid)
                chats += 1
            except BaseException:
                pass
    await xx.edit(f"`Gkicked` [{name}](tg://user?id={userid}) `in {chats} chats.`")


@ultroid_cmd(pattern="gmute ?(.*)", fullsudo=True)
async def _(e):
    xx = await eor(e, "`Gmuting...`")
    if e.reply_to_msg_id:
        userid = (await e.get_reply_message()).sender_id
    elif e.pattern_match.group(1):
        userid = await get_user_id(e.pattern_match.group(1))
    elif e.is_private:
        userid = (await e.get_chat()).id
    else:
        return await eor(xx, "`Reply to some msg or add their id.`", tome=5, time=5)
    name = (await e.client.get_entity(userid)).first_name
    chats = 0
    if userid == ultroid_bot.uid:
        return await eor(xx, "`I can't gmute myself.`", time=3)
    if userid in DEVLIST:
        return await eor(xx, "`I can't gmute my Developers.`", time=3)
    if is_gmuted(userid):
        return await eor(xx, "`User is already gmuted.`", time=4)
    async for onmute in e.client.iter_dialogs():
        if onmute.is_group:
            try:
                await e.client.edit_permissions(onmute.id, userid, send_messages=False)
                chats += 1
            except BaseException:
                pass
    gmute(userid)
    await xx.edit(f"`Gmuted` [{name}](tg://user?id={userid}) `in {chats} chats.`")


@ultroid_cmd(pattern="ungmute ?(.*)", fullsudo=True)
async def _(e):
    xx = await eor(e, "`UnGmuting...`")
    if e.reply_to_msg_id:
        userid = (await e.get_reply_message()).sender_id
    elif e.pattern_match.group(1):
        userid = await get_user_id(e.pattern_match.group(1))
    elif e.is_private:
        userid = (await e.get_chat()).id
    else:
        return await eor(xx, "`Reply to some msg or add their id.`", time=5)
    name = (await e.client.get_entity(userid)).first_name
    chats = 0
    if not is_gmuted(userid):
        return await eor(xx, "`User is not gmuted.`", time=3)
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
    pattern="listgban$",
)
async def list_gengbanned(event):
    users = list_gbanned()
    x = await eor(event, get_string("com_1"))
    msg = ""
    if not users:
        return await x.edit("`You haven't GBanned anyone!`")
    for i in users:
        try:
            name = (await ultroid_bot.get_entity(int(i))).first_name
        except BaseException:
            name = i
        msg += f"<strong>User</strong>: <a href=tg://user?id={i}>{name}</a>\n"
        reason = users[i]
        msg += f"<strong>Reason</strong>: {reason}\n\n" if reason is not None else "\n"
    gbanned_users = f"<strong>List of users GBanned by {OWNER_NAME}</strong>:\n\n{msg}"
    if len(gbanned_users) > 4096:
        with open("gbanned.txt", "w") as f:
            f.write(
                gbanned_users.replace("<strong>", "")
                .replace("</strong>", "")
                .replace("<a href=tg://user?id=", "")
                .replace("</a>", "")
            )
        await x.reply(
            file="gbanned.txt",
            message=f"List of users GBanned by [{OWNER_NAME}](tg://user?id={OWNER_ID})",
        )
        os.remove("gbanned.txt")
        await x.delete()
    else:
        await x.edit(gbanned_users, parse_mode="html")


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
        try:
            userid = await get_user_id(e.pattern_match.group(1))
        except Exception as err:
            return await eor(xx, f"{err}", time=10)
    else:
        return await eor(xx, "`Reply to some msg or add their id.`", time=5)
    name = (await e.client.get_entity(userid)).first_name
    msg = "**" + name + " is "
    is_banned = is_gbanned(userid)
    reason = list_gbanned().get(userid)
    if is_banned:
        msg += "Globally Banned"
        msg += f" with reason** `{reason}`" if reason else ".**"
    else:
        msg += "not Globally Banned.**"
    await xx.edit(msg)


@ultroid_cmd(pattern="gblacklist")
async def blacklist_(event):
    await gblacker(event, "add")


@ultroid_cmd(pattern="ungblacklist")
async def ungblacker(event):
    await gblacker(event, "remove")


async def gblacker(event, type_):
    chat = (await event.get_chat()).id
    try:
        chat = int(event.text.split(" ", 1)[1])
    except IndexError:
        pass
    try:
        chat_id = (await ultroid_bot.get_entity(chat)).id
    except Exception as e:
        return await eor(event, "**ERROR**\n`{}`".format(str(e)))
    if type_ == "add":
        add_gblacklist(chat_id)
    elif type_ == "remove":
        rem_gblacklist(chat_id)
    await eor(event, "Global Broadcasts: \n{}ed {}".format(type_, chat))
