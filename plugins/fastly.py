# Ultroid - UserBot
# Copyright (C) 2020 TeamUltroid
#
# This file is a part of < https://github.com/TeamUltroid/Ultroid/ >
# PLease read the GNU Affero General Public License in
# <https://www.github.com/TeamUltroid/Ultroid/blob/main/LICENSE/>.

"""
Fasly Bot Cheat.

• `{i}fastly` - On/Off command.

• Also Required : `OCR_API`. Add it using the command `.setdb OCR_API api_key`
• To get the API visit 'https://ocr.space/ocrapi'
The bot will try to auto reply first to the messages by @FastlyWriteBot

• Add User id of fastly clone to `FASTLY_CLONES` to allow this plugin work with them.
"""

from os import remove
from core.remote import rm
from telethon import events

from . import LOGS, async_searcher, udB, ultroid_bot, ultroid_cmd

base_url = "https://api.ocr.space/parse/imageurl?apikey={api}&url={tgraph}"

BotList = [1806208310]

if udB.get_key("FASTLY_CLONES"):
    for i in udB.get_key("FASTLY_CLONES").split():
        try:
            BotList.append(int(i))
        except TypeError:
            LOGS.exception(f"Invalid Value in 'FASTLY_CLONES': {i}")


async def fastly_bot(event):
    if not udB.get_key("FASTLY"):
        return
    api = udB.get_key("OCR_API")
    if not (api and event.photo):
        return
    med = await event.download_media()
    with rm.get("telegraph", helper=True, dispose=True) as mod:
        link = mod.upload_file(med)
    out = await async_searcher(base_url.format(api=api, tgraph=link), re_json=True)
    try:
        txt = out["ParsedResults"][0]["ParsedText"]
    except (KeyError, IndexError):
        return
    txt = txt.split("By@")[0].replace("\n", "").replace("\r", "")
    if txt:
        try:
            await event.reply(txt)
        except Exception as er:
            LOGS.exception(er)
    try:
        remove(med)
    except Exception as e:
        LOGS.exception(e)


@ultroid_cmd(pattern="fastly$")
async def fastOnOff(event):
    xx = await event.eor("`...`")
    get_ = udB.get_key("FASTLY")
    if not get_:
        if not udB.get_key("OCR_API"):
            return await xx.edit("`OCR_API` is missing.\nAdd it before using this..")
        udB.set_key("FASTLY", True)
        ultroid_bot.add_handler(
            fastly_bot,
            events.NewMessage(incoming=True, from_users=BotList),
        )
        return await xx.edit("`Auto Fastly Response Activated`")
    udB.del_key("FASTLY")
    await xx.edit("`Fastly Stopped!`")


if udB.get_key("FASTLY"):
    ultroid_bot.add_handler(
        fastly_bot,
        events.NewMessage(incoming=True, from_users=BotList),
    )
