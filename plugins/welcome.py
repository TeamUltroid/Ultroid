from pyUltroid.functions.welcome_db import *
from telethon.utils import get_display_name, pack_bot_file_id

from . import *


@ultroid_cmd(pattern="setwelcome")
async def setwel(event):
    x = await eor(event, get_string("com_1"))
    r = await event.get_reply_message()
    if event.is_private:
        return await eod(x, "Please use this in a group and not PMs!", time=10)
    if r and r.media:
        add_welcome(event.chat_id, r.message, pack_bot_file_id(r.media))
        await eor(x, "`Welcome note saved`")
    else:
        add_welcome(event.chat_id, event.text.split(" ", maxsplit=1)[1], None)
        await eor(x, "`Welcome note saved`")


@ultroid_cmd(pattern="clearwelcome$")
async def clearwel(event):
    prv = get_welcome(event.chat_id)
    if prv is None:
        await eod(event, "`No welcome was set!`", time=5)
    delete_welcome(event.chat_id)
    await eod(event, "`Welcome Note Deleted`")


@ultroid_cmd(pattern="listwelcome$")
async def listwel(event):
    prv, prc = get_welcome(event.chat_id)
    if get_welcome(event.chat_id) is None:
        await eod(event, "`No welcome was set!`", time=5)
    await event.reply(f"**Welcome Note in this chat**\n\n`{prv}`", file=prc)
    await event.delete()


@ultroid_bot.on(events.ChatAction())
async def _(event):
    wel, med = get_welcome(event.chat_id)
    if get_welcome(event.chat_id):
        if event.user_joined:
            user = await event.get_user()
            chat = await event.get_chat()
            title = chat.title if chat.title else "this chat"
            pp = await event.client.get_participants(chat)
            count = len(pp)
            mention = f"[{get_display_name(user)}](tg://user?id={user.id})"
            name = user.first_name
            last = user.last_name
            if last:
                fullname = f"{name} {last}"
            else:
                fullname = name
            uu = user.username
            if uu:
                username = f"@{uu}"
            else:
                username = mention
            userid = user.id
            await event.reply(
                wel.format(
                    mention=mention,
                    title=title,
                    count=count,
                    name=name,
                    fullname=fullname,
                    username=username,
                    userid=userid,
                ),
                file=med,
            )
