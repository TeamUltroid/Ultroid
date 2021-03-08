# Ultroid - UserBot
# Copyright (C) 2020 TeamUltroid
#
# This file is a part of < https://github.com/TeamUltroid/Ultroid/ >
# PLease read the GNU Affero General Public License in
# <https://www.github.com/TeamUltroid/Ultroid/blob/main/LICENSE/>.

"""
✘ Commands Available -

• `{i}promote <reply to user/userid/username>`
    Promote the user in the chat.

• `{i}demote <reply to user/userid/username>`
    Demote the user in the chat.

• `{i}ban <reply to user/userid/username> <reason>`
    Ban the user from the chat.

• `{i}unban <reply to user/userid/username> <reason>`
    Unban the user from the chat.

• `{i}kick <reply to user/userid/username> <reason>`
    Kick the user from the chat.

• `{i}pin <reply to message>`
    Pin the message in the chat
    for silent pin use ({i}pin silent).

• `{i}unpin (all) <reply to message>`
    Unpin the message(s) in the chat.

• `{i}purge <reply to message>`
    Purge all messages from the replied message.

• `{i}purgeme <reply to message>`
    Purge Only your messages from the replied message.

• `{i}purgeall <reply to message>`
    Delete all msgs of replied user.

• `{i}del <reply to message>`
    Delete the replied message.

• `{i}edit <new message>`
    Edit your last message.
"""

import asyncio

from telethon.errors import BadRequestError
from telethon.errors.rpcerrorlist import UserIdInvalidError
from telethon.tl.functions.channels import EditAdminRequest, EditBannedRequest
from telethon.tl.types import ChatAdminRights, ChatBannedRights

from . import *


@ultroid_cmd(
    pattern="promote ?(.*)",
    groups_only=True,
)
async def prmte(ult):
    xx = await eor(ult, get_string("com_1"))
    chat = await ult.get_chat()
    isAdmin = chat.admin_rights
    isCreator = chat.creator
    if not isAdmin and not isCreator:
        return await xx.edit("`Hmm, I'm not an admin here...`")
    await xx.edit("`Promoting...`")
    user, rank = await get_user_info(ult)
    if not rank:
        rank = "Admin"
    if not user:
        return await xx.edit("`Reply to a user to promote him!`")
    try:
        await ultroid_bot(
            EditAdminRequest(
                ult.chat_id,
                user.id,
                ChatAdminRights(
                    add_admins=False,
                    invite_users=True,
                    change_info=False,
                    ban_users=True,
                    delete_messages=True,
                    pin_messages=True,
                ),
                rank,
            )
        )
        await xx.edit(
            f"[{user.first_name}](tg://user?id={user.id}) `is now an admin in {ult.chat.title} with title {rank}.`"
        )
    except BadRequestError:
        return await xx.edit("`I don't have the right to promote you.`")
    await asyncio.sleep(5)
    await xx.delete()


@ultroid_cmd(
    pattern="demote ?(.*)",
    groups_only=True,
)
async def dmote(ult):
    xx = await eor(ult, get_string("com_1"))
    chat = await ult.get_chat()
    isAdmin = chat.admin_rights
    isCreator = chat.creator
    if not isAdmin and not isCreator:
        return await xx.edit("`Hmm, I'm not an admin here...`")
    await xx.edit("`Demoting...`")
    user, rank = await get_user_info(ult)
    if not rank:
        rank = "Not Admin"
    if not user:
        return await xx.edit("`Reply to a user to demote him!`")
    try:
        await ultroid_bot(
            EditAdminRequest(
                ult.chat_id,
                user.id,
                ChatAdminRights(
                    add_admins=None,
                    invite_users=None,
                    change_info=None,
                    ban_users=None,
                    delete_messages=None,
                    pin_messages=None,
                ),
                rank,
            )
        )
        await xx.edit(
            f"[{user.first_name}](tg://user?id={user.id}) `is no longer an admin in {ult.chat.title}`"
        )
    except BadRequestError:
        return await xx.edit("`I don't have the right to demote you.`")
    await asyncio.sleep(5)
    await xx.delete()


