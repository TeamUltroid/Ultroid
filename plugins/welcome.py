from . import *
from .welcome_db import *


@ultroid_cmd(pattern="setwelcome")
async def setwelcome_(event):
    x = await eor(event, get_string("com_1"))
    if event.is_private:
        return await eod(x, "Please use this in a group and not PMs!", time=10)
    try:
        msg = event.text.split(" ", maxsplit=1)[1]
    except:
        return await eod(
            x, "Please use `{}setwelcome <messsage>`".format(hndlr), time=10
        )
    await add_welcome(x, event.chat_id, msg)


@ultroid_cmd(pattern="clearwelcome")
async def clearwelcome_(event):
    prv = get_welcome(event.chat_id)
    if prv is None:
        await eod(event, "`No welcome was set!`", time=5)
    await delete_welcome(event)


@ultroid.on(events.ChatAction())
async def check_join(event):
    try:
        tmp = get_welcome(event.chat_id)
    except:
        return
    if tmp is None:
        return
    if event.user_joined or event.user_added:
        await event.reply(tmp)
