# Ultroid - UserBot
# Copyright (C) 2021-2024 TeamUltroid
#
# This file is a part of < https://github.com/TeamUltroid/Ultroid/ >
# PLease read the GNU Affero General Public License in
# <https://www.github.com/TeamUltroid/Ultroid/blob/main/LICENSE/>.

from . import get_help

__doc__ = get_help("help_beautify")


import os
import random
from secrets import token_hex
from urllib.parse import urlencode

from telethon.utils import get_display_name

from . import Carbon, get_string, inline_mention, ultroid_cmd

_colorspath = "resources/colorlist.txt"

if os.path.exists(_colorspath):
    with open(_colorspath, "r") as f:
        all_col = f.read().split()
else:
    all_col = []


@ultroid_cmd(
    pattern="(rc|c)arbon",
)
async def cr_bn(event):
    xxxx = await event.eor(get_string("com_1"))
    te = event.pattern_match.group(1)
    col = random.choice(all_col) if te[0] == "r" else "White"
    if event.reply_to_msg_id:
        temp = await event.get_reply_message()
        if temp.media:
            b = await event.client.download_media(temp)
            with open(b) as a:
                code = a.read()
            os.remove(b)
        else:
            code = temp.message
    else:
        try:
            code = event.text.split(" ", maxsplit=1)[1]
        except IndexError:
            return await xxxx.eor(get_string("carbon_2"))
    xx = await Carbon(code=code, file_name="ultroid_carbon", backgroundColor=col)
    if isinstance(xx, dict):
        await xxxx.edit(f"`{xx}`")
        return
    await xxxx.delete()
    await event.reply(
        f"Carbonised by {inline_mention(event.sender)}",
        file=xx,
    )


@ultroid_cmd(
    pattern="ccarbon( (.*)|$)",
)
async def crbn(event):
    match = event.pattern_match.group(1).strip()
    if not match:
        return await event.eor(get_string("carbon_3"))
    msg = await event.eor(get_string("com_1"))
    if event.reply_to_msg_id:
        temp = await event.get_reply_message()
        if temp.media:
            b = await event.client.download_media(temp)
            with open(b) as a:
                code = a.read()
            os.remove(b)
        else:
            code = temp.message
    else:
        try:
            match = match.split(" ", maxsplit=1)
            code = match[1]
            match = match[0]
        except IndexError:
            return await msg.eor(get_string("carbon_2"))
    xx = await Carbon(code=code, backgroundColor=match)
    await msg.delete()
    await event.reply(
        f"Carbonised by {inline_mention(event.sender)}",
        file=xx,
    )


RaySoTheme = [
    "meadow",
    "breeze",
    "raindrop",
    "candy",
    "crimson",
    "falcon",
    "sunset",
    "midnight",
]


@ultroid_cmd(pattern="rayso")
async def pass_on(ult):
    try:
        from playwright.async_api import async_playwright
    except ImportError:
        await ult.eor(
            "`playwright` is not installed!\nPlease install it to use this command.."
        )
        return
    proc = await ult.eor(get_string("com_1"))
    spli = ult.text.split()
    theme, dark, title, text = None, True, get_display_name(ult.chat), None
    if len(spli) > 2:
        if spli[1] in RaySoTheme:
            theme = spli[1]
        dark = spli[2].lower().strip() in ["true", "t"]
    elif len(spli) > 1:
        if spli[1] in RaySoTheme:
            theme = spli[1]
        elif spli[1] == "list":
            text = "**List of Rayso Themes:**\n" + "\n".join(
                [f"- `{th_}`" for th_ in RaySoTheme]
            )

            await proc.eor(text)
            return
        else:
            try:
                text = ult.text.split(maxsplit=1)[1]
            except IndexError:
                pass
    if not theme or theme not in RaySoTheme:
        theme = random.choice(RaySoTheme)
    if ult.is_reply:
        msg = await ult.get_reply_message()
        text = msg.message
        title = get_display_name(msg.sender)
    name = token_hex(8) + ".png"
    data = {"darkMode": dark, "theme": theme, "title": title}
    url = f"https://ray.so/#{urlencode(data)}"
    async with async_playwright() as play:
        chrome = await play.chromium.launch()
        page = await chrome.new_page()
        await page.goto(url)
        await page.wait_for_load_state("networkidle")
        elem = await page.query_selector("textarea[class='Editor_textarea__sAyL_']")
        await elem.type(text)
        button = await page.query_selector("button[class='ExportButton_button__d___t']")
        await button.click()
        async with page.expect_download() as dl:
            dled = await dl.value
            await dled.save_as(name)
    await proc.reply(file=name)
    await proc.try_delete()
    os.remove(name)
