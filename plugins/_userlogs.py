# Ultroid - UserBot
# Copyright (C) 2021-2024 TeamUltroid
#
# This file is a part of < https://github.com/TeamUltroid/Ultroid/ >
# PLease read the GNU Affero General Public License in
# <https://www.github.com/TeamUltroid/Ultroid/blob/main/LICENSE/>.

import os
import re

from telethon.errors.rpcerrorlist import (
    ChannelPrivateError,
    ChatWriteForbiddenError,
    MediaCaptionTooLongError,
    MediaEmptyError,
    MessageTooLongError,
    PeerIdInvalidError,
    UserNotParticipantError,
)
from telethon.tl.types import MessageEntityMention, MessageEntityMentionName, User
from telethon.utils import get_display_name

from pyUltroid.dB.botchat_db import tag_add, who_tag

from . import (
    LOG_CHANNEL,
    LOGS,
    Button,
    asst,
    callback,
    events,
    get_string,
    inline_mention,
    udB,
    ultroid_bot,
)

CACHE_SPAM = {}
TAG_EDITS = {}


@ultroid_bot.on(
    events.NewMessage(
        incoming=True,
        func=lambda e: (e.mentioned),
    ),
)
async def all_messages_catcher(e):
    x = await e.get_sender()
    if isinstance(x, User) and (x.bot or x.verified):
        return
    if not udB.get_key("TAG_LOG"):
        return
    NEEDTOLOG = udB.get_key("TAG_LOG")
    buttons = await parse_buttons(e)
    try:
        sent = await asst.send_message(NEEDTOLOG, e.message, buttons=buttons)
        if TAG_EDITS.get(e.chat_id):
            TAG_EDITS[e.chat_id].update({e.id: {"id": sent.id, "msg": e}})
        else:
            TAG_EDITS.update({e.chat_id: {e.id: {"id": sent.id, "msg": e}}})
        tag_add(sent.id, e.chat_id, e.id)
    except MediaEmptyError as er:
        LOGS.debug(f"handling {er}.")
        try:
            msg = await asst.get_messages(e.chat_id, ids=e.id)
            sent = await asst.send_message(NEEDTOLOG, msg, buttons=buttons)
            if TAG_EDITS.get(e.chat_id):
                TAG_EDITS[e.chat_id].update({e.id: {"id": sent.id, "msg": e}})
            else:
                TAG_EDITS.update({e.chat_id: {e.id: {"id": sent.id, "msg": e}}})
            tag_add(sent.id, e.chat_id, e.id)
        except Exception as me:
            if not isinstance(me, (PeerIdInvalidError, ValueError)):
                LOGS.exception(me)
            if e.photo or e.sticker or e.gif:
                try:
                    media = await e.download_media()
                    sent = await asst.send_message(
                        NEEDTOLOG, e.message.text, file=media, buttons=buttons
                    )
                    if TAG_EDITS.get(e.chat_id):
                        TAG_EDITS[e.chat_id].update({e.id: {"id": sent.id, "msg": e}})
                    else:
                        TAG_EDITS.update({e.chat_id: {e.id: {"id": sent.id, "msg": e}}})
                    return os.remove(media)
                except Exception as er:
                    LOGS.exception(er)
            await asst.send_message(NEEDTOLOG, get_string("com_4"), buttons=buttons)
    except (PeerIdInvalidError, ValueError) as er:
        LOGS.exception(er)
        try:
            CACHE_SPAM[NEEDTOLOG]
        except KeyError:
            await asst.send_message(
                udB.get_key("LOG_CHANNEL"), get_string("userlogs_1")
            )
            CACHE_SPAM.update({NEEDTOLOG: True})
    except ChatWriteForbiddenError:
        try:
            await asst.get_permissions(NEEDTOLOG, "me")
            MSG = get_string("userlogs_4")
        except UserNotParticipantError:
            MSG = get_string("userlogs_2")
        try:
            CACHE_SPAM[NEEDTOLOG]
        except KeyError:
            await asst.send_message(LOG_CHANNEL, MSG)
            CACHE_SPAM.update({NEEDTOLOG: True})
    except Exception as er:
        LOGS.exception(er)