@ultroid_cmd(
    pattern="ban ?(.*)",
    groups_only=True,
)
async def bban(ult):
    xx = await eor(ult, get_string("com_1"))
    chat = await ult.get_chat()
    isAdmin = chat.admin_rights
    isCreator = chat.creator
    if not isAdmin and not isCreator:
        return await xx.edit("`Hmm, I'm not an admin here...`")
    user, reason = await get_user_info(ult)
    if not user:
        return await xx.edit("`Reply to a user or give username to ban him!`")
    if str(user.id) in DEVLIST:
        return await xx.edit(" `LoL, I can't Ban my Developer 😂`")
    await xx.edit("`Getting user info...`")
    try:
        await ultroid_bot(
            EditBannedRequest(
                ult.chat_id,
                user.id,
                ChatBannedRights(
                    until_date=None,
                    view_messages=True,
                ),
            )
        )
    except BadRequestError:
        return await xx.edit("`I don't have the right to ban a user.`")
    except UserIdInvalidError:
        await xx.edit("`I couldn't get who he is!`")
    try:
        reply = await ult.get_reply_message()
        if reply:
            await reply.delete()
    except BadRequestError:
        return await xx.edit(
            f"[{user.first_name}](tg://user?id={user.id}) **was banned by** [{OWNER_NAME}](tg://user?id={OWNER_ID}) **in** `{ult.chat.title}`\n**Reason**: `{reason}`\n**Messages Deleted**: `False`"
        )
    if reason:
        await xx.edit(
            f"[{user.first_name}](tg://user?id={user.id}) **was banned by** [{OWNER_NAME}](tg://user?id={OWNER_ID}) **in** `{ult.chat.title}`\n**Reason**: `{reason}`"
        )
    else:
        await xx.edit(
            f"[{user.first_name}](tg://user?id={user.id}) **was banned by** [{OWNER_NAME}](tg://user?id={OWNER_ID}) **in** `{ult.chat.title}`"
        )


@ultroid_cmd(
    pattern="unban ?(.*)",
    groups_only=True,
)
async def uunban(ult):
    xx = await eor(ult, get_string("com_1"))
    chat = await ult.get_chat()
    isAdmin = chat.admin_rights
    isCreator = chat.creator
    if not isAdmin and not isCreator:
        return await xx.edit("`Hmm, I'm not an admin here...`")
    user, reason = await get_user_info(ult)
    if not user:
        return await xx.edit("`Reply to a user or give username to unban him!`")
    await xx.edit("`Getting user info...`")
    try:
        await ultroid_bot(
            EditBannedRequest(
                ult.chat_id,
                user.id,
                ChatBannedRights(
                    until_date=None,
                    view_messages=None,
                ),
            )
        )
    except BadRequestError:
        return await xx.edit("`I don't have the right to unban a user.`")
    except UserIdInvalidError:
        await xx.edit("`I couldn't get who he is!`")
    if reason:
        await xx.edit(
            f"[{user.first_name}](tg://user?id={user.id}) **was unbanned by** [{OWNER_NAME}](tg://user?id={OWNER_ID}) **in** `{ult.chat.title}`\n**Reason**: `{reason}`"
        )
    else:
        await xx.edit(
            f"[{user.first_name}](tg://user?id={user.id}) **was unbanned by** [{OWNER_NAME}](tg://user?id={OWNER_ID}) **in** `{ult.chat.title}`"
        )


@ultroid_cmd(
    pattern="kick ?(.*)",
    groups_only=True,
)
async def kck(ult):
    tt = ult.text
    try:
        tx = tt[5]
        if tx:
            return
    except BaseException:
        pass
    xx = await eor(ult, get_string("com_1"))
    chat = await ult.get_chat()
    isAdmin = chat.admin_rights
    isCreator = chat.creator
    if not isAdmin and not isCreator:
        return await xx.edit("`Hmm, I'm not an admin here...`")
    user, reason = await get_user_info(ult)
    if not user:
        return await xx.edit("`Kick? Whom? I couldn't get his info...`")
    if str(user.id) in DEVLIST:
        return await xx.edit(" `Lol, I can't Kick my Developer`😂")
    await xx.edit("`Kicking...`")
    try:
        await ultroid_bot.kick_participant(ult.chat_id, user.id)
        await asyncio.sleep(0.5)
    except BadRequestError:
        return await xx.edit("`I don't have the right to kick a user.`")
    except Exception as e:
        return await xx.edit(
            f"`I don't have the right to kick a user.`\n\n**ERROR**:\n`{str(e)}`"
        )
    if reason:
        await xx.edit(
            f"[{user.first_name}](tg://user?id={user.id})` was kicked by` [{OWNER_NAME}](tg://user?id={OWNER_ID}) `in {ult.chat.title}`\n**Reason**: `{reason}`"
        )
    else:
        await xx.edit(
            f"[{user.first_name}](tg://user?id={user.id})` was kicked by` [{OWNER_NAME}](tg://user?id={OWNER_ID}) `in {ult.chat.title}`"
        )


@ultroid_cmd(
    pattern="pin ?(.*)",
)
async def pin(msg):
    if not msg.is_private:
        # for pin(s) in private messages
        await msg.get_chat()
    cht = await ultroid_bot.get_entity(msg.chat_id)
    xx = msg.reply_to_msg_id
    tt = msg.text
    try:
        kk = tt[4]
        if kk:
            return
    except BaseException:
        pass
    if not msg.is_reply:
        return
    ch = msg.pattern_match.group(1)
    if ch != "silent":
        slnt = True
        x = await eor(msg, get_string("com_1"))
        try:
            await ultroid_bot.pin_message(msg.chat_id, xx, notify=slnt)
        except BadRequestError:
            return await x.edit("`Hmm, I'm have no rights here...`")
        except Exception as e:
            return await x.edit(f"**ERROR:**`{str(e)}`")
        await x.edit(f"`Pinned` [this message](https://t.me/c/{cht.id}/{xx})!")
    else:
        try:
            await ultroid_bot.pin_message(msg.chat_id, xx, notify=False)
        except BadRequestError:
            return await eor(msg, "`Hmm, I'm have no rights here...`")
        except Exception as e:
            return await eor(msg, f"**ERROR:**`{str(e)}`")
        try:
            await msg.delete()
        except BaseException:
            pass


