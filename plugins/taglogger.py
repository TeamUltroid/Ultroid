# Ultroid - UserBot
# Copyright (C) 2021-2022 TeamUltroid
#
# This file is a part of < https://github.com/TeamUltroid/Ultroid/ >
# PLease read the GNU Affero General Public License in
# <https://www.github.com/TeamUltroid/Ultroid/blob/main/LICENSE/>.

"""
- TagLogger
"""

import os
from .. import ultroid_bot, udB, LOGS, asst, get_string
from telethon import events
from telethon.tl.types import User, MessageEntityMention, MessageEntityMentionName
from telethon.tl.custom import Button
from telethon.utils import get_display_name
from telethon.errors import PeerIdInvalidError, ChatWriteForbiddenError, MediaEmptyError, MessageTooLongError, MediaCaptionTooLongError, UserNotParticipantError


CACHE_SPAM = {}
TAG_EDITS = {}


@ultroid_bot.on(
    events.NewMessage(
        incoming=True,
        func=lambda e: (e.mentioned) and udB.get_key("TAG_LOG"),
    ),
)
async def all_messages_catcher(e):
    x = await e.get_sender()
    if isinstance(x, User) and (x.bot or x.verified):
        return
    LOG_CHANNEL = udB.get_config("LOG_CHANNEL")
    NEEDTOLOG = udB.get_key("TAG_LOG")
    buttons = await parse_buttons(e)
    try:
        sent = await asst.send_message(NEEDTOLOG, e.message, buttons=buttons)
        if TAG_EDITS.get(e.chat_id):
            TAG_EDITS[e.chat_id].update({e.id: {"id": sent.id, "msg": e}})
        else:
            TAG_EDITS.update({e.chat_id: {e.id: {"id": sent.id, "msg": e}}})
#        tag_add(sent.id, e.chat_id, e.id)
    except MediaEmptyError as er:
        LOGS.debug(f"handling {er}.")
        try:
            msg = await asst.get_messages(e.chat_id, ids=e.id)
            sent = await asst.send_message(NEEDTOLOG, msg, buttons=buttons)
            if TAG_EDITS.get(e.chat_id):
                TAG_EDITS[e.chat_id].update({e.id: {"id": sent.id, "msg": e}})
            else:
                TAG_EDITS.update({e.chat_id: {e.id: {"id": sent.id, "msg": e}}})
#            tag_add(sent.id, e.chat_id, e.id)
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
    
    # TODO: decide whether to keep

    # @ultroid_bot.on(
    #     events.NewMessage(
    #         outgoing=True,
    #         chats=[udB.get_key("TAG_LOG")],
    #         func=lambda e: e.reply_to,
    #     )
    # )
    # async def idk(e):
    #     id = e.reply_to_msg_id
    #     chat, msg = who_tag(id)
    #     if chat and msg:
    #         try:
    #             await ultroid_bot.send_message(chat, e.message, reply_to=msg)
    #         except BaseException as er:
    #             LOGS.exception(er)


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