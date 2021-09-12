# Ultroid - UserBot
# Copyright (C) 2020 TeamUltroid
#
# This file is a part of < https://github.com/TeamUltroid/Ultroid/ >
# PLease read the GNU Affero General Public License in
# <https://www.github.com/TeamUltroid/Ultroid/blob/main/LICENSE/>.

"""
✘ Commands Available -

• `{i}addai <reply to user/give username/userid>`
   Add a AI ChatBot to reply to that user.

• `{i}remai <reply to user/give username/userid>`
   Remove the AI ChatBot.

• `{i}repai <reply to user/give a message>`
   Reply to the user with a message by an AI.

• `{i}listai`
   List the currently AI added users.
"""

from pyUltroid.functions.all import get_chatbot_reply
from pyUltroid.functions.chatBot_db import *


@ultroid_cmd(pattern="repai")
async def im_lonely_chat_with_me(event):
    if event.reply_to_msg_id:
        message = (await event.get_reply_message()).message
    else:
        try:
            message = event.text.split(" ", 1)[1]
        except IndexError:
            return await eod(
                event, "Give a message or Reply to a User's Message.", time=10
            )
    reply_ = get_chatbot_reply(event, message=message)
    await eor(event, reply_)


@ultroid_cmd(pattern="addai")
async def add_chatBot(event):
    await chat_bot_fn(event, type_="add")


@ultroid_cmd(pattern="remai")
async def rem_chatBot(event):
    await chat_bot_fn(event, type_="remov")


@ultroid_cmd(pattern="listai")
async def lister(event):
    users = get_all_added(event.chat.id)
    if udB.get("CHATBOT_USERS") is None:
        return await eor(event, "`No user has AI added.`", time=5)
    msg = ""
    for i in users:
        try:
            user = await event.client.get_entity(int(i))
            user = inline_mention(user)
        except BaseException:
            user = f"`{i}`"
        msg += "- {}\n".format(user)
    await eor(event, msg, link_preview=False)


async def chat_bot_fn(event, type_):
    if event.reply_to_msg_id:
        user = (await event.get_reply_message()).sender
    else:
        temp = event.text.split(maxsplit=1)
        try:
            user = await event.client.get_entity(temp[1])
        except BaseException:
            if event.is_private:
                user = event.chat
            else:
                return await eod(
                    event,
                    "Reply to a user or give me his id/username to add an AI ChatBot!",
                )
    if type_ == "add":
        add_chatbot(event.chat_id, user.id)
    if type_ == "remov":
        rem_chatbot(event.chat_id, user.id)
    await eor(
        event, f"**ChatBot:**\n{type_}ed [{user.first_name}](tg://user?id={user.id})"
    )
