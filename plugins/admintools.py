# Ultroid - UserBot
# Copyright (C) 2021 TeamUltroid
#
# This file is a part of < https://github.com/TeamUltroid/Ultroid/ >
# PLease read the GNU Affero General Public License in
# <https://www.github.com/TeamUltroid/Ultroid/blob/main/LICENSE/>.
"""
✘ Commands Available -

• `{i}promote <reply to user/userid/username>`
• `{i}demote`
    Promote/Demote the user in the chat.

• `{i}ban <reply to user/userid/username> <reason>`
• `{i}unban`
    Ban/Unban the user from the chat.

• `{i}kick <reply to user/userid/username> <reason>`
    Kick the user from the chat.

• `{i}pin <reply to message>`
    Pin the message in the chat
• `{i}unpin (all) <reply to message>`
    Unpin the messages in the chat.

• `{i}pinned`
   Get pinned message in the current chat.
• `{i}listpinned`
   Get all pinned messages in current chat

• `{i}autodelete <24h/7d/1m/off>`
   Enable Auto Delete Messages in Chat.

• `{i}purge <reply to message>`
    Purge all messages from the replied message.

• `{i}purgeme <reply to message>`
    Purge Only your messages from the replied message.

• `{i}purgeall`
    Delete all msgs of replied user.
"""

from pyUltroid.dB import DEVLIST
from pyUltroid.functions.admins import ban_time
from telethon.errors import BadRequestError
from telethon.errors.rpcerrorlist import ChatNotModifiedError, UserIdInvalidError
from telethon.tl.functions.channels import (
    DeleteUserHistoryRequest,
    GetFullChannelRequest,
)
from telethon.tl.functions.messages import GetFullChatRequest, SetHistoryTTLRequest
from telethon.tl.types import InputMessagesFilterPinned

from . import (
    HNDLR,
    LOGS,
    eod,
    eor,
    get_string,
    get_uinfo,
    get_user_id,
    inline_mention,
    types,
    ultroid_bot,
    ultroid_cmd,
)


@ultroid_cmd(pattern="promote ?(.*)", admins_only=True, type=["official", "manager"])
async def prmte(ult):
    xx = await eor(ult, get_string("com_1"))
    await ult.get_chat()
    user, rank = await get_uinfo(ult)
    rank = rank or "Admin"
    if not user:
        return await xx.edit(get_string("pro_1"))
    try:
        await ult.client.edit_admin(
            ult.chat_id,
            user.id,
            invite_users=True,
            ban_users=True,
            delete_messages=True,
            pin_messages=True,
            manage_call=True,
            title=rank,
        )
        await eod(
            xx, get_string("pro_2").format(inline_mention(user), ult.chat.title, rank)
        )
    except Exception as ex:
        return await xx.edit(f"`{ex}`")


@ultroid_cmd(
    pattern="demote ?(.*)",
    admins_only=True,
    type=["official", "manager"],
)
async def dmote(ult):
    xx = await eor(ult, get_string("com_1"))
    await ult.get_chat()
    user, rank = await get_uinfo(ult)
    if not rank:
        rank = "Not Admin"
    if not user:
        return await xx.edit(get_string("de_1"))
    try:
        await ult.client.edit_admin(
            ult.chat_id,
            user.id,
            invite_users=None,
            ban_users=None,
            delete_messages=None,
            pin_messages=None,
            manage_call=None,
            title=rank,
        )
        await eod(xx, get_string("de_2").format(inline_mention(user), ult.chat.title))
    except Exception as ex:
        return await xx.edit(f"`{ex}`")


@ultroid_cmd(
    pattern="ban ?(.*)",
    admins_only=True,
    type=["official", "manager"],
)
async def bban(ult):
    user, reason = await get_uinfo(ult)
    if not user:
        return await eod(ult, get_string("ban_1"))
    if user.id in DEVLIST:
        return await eod(ult, get_string("ban_2"))
    try:
        await ult.client.edit_permissions(ult.chat_id, user.id, view_messages=False)
    except BadRequestError:
        return await eod(ult, get_string("ban_3"))
    except UserIdInvalidError:
        return await eod(ult, get_string("adm_1"))
    senderme = inline_mention(await ult.get_sender())
    userme = inline_mention(user)
    text = get_string("ban_4").format(userme, senderme, ult.chat.title)
    if reason:
        text += get_string("ban_5").format(reason)
    await eod(ult, text)


