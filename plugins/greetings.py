# Ultroid - UserBot
# Copyright (C) 2021 TeamUltroid
#
# This file is a part of < https://github.com/TeamUltroid/Ultroid/ >
# PLease read the GNU Affero General Public License in
# <https://www.github.com/TeamUltroid/Ultroid/blob/main/LICENSE/>.

"""
✘ Commands Available -

---- Welcomes ----
• `{i}setwelcome <message/reply to message>`
    Set welcome message in the current chat.

• `{i}clearwelcome`
    Delete the welcome in the current chat.

• `{i}getwelcome`
    Get the welcome message in the current chat.

---- GoodByes ----
• `{i}setgoodbye <message/reply to message>`
    Set goodbye message in the current chat.

• `{i}cleargoodbye`
    Delete the goodbye in the current chat.

• `{i}getgoodbye`
    Get the goodbye message in the current chat.

• `{i}thankmembers on/off`
    Send a thank you sticker on hitting a members count of 100*x in your groups.
"""
import os

from pyUltroid.functions.greetings_db import *
from telegraph import upload_file as uf
from telethon.utils import pack_bot_file_id

from . import *

Note = "\n\nNote: `{mention}`, `{group}`, `{count}`, `{name}`, `{fullname}`, `{username}`, `{userid}` can be used as formatting parameters.\n\n"


@ultroid_cmd(pattern="setwelcome")
async def setwel(event):
    x = await eor(event, get_string("com_1"))
    r = await event.get_reply_message()
    if event.is_private:
        return await eod(x, "Please use this in a group and not PMs!", time=10)
    if r and r.media:
        wut = mediainfo(r.media)
        if wut.startswith(("pic", "gif")):
            dl = await r.download_media()
            variable = uf(dl)
            os.remove(dl)
            m = "https://telegra.ph" + variable[0]
        elif wut == "video":
            if r.media.document.size > 8 * 1000 * 1000:
                return await eod(x, "`Unsupported Media`")
            else:
                dl = await r.download_media()
                variable = uf(dl)
                os.remove(dl)
                m = "https://telegra.ph" + variable[0]
        elif wut == "web":
            m = None
        else:
            m = pack_bot_file_id(r.media)
        if r.text:
            add_welcome(event.chat_id, r.message, m)
        else:
            add_welcome(event.chat_id, None, m)
        await eor(x, "`Welcome note saved`")
    elif r and r.text:
        add_welcome(event.chat_id, r.message, None)
        await eor(x, "`Welcome note saved`")
    else:
        await eod(x, "`Reply to message which u want to set as welcome`")


@ultroid_cmd(pattern="clearwelcome$")
async def clearwel(event):
    if not get_welcome(event.chat_id):
        await eod(event, "`No welcome was set!`", time=5)
    delete_welcome(event.chat_id)
    await eod(event, "`Welcome Note Deleted`")


@ultroid_cmd(pattern="getwelcome$")
async def listwel(event):
    wel = get_welcome(event.chat_id)
    if not wel:
        await eod(event, "`No welcome was set!`", time=5)
    msgg = wel["welcome"]
    med = wel["media"]
    await event.reply(f"**Welcome Note in this chat**\n\n`{msgg}`", file=med)
    await event.delete()


@ultroid_cmd(pattern="setgoodbye")
async def setgb(event):
    x = await eor(event, get_string("com_1"))
    r = await event.get_reply_message()
    if event.is_private:
        return await eod(x, "Please use this in a group and not PMs!", time=10)
    if r and r.media:
        wut = mediainfo(r.media)
        if wut.startswith(("pic", "gif")):
            dl = await r.download_media()
            variable = uf(dl)
            os.remove(dl)
            m = "https://telegra.ph" + variable[0]
        elif wut == "video":
            if r.media.document.size > 8 * 1000 * 1000:
                return await eod(x, "`Unsupported Media`")
            else:
                dl = await r.download_media()
                variable = uf(dl)
                os.remove(dl)
                m = "https://telegra.ph" + variable[0]
        elif wut == "web":
            m = None
        else:
            m = pack_bot_file_id(r.media)
        if r.text:
            add_goodbye(event.chat_id, r.message, m)
        else:
            add_goodbye(event.chat_id, None, m)
        await eor(x, "`Goodbye note saved`")
    elif r and r.text:
        add_goodbye(event.chat_id, r.message, None)
        await eor(x, "`Goodbye note saved`")
    else:
        await eod(x, "`Reply to message which u want to set as goodbye`")


@ultroid_cmd(pattern="cleargoodbye$")
async def clearwgb(event):
    if not get_goodbye(event.chat_id):
        await eod(event, "`No goodbye was set!`", time=5)
    delete_goodbye(event.chat_id)
    await eod(event, "`Goodbye Note Deleted`")


@ultroid_cmd(pattern="getgoodbye$")
async def listgd(event):
    wel = get_goodbye(event.chat_id)
    if not wel:
        await eod(event, "`No goodbye was set!`", time=5)
    msgg = wel["goodbye"]
    med = wel["media"]
    await event.reply(f"**Goodbye Note in this chat**\n\n`{msgg}`", file=med)
    await event.delete()


@ultroid_cmd(pattern="thankmembers (on|off)")
async def thank_set(event):
    type_ = event.pattern_match.group(1)
    if not type_ or type_ == "":
        await eor(
            event,
            f"**Current Chat Settings:**\n**Thanking Members:** `{must_thank(event.chat_id)}`\n\nUse `{hndlr}thankmembers on` or `{hndlr}thankmembers off` to toggle current settings!",
        )
        return
    chat = event.chat_id
    if not str(chat).startswith("-"):
        return await eod(event, "`Please use this command in a group!`", time=10)
    if type_.lower() == "on":
        add_thanks(chat)
    elif type_.lower() == "off":
        remove_thanks(chat)
    await eor(
        event,
        f"**Done! Thank you members has been turned** `{type_.lower()}` **for this chat**!",
    )
