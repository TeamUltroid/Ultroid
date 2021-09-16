# Ultroid - UserBot
# Copyright (C) 2021 TeamUltroid
#
# This file is a part of < https://github.com/TeamUltroid/Ultroid/ >
# PLease read the GNU Affero General Public License in
# <https://www.github.com/TeamUltroid/Ultroid/blob/main/LICENSE/>.


from pyUltroid.functions.all import get_chatbot_reply
from pyUltroid.functions.chatBot_db import chatbot_stats
from pyUltroid.functions.clean_db import *
from pyUltroid.functions.forcesub_db import *
from pyUltroid.functions.gban_mute_db import *
from pyUltroid.functions.greetings_db import *
from pyUltroid.functions.username_db import *
from telethon.errors.rpcerrorlist import UserNotParticipantError
from telethon.tl.functions.channels import GetParticipantRequest
from telethon.utils import get_display_name

from . import *


@ultroid_bot.on(events.ChatAction())
async def ChatActionsHandler(ult):  # sourcery no-metrics
    # clean chat actions
    if is_clean_added(ult.chat_id):
        try:
            await ult.delete()
        except BaseException:
            pass

    # thank members
    if must_thank(ult.chat_id):
        chat_count = len(await ult.client.get_participants(await ult.get_chat()))
        if chat_count % 100 == 0:
            stik_id = chat_count / 100 - 1
            sticker = stickers[stik_id]
            await ultroid.send_message(ult.chat_id, file=sticker)
    # force subscribe
    if (
        udB.get("FORCESUB")
        and ((ult.user_joined or ult.user_added))
        and get_forcesetting(ult.chat_id)
    ):
        user = await ult.get_user()
        if not user.bot:
            joinchat = get_forcesetting(ult.chat_id)
            try:
                await ultroid_bot(GetParticipantRequest(int(joinchat), user.id))
            except UserNotParticipantError:
                await ultroid_bot.edit_permissions(
                    ult.chat_id, user.id, send_messages=False
                )
                res = await ultroid_bot.inline_query(
                    asst.me.username, f"fsub {user.id}_{joinchat}"
                )
                await res[0].click(ult.chat_id, reply_to=ult.action_message.id)

    # gban checks
    if ult.user_joined or ult.added_by:
        user = await ult.get_user()
        chat = await ult.get_chat()
        reason = is_gbanned(user.id)
        if reason and chat.admin_rights:
            try:
                await ult.client.edit_permissions(
                    chat.id,
                    user.id,
                    view_messages=False,
                )
                gban_watch = f"#GBanned_User Joined.\n\n**User** - [{user.first_name}](tg://user?id={user.id})\n"
                gban_watch += f"**Reason**: {reason}\n\n"
                gban_watch += "`User Banned.`"
                await ult.reply(gban_watch)
            except Exception as er:
                LOGS.info(er)

        # greetings
        elif get_welcome(ult.chat_id):
            user = await ult.get_user()
            chat = await ult.get_chat()
            title = chat.title or "this chat"
            pp = await ult.client.get_participants(chat)
            count = len(pp)
            mention = f"[{get_display_name(user)}](tg://user?id={user.id})"
            name = user.first_name
            last = user.last_name
            fullname = f"{name} {last}" if last else name
            uu = user.username
            username = f"@{uu}" if uu else mention
            wel = get_welcome(ult.chat_id)
            msgg = wel["welcome"]
            med = wel["media"]
            userid = user.id
            if msgg:
                send = await ult.reply(
                    msgg.format(
                        mention=mention,
                        group=title,
                        count=count,
                        name=name,
                        fullname=fullname,
                        username=username,
                        userid=userid,
                    ),
                    file=med,
                )
                await asyncio.sleep(150)
                await send.delete()
            else:
                await ult.reply(file=med)
    elif (ult.user_left or ult.user_kicked) and get_goodbye(ult.chat_id):
        user = await ult.get_user()
        chat = await ult.get_chat()
        title = chat.title or "this chat"
        pp = await ult.client.get_participants(chat)
        count = len(pp)
        mention = f"[{get_display_name(user)}](tg://user?id={user.id})"
        name = user.first_name
        last = user.last_name
        fullname = f"{name} {last}" if last else name
        uu = user.username
        username = f"@{uu}" if uu else mention
        wel = get_goodbye(ult.chat_id)
        msgg = wel["goodbye"]
        med = wel["media"]
        userid = user.id
        if msgg:
            send = await ult.reply(
                msgg.format(
                    mention=mention,
                    group=title,
                    count=count,
                    name=name,
                    fullname=fullname,
                    username=username,
                    userid=userid,
                ),
                file=med,
            )
            await asyncio.sleep(150)
            await send.delete()
        else:
            await ult.reply(file=med)


@ultroid_bot.on(events.NewMessage(incoming=True))
async def chatBot_replies(e):
    sender = await e.get_sender()
    if not isinstance(sender, types.User):
        return
    if e.text and chatbot_stats(e.chat_id, e.sender_id):
        msg = get_chatbot_reply(e, e.message.message)
        if msg:
            await e.reply(msg)
    chat = await e.get_chat()
    if e.is_group and not sender.bot:
        if sender.username:
            await uname_stuff(e.sender_id, sender.username, sender.first_name)
    elif e.is_private and not sender.bot:
        if chat.username:
            await uname_stuff(e.sender_id, chat.username, chat.first_name)


@ultroid_bot.on(events.Raw(types.UpdateUserName))
async def uname_change(e):
    await uname_stuff(e.user_id, e.username, e.first_name)


async def uname_stuff(id, uname, name):
    if udB.get("USERNAME_LOG") == "True":
        old = get_username(id)
        # Ignore Name Logs
        if old and old == uname:
            return
        if old and uname:
            await asst.send_message(
                LOG_CHANNEL,
                f"∆ #UsernameUpdate\n\n@{old} changed username to @{uname}",
            )
        elif old:
            await asst.send_message(
                LOG_CHANNEL,
                f"∆ #UsernameUpdate\n\n[{name}](tg://user?id={id}) removed its username. (@{old})",
            )
        elif uname:
            await asst.send_message(
                LOG_CHANNEL,
                f"∆ #UsernameUpdate\n\n[{name}](tg://user?id={id})'s new username --> @{uname}",
            )
        update_username(id, uname)