@ultroid_cmd(
    pattern="unban ?(.*)",
    admins_only=True,
    type=["official", "manager"],
)
async def uunban(ult):
    xx = await eor(ult, get_string("com_1"))
    if ult.text[1:].startswith("unbanall"):
        return
    user, reason = await get_uinfo(ult)
    if not user:
        return await xx.edit(get_string("unban_1"))
    try:
        await ult.client.edit_permissions(ult.chat_id, user.id, view_messages=True)
    except BadRequestError:
        return await xx.edit(get_string("adm_2"))
    except UserIdInvalidError:
        await xx.edit(get_string("adm_1"))
    sender = inline_mention(await ult.get_sender())
    text = get_string("unban_3").format(user, sender, ult.chat.title)
    if reason:
        text += get_string("ban_5").format(reason)
    await xx.edit(text)


@ultroid_cmd(
    pattern="kick ?(.*)",
    admins_only=True,
    type=["official", "manager"],
)
async def kck(ult):
    if "kickme" in ult.text:
        return
    ml = ult.text.split(" ", maxsplit=1)[0]
    xx = await eor(ult, get_string("com_1"))
    user, reason = await get_uinfo(ult)
    if not user:
        return await xx.edit(get_string("adm_1"))
    if user.id in DEVLIST:
        return await xx.edit(get_string("kick_2"))
    if user.is_self:
        return await xx.edit(get_string("kick_3"))
    try:
        await ult.client.kick_participant(ult.chat_id, user.id)
    except BadRequestError as er:
        LOGS.info(er)
        return await xx.edit(get_string("kick_1"))
    except Exception as e:
        LOGS.exception(e)
    text = get_string("kick_4").format(
        inline_mention(user), inline_mention(await ult.get_sender()), ult.chat.title
    )
    if reason:
        text += get_string("ban_5").format(reason)
    await xx.edit(text)


@ultroid_cmd(pattern="tban ?(.*)", type=["official", "manager"])
async def tkicki(e):
    huh = e.text.split(" ")
    try:
        tme = huh[1]
    except IndexError:
        return await eor(e, get_string("adm_3"), time=15)
    try:
        inputt = huh[2]
    except IndexError:
        pass
    chat = await e.get_chat()
    if e.is_reply:
        replied = await e.get_reply_message()
        userid = replied.sender_id
        fn = (await e.get_sender()).first_name
    elif inputt:
        userid = await get_user_id(inputt)
        fn = (await e.client.get_entity(userid)).first_name
    else:
        return await eor(e, get_string("tban_1"), time=3)
    try:
        bun = await ban_time(e, tme)
        await e.client.edit_permissions(
            e.chat_id, userid, until_date=bun, view_messages=False
        )
        await eod(
            e,
            get_string("tban_2").format(fn, chat.title, tme),
            time=15,
        )
    except Exception as m:
        return await eor(e, str(m))


@ultroid_cmd(pattern="pin$", type=["official", "manager"])
async def pin(msg):
    if not msg.is_reply:
        return await eor(msg, get_string("pin_1"))
    me = await msg.get_reply_message()
    if me.is_private:
        text = "`Pinned.`"
    else:
        text = f"Pinned [This Message]({me.message_link}) !"
    try:
        await msg.client.pin_message(msg.chat_id, me.id, notify=False)
    except BadRequestError:
        return await eor(msg, get_string("adm_2"))
    except Exception as e:
        return await eor(msg, f"**ERROR:**`{e}`")
    await eor(msg, text)


@ultroid_cmd(
    pattern="unpin($| (.*))",
    type=["official", "manager"],
)
async def unp(ult):
    xx = await eor(ult, get_string("com_1"))
    ch = (ult.pattern_match.group(1)).strip()
    msg = None
    if ult.is_reply:
        msg = ult.reply_to_msg_id
    elif ch != "all":
        return await xx.edit(get_string("unpin_1").format(HNDLR))
    try:
        await ult.client.unpin_message(ult.chat_id, msg)
    except BadRequestError:
        return await xx.edit(get_string("adm_2"))
    except Exception as e:
        return await xx.edit(f"**ERROR:**`{e}`")
    await xx.edit("`Unpinned!`")


@ultroid_cmd(
    pattern="purge ?(.*)",
    type=["official", "manager"],
)
async def fastpurger(purg):
    match = purg.pattern_match.group(1)
    try:
        ABC = purg.text[6]
    except IndexError:
        ABC = None
    if ABC and purg.text[6] in ["m", "a"]:
        return
    if not purg._client._bot and ((match) or (purg.is_reply and purg.is_private)):
        p = 0
        async for msg in purg.client.iter_messages(
            purg.chat_id,
            limit=int(match) if match else None,
            min_id=purg.reply_to_msg_id if purg.is_reply else None,
        ):
            await msg.delete()
            p += 0
        return await eor(purg, f"Purged {p} Messages! ", time=5)
    if not purg.reply_to_msg_id:
        return await eor(purg, get_string("purge_1"), time=10)
    try:
        await purg.client.delete_messages(
            purg.chat_id, [a for a in range(purg.reply_to_msg_id, purg.id + 1)]
        )
    except Exception as er:
        LOGS.info(er)
    await purg.respond(
        "__Fast purge complete!__",
    )


