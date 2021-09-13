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

• `{i}tban <time> <reply to msg/ use id>`
    s- seconds | m- minutes
    h- hours |  d- days
    Ban user in current chat with time.

• `{i}pin <reply to message>`
    Pin the message in the chat
    for silent pin use ({i}pin silent).

• `{i}unpin (all) <reply to message>`
    Unpin the messages in the chat.

• `{i}pinned`
   Get pinned message in the current chat.

• `{i}autodelete <24h/7d/1m/off>`
   Enable Auto Delete Messages in Chat.

• `{i}listpinned`
   Get all pinned messages in current chat.

• `{i}purge <reply to message>`
    Purge all messages from the replied message.

• `{i}purgeme <reply to message>`
    Purge Only your messages from the replied message.

• `{i}purgeall`
    Delete all msgs of replied user.
"""

from telethon.errors import BadRequestError
from telethon.errors.rpcerrorlist import ChatNotModifiedError, UserIdInvalidError
from telethon.tl.functions.channels import (
    DeleteUserHistoryRequest,
    GetFullChannelRequest,
)
from telethon.tl.functions.messages import GetFullChatRequest, SetHistoryTTLRequest
from telethon.tl.types import InputMessagesFilterPinned

from . import *


@ultroid_cmd(pattern="promote ?(.*)", admins_only=True, type=["official", "manager"])
async def prmte(ult):
    xx = await eor(ult, get_string("com_1"))
    await ult.get_chat()
    user, rank = await get_user_info(ult)
    if not rank:
        rank = "Admin"
    if not user:
        return await xx.edit("`Reply to a user to promote him!`")
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
            xx,
            f"{inline_mention(user)} `is now an admin in {ult.chat.title} with title {rank}.`",
        )
    except Exception as ex:
        return await xx.edit("`" + str(ex) + "`")


@ultroid_cmd(
    pattern="demote ?(.*)",
    admins_only=True,
    type=["official", "manager"],
)
async def dmote(ult):
    xx = await eor(ult, get_string("com_1"))
    await ult.get_chat()
    user, rank = await get_user_info(ult)
    if not rank:
        rank = "Not Admin"
    if not user:
        return await xx.edit("`Reply to a user to demote him!`")
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
        await eod(
            xx, f"{inline_mention(user)} `is no longer an admin in {ult.chat.title}`"
        )
    except Exception as ex:
        return await xx.edit("`" + str(ex) + "`")


@ultroid_cmd(pattern="ban ?(.*)", admins_only=True, type=["official", "manager"])
async def bban(ult):
    xx = await eor(ult, get_string("com_1"))
    user, reason = await get_user_info(ult)
    if not user:
        return await xx.edit("`Reply to a user or give username to ban him!`")
    if user.id in DEVLIST:
        return await xx.edit(" `LoL, I can't Ban my Developer 😂`")
    try:
        await ult.client.edit_permissions(ult.chat_id, user.id, view_messages=False)
    except BadRequestError:
        return await xx.edit(f"`I don't have the right to ban a user.`")
    except UserIdInvalidError:
        return await xx.edit("`I couldn't get who he is!`")
    senderme = inline_mention(await ult.get_sender())
    try:
        reply = await ult.get_reply_message()
        if reply:
            await reply.delete()
    except BadRequestError:
        return await xx.edit(
            f"{inline_mention(user)}**was banned by** {senderme} **in** `{ult.chat.title}`\n**Reason**: `{reason}`\n**Messages Deleted**: `False`",
        )
    userme = inline_mention(user)
    if reason:
        await xx.edit(
            f"{userme} **was banned by** {senderme} **in** `{ult.chat.title}`\n**Reason**: `{reason}`",
        )
    else:
        await xx.edit(
            f"{userme} **was banned by** {senderme} **in** `{ult.chat.title}`",
        )


@ultroid_cmd(
    pattern="unban ?(.*)",
    admins_only=True,
    type=["official", "manager"],
)
async def uunban(ult):
    xx = await eor(ult, get_string("com_1"))
    user, reason = await get_user_info(ult)
    if not user:
        return await xx.edit("`Reply to a user or give username to unban him!`")
    try:
        await ult.client.edit_permissions(ult.chat_id, user.id, view_messages=True)
    except BadRequestError:
        return await xx.edit("`I don't have the right to unban a user.`")
    except UserIdInvalidError:
        await xx.edit("`I couldn't get who he is!`")
    sender = inline_mention(await ult.get_sender())
    text = (
        f"{inline_mention(user)} **was unbanned by** {sender} **in** `{ult.chat.title}`"
    )
    if reason:
        text += f"\n**Reason**: `{reason}`"
    await xx.edit(text)


@ultroid_cmd(
    pattern="kick ?(.*)",
    admins_only=True,
    type=["official", "manager"],
)
async def kck(ult):
    ml = ult.text.split(" ", maxsplit=1)[0]
    if "kickme" in ult.text:
        return
    xx = await eor(ult, get_string("com_1"))
    user, reason = await get_user_info(ult)
    if not user:
        return await xx.edit("`Kick? Whom? I couldn't get his info...`")
    if user.id in DEVLIST:
        return await xx.edit(" `Lol, I can't Kick my Developer`😂")
    if user.is_self:
        return await xx.edit("`I Cant kick him ever...`")
    try:
        await ult.client.kick_participant(ult.chat_id, user.id)
    except BadRequestError:
        return await xx.edit("`I don't have the right to kick a user.`")
    except Exception as e:
        return await xx.edit(
            f"`I don't have the right to kick a user.`\n\n**ERROR**:\n`{str(e)}`",
        )
    text = f"{inline_mention(user)} **was kicked by** {inline_mention(await ult.get_sender())} **in** `{ult.chat.title}`"
    if reason:
        text += f"\n**Reason**: `{reason}`"
    await xx.edit(text)


@ultroid_cmd(pattern="tban ?(.*)", type=["official", "manager"])
async def tkicki(e):
    huh = e.text.split(" ")
    try:
        tme = huh[1]
    except IndexError:
        return await eor(e, "`Time till kick?`", time=15)
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
        return await eor(e, "`Reply to someone or use its id...`", time=3)
    try:
        bun = await ban_time(e, tme)
        await e.client.edit_permissions(
            e.chat_id, userid, until_date=bun, view_messages=False
        )
        await eod(
            e,
            f"`Successfully Banned` `{fn}` `in {chat.title} for {tme}`",
            time=15,
        )
    except Exception as m:
        return await eor(e, str(m))


@ultroid_cmd(pattern="pin$", type=["official", "manager"])
async def pin(msg):
    if not msg.is_reply:
        return await eor(msg, "Reply a Message to Pin !")
    me = await msg.get_reply_message()
    if me.is_private:
        text = "`Pinned.`"
    else:
        text = f"Pinned [This Message]({me.message_link}) !"
    try:
        await msg.client.pin_message(msg.chat_id, me.id, notify=False)
    except BadRequestError:
        return await eor(msg, "`Hmm.. Guess I have no rights here!`")
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
    msg = ult.reply_to_msg_id
    if msg:
        pass
    elif ch == "all":
        msg = None
    else:
        return await xx.edit(f"Either reply to a message, or, use `{hndlr}unpin all`")
    try:
        await ult.client.unpin_message(ult.chat_id, msg)
    except BadRequestError:
        return await xx.edit("`Hmm.. Guess I have no rights here!`")
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
        return await eor(purg, "`Reply to a message to purge from.`", time=10)
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
            await eor(purg, "`Give a Valid Input.. `", time=5)
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
            "`Reply to someone's msg to delete.`",
        )

    name = (await e.get_reply_message()).sender
    try:
        await e.client(DeleteUserHistoryRequest(e.chat_id, name.id))
        await eor(e, f"Successfully Purged All Messages from {name.first_name}", time=5)
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
        return await eor(event, "No Pinned Message Found!")
    msg = await event.client.get_messages(chat.id, ids=msg_id)
    await eor(event, f"Pinned Message in Current chat is [here]({msg.message_link}).")


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
        return await eor(x, "There is no message pinned in this group!", time=5)

    await x.edit(m + a, parse_mode="html")


@ultroid_cmd(
    pattern="autodelete ?(.*)",
    admins_only=True,
)
async def autodelte(ult):
    match = ult.pattern_match.group(1)
    if not match or match not in ["24h", "7d", "1m", "off"]:
        return await eor(ult, "`Please Use Proper Format..`", time=5)
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