@ultroid_cmd(
    pattern="unpin($| (.*))",
)
async def unp(ult):
    xx = await eor(ult, get_string("com_1"))
    if not ult.is_private:
        # for (un)pin(s) in private messages
        await ult.get_chat()
    ch = (ult.pattern_match.group(1)).strip()
    msg = ult.reply_to_msg_id
    if msg and not ch:
        try:
            await ultroid_bot.unpin_message(ult.chat_id, msg)
        except BadRequestError:
            return await xx.edit("`Hmm, I'm have no rights here...`")
        except Exception as e:
            return await xx.edit(f"**ERROR:**\n`{str(e)}`")
    elif ch == "all":
        try:
            await ultroid_bot.unpin_message(ult.chat_id)
        except BadRequestError:
            return await xx.edit("`Hmm, I'm have no rights here...`")
        except Exception as e:
            return await xx.edit(f"**ERROR:**`{str(e)}`")
    else:
        return await xx.edit(f"Either reply to a message, or, use `{hndlr}unpin all`")
    if not msg and ch != "all":
        return await xx.edit(f"Either reply to a message, or, use `{hndlr}unpin all`")
    await xx.edit("`Unpinned!`")


@ultroid_cmd(
    pattern="purge$",
)
async def fastpurger(purg):
    chat = await purg.get_input_chat()
    msgs = []
    count = 0
    if not purg.reply_to_msg_id:
        return await eod(purg, "`Reply to a message to purge from.`", time=10)
    async for msg in ultroid_bot.iter_messages(chat, min_id=purg.reply_to_msg_id):
        msgs.append(msg)
        count = count + 1
        msgs.append(purg.reply_to_msg_id)
        if len(msgs) == 100:
            await ultroid_bot.delete_messages(chat, msgs)
            msgs = []

    if msgs:
        await ultroid_bot.delete_messages(chat, msgs)
    done = await ultroid_bot.send_message(
        purg.chat_id,
        "__Fast purge complete!__\n**Purged** `" + str(count) + "` **messages.**",
    )
    await asyncio.sleep(5)
    await done.delete()


@ultroid_cmd(
    pattern="purgeme$",
)
async def fastpurgerme(purg):
    chat = await purg.get_input_chat()
    msgs = []
    count = 0
    if not purg.reply_to_msg_id:
        return await eod(purg, "`Reply to a message to purge from.`", time=10)
    async for msg in ultroid_bot.iter_messages(
        chat, from_user="me", min_id=purg.reply_to_msg_id
    ):
        msgs.append(msg)
        count = count + 1
        msgs.append(purg.reply_to_msg_id)
        if len(msgs) == 100:
            await ultroid_bot.delete_messages(chat, msgs)
            msgs = []

    if msgs:
        await ultroid_bot.delete_messages(chat, msgs)
    done = await ultroid_bot.send_message(
        purg.chat_id,
        "__Fast purge complete!__\n**Purged** `" + str(count) + "` **messages.**",
    )
    await asyncio.sleep(5)
    await done.delete()


@ultroid_cmd(
    pattern="purgeall$",
)
async def _(e):
    xx = await eor(e, get_string("com_1"))
    if e.reply_to_msg_id:
        input = (await e.get_reply_message()).sender_id
        (await e.client.get_entity(input)).first_name
        try:
            nos = 0
            async for x in e.client.iter_messages(e.chat_id, from_user=input):
                await e.client.delete_messages(e.chat_id, x)
                nos += 1
            await xx.edit(
                f"**Purged **`{nos}`** msgs of **[{input}](tg://user?id={input})"
            )
        except ValueError:
            return await eod(xx, str(er), time=5)
    else:
        return await eod(
            xx,
            "`Reply to someone's msg to delete.`",
            time=5,
        )


@ultroid_cmd(
    pattern="del$",
)
async def delete_it(delme):
    msg_src = await delme.get_reply_message()
    if delme.reply_to_msg_id:
        try:
            await msg_src.delete()
            await delme.delete()
        except BaseException:
            await eod(
                delme,
                f"Couldn't delete the message.\n\n**ERROR:**\n`{str(e)}`",
                time=5,
            )


@ultroid_cmd(
    pattern="edit",
)
async def editer(edit):
    message = edit.text
    chat = await edit.get_input_chat()
    self_id = await ultroid_bot.get_peer_id("me")
    string = str(message[6:])
    i = 1
    async for message in ultroid_bot.iter_messages(chat, self_id):
        if i == 2:
            await message.edit(string)
            await edit.delete()
            break
        i = i + 1


HELP.update({f"{__name__.split('.')[1]}": f"{__doc__.format(i=HNDLR)}"})