if udB.get_key("TAG_LOG"):

    @ultroid_bot.on(events.MessageEdited(func=lambda x: not x.out))
    async def upd_edits(event):
        x = event.sender
        if isinstance(x, User) and (x.bot or x.verified):
            return
        if event.chat_id not in TAG_EDITS:
            if event.sender_id == udB.get_key("TAG_LOG"):
                return
            if event.is_private:
                return
            if entities := event.get_entities_text():
                is_self = False
                username = event.client.me.username
                if username:
                    username = username.lower()
                for ent, text in entities:
                    if isinstance(ent, MessageEntityMention):
                        is_self = text[1:].lower() == username
                    elif isinstance(ent, MessageEntityMentionName):
                        is_self = ent.user_id == event.client.me.id
                if is_self:
                    text = f"**#Edited & #Mentioned**\n\n{event.text}"
                    try:
                        sent = await asst.send_message(
                            udB.get_key("TAG_LOG"),
                            text,
                            buttons=await parse_buttons(event),
                        )
                    except Exception as er:
                        return LOGS.exception(er)
                    if TAG_EDITS.get(event.chat_id):
                        TAG_EDITS[event.chat_id].update({event.id: {"id": sent.id}})
                    else:
                        TAG_EDITS.update({event.chat_id: {event.id: {"id": sent.id}}})
            return
        d_ = TAG_EDITS[event.chat_id]
        if not d_.get(event.id):
            return
        d_ = d_[event.id]
        if d_["msg"].text == event.text:
            return
        msg = None
        if d_.get("count"):
            d_["count"] += 1
        else:
            msg = True
            d_.update({"count": 1})
        if d_["count"] > 10:
            return  # some limit to take edits
        try:
            MSG = await asst.get_messages(udB.get_key("TAG_LOG"), ids=d_["id"])
        except Exception as er:
            return LOGS.exception(er)
        TEXT = MSG.text
        if msg:
            TEXT += "\n\n🖋 **Later Edited to !**"
        strf = event.edit_date.strftime("%H:%M:%S")
        if "\n" not in event.text:
            TEXT += f"\n• `{strf}` : {event.text}"
        else:
            TEXT += f"\n• `{strf}` :\n-> {event.text}"
        if d_["count"] == 10:
            TEXT += "\n\n• __Only the first 10 Edits are shown.__"
        try:
            msg = await MSG.edit(TEXT, buttons=await parse_buttons(event))
            d_["msg"] = msg
        except (MessageTooLongError, MediaCaptionTooLongError):
            del TAG_EDITS[event.chat_id][event.id]
        except Exception as er:
            LOGS.exception(er)

    @ultroid_bot.on(
        events.NewMessage(
            outgoing=True,
            chats=[udB.get_key("TAG_LOG")],
            func=lambda e: e.reply_to,
        )
    )
    async def idk(e):
        id = e.reply_to_msg_id
        chat, msg = who_tag(id)
        if chat and msg:
            try:
                await ultroid_bot.send_message(chat, e.message, reply_to=msg)
            except BaseException as er:
                LOGS.exception(er)


# log for assistant/user joins/add


async def when_added_or_joined(event):
    user = await event.get_user()
    chat = await event.get_chat()
    if not (user and user.is_self):
        return
    if getattr(chat, "username", None):
        chat = f"[{chat.title}](https://t.me/{chat.username}/{event.action_message.id})"
    else:
        chat = f"[{chat.title}](https://t.me/c/{chat.id}/{event.action_message.id})"
    key = "bot" if event.client._bot else "user"
    buttons = Button.inline(
        get_string("userlogs_3"), data=f"leave_ch_{event.chat_id}|{key}"
    )
    if event.user_added:
        tmp = event.added_by
        text = f"#ADD_LOG\n\n{inline_mention(tmp)} just added {inline_mention(user)} to {chat}."
    elif event.from_request:
        text = f"#APPROVAL_LOG\n\n{inline_mention(user)} just got Chat Join Approval to {chat}."
    else:
        text = f"#JOIN_LOG\n\n{inline_mention(user)} just joined {chat}."
    await asst.send_message(udB.get_key("LOG_CHANNEL"), text, buttons=buttons)


asst.add_event_handler(
    when_added_or_joined, events.ChatAction(func=lambda x: x.user_added)
)
ultroid_bot.add_event_handler(
    when_added_or_joined,
    events.ChatAction(func=lambda x: x.user_added or x.user_joined),
)
_client = {"bot": asst, "user": ultroid_bot}


@callback(
    re.compile(
        "leave_ch_(.*)",
    ),
    from_users=[ultroid_bot.uid],
)
async def leave_ch_at(event):
    cht = event.data_match.group(1).decode("UTF-8")
    ch_id, client = cht.split("|")
    try:
        client = _client[client]
    except KeyError:
        return
    try:
        name = (await client.get_entity(int(ch_id))).title
        await client.delete_dialog(int(ch_id))
    except UserNotParticipantError:
        pass
    except ChannelPrivateError:
        return await event.edit(
            "`[CANT_ACCESS_CHAT]` `Maybe already left or got banned.`"
        )
    except Exception as er:
        LOGS.exception(er)
        return await event.answer(str(er))
    await event.edit(get_string("userlogs_5").format(name))


@callback("do_nothing")
async def _(event):
    await event.answer()


async def parse_buttons(event):
    y, x = event.chat, event.sender
    where_n, who_n = get_display_name(y), get_display_name(x)
    where_l = event.message_link
    buttons = [[Button.url(where_n, where_l)]]
    if isinstance(x, User) and x.username:
        try:
            buttons.append(
                [Button.mention(who_n, await asst.get_input_entity(x.username))]
            )
        except Exception as er:
            LOGS.exception(er)
            buttons.append([Button.url(who_n, f"t.me/{x.username}")])
    elif getattr(x, "username"):
        buttons.append([Button.url(who_n, f"t.me/{x.username}")])
    else:
        buttons.append([Button.url(who_n, where_l)])
    replied = await event.get_reply_message()
    if replied and replied.out:
        button = Button.url("Replied to", replied.message_link)
        if len(who_n) > 7:
            buttons.append([button])
        else:
            buttons[-1].append(button)
    return buttons