@ultroid_cmd(
    pattern="purgeme ?(.*)",
)
async def fastpurgerme(purg):
    num = purg.pattern_match.group(1)
    if num and not purg.is_reply:
        try:
            nnt = int(num)
        except BaseException:
            await eor(purg, get_string("com_3"), time=5)
            return
        mp = 0
        async for mm in purg.client.iter_messages(
            purg.chat_id, limit=nnt, from_user="me"
        ):
            await mm.delete()
            mp += 1
        await eor(purg, f"Purged {mp} Messages!", time=5)
        return
    chat = await purg.get_input_chat()
    msgs = []
    count = 0
    if not (purg.reply_to_msg_id or num):
        return await eod(
            purg,
            "`Reply to a message to purge from or use it like ``purgeme <num>`",
            time=10,
        )
    async for msg in purg.client.iter_messages(
        chat,
        from_user="me",
        min_id=purg.reply_to_msg_id,
    ):
        msgs.append(msg)
        count += 1
        msgs.append(purg.reply_to_msg_id)
        if len(msgs) == 100:
            await ultroid_bot.delete_messages(chat, msgs)
            msgs = []

    if msgs:
        await purg.client.delete_messages(chat, msgs)
    await eod(
        purg,
        "__Fast purge complete!__\n**Purged** `" + str(count) + "` **messages.**",
    )


@ultroid_cmd(
    pattern="purgeall$",
)
async def _(e):
    if not e.is_reply:
        return await eod(
            e,
            get_string("purgeall_1"),
        )

    name = (await e.get_reply_message()).sender
    try:
        await e.client(DeleteUserHistoryRequest(e.chat_id, name.id))
        await eor(e, get_string("purgeall_2").format(name.first_name), time=5)
    except Exception as er:
        return await eor(e, str(er), time=5)


@ultroid_cmd(pattern="pinned", type=["official", "manager"], groups_only=True)
async def djshsh(event):
    chat = await event.get_chat()
    if isinstance(chat, types.Chat):
        FChat = await event.client(GetFullChatRequest(chat.id))
    elif isinstance(chat, types.Channel):
        FChat = await event.client(GetFullChannelRequest(chat.id))
    else:
        return
    msg_id = FChat.full_chat.pinned_msg_id
    if not msg_id:
        return await eor(event, get_string("pinned_1"))
    msg = await event.client.get_messages(chat.id, ids=msg_id)
    if msg:
        await eor(
            event, f"Pinned Message in Current chat is [here]({msg.message_link})."
        )


@ultroid_cmd(
    pattern="listpinned$",
)
async def get_all_pinned(event):
    x = await eor(event, get_string("com_1"))
    chat_id = (str(event.chat_id)).replace("-100", "")
    chat_name = (await event.get_chat()).title
    a = ""
    c = 1
    async for i in event.client.iter_messages(
        event.chat_id, filter=InputMessagesFilterPinned
    ):
        if i.message:
            t = " ".join(i.message.split()[0:4])
            txt = "{}....".format(t)
        else:
            txt = "Go to message."
        a += f"{c}. <a href=https://t.me/c/{chat_id}/{i.id}>{txt}</a>\n"
        c += 1

    if c == 1:
        m = f"<b>The pinned message in {chat_name}:</b>\n\n"
    else:
        m = f"<b>List of pinned message(s) in {chat_name}:</b>\n\n"

    if a == "":
        return await eor(x, get_string("listpin_1"), time=5)

    await x.edit(m + a, parse_mode="html")


@ultroid_cmd(
    pattern="autodelete ?(.*)",
    admins_only=True,
)
async def autodelte(ult):
    match = ult.pattern_match.group(1)
    if not match or match not in ["24h", "7d", "1m", "off"]:
        return await eor(ult, "`Please Use in Proper Format..`", time=5)
    if match == "24h":
        tt = 3600 * 24
    elif match == "7d":
        tt = 3600 * 24 * 7
    elif match == "1m":
        tt = 3600 * 24 * 31
    else:
        tt = 0
    try:
        await ult.client(SetHistoryTTLRequest(ult.chat_id, period=tt))
    except ChatNotModifiedError:
        return await eor(
            ult, f"Auto Delete Setting is Already same to `{match}`", time=5
        )
    await eor(ult, f"Auto Delete Status Changed to `{match}` !")
