# Ultroid - UserBot
# Copyright (C) 2021-2025 TeamUltroid
#
# This file is a part of < https://github.com/TeamUltroid/Ultroid/ >
# PLease read the GNU Affero General Public License in
# <https://www.github.com/TeamUltroid/Ultroid/blob/main/LICENSE/>.
"""
✘ Commands Available -

• `{i}wspr <username>`
    Send secret message..

• `{i}q <color-optional>`
• `{i}q @username`
• `{i}q r <color-optional>`
• `{i}q count` : `multiple quotes`
    Create quotes..

• `{i}sticker <query>`
    Search Stickers as Per ur Wish..

• `{i}getaudio <reply to an audio>`
    Download Audio To put in ur Desired Video/Gif.

• `{i}addaudio <reply to Video/gif>`
    It will put the above audio to the replied video/gif.

• `{i}dob <date of birth>`
    Put in dd/mm/yy Format only(eg .dob 01/01/1999).

• `{i}wall <query>`
    Search Hd Wallpaper as Per ur Wish..
"""
import os
import time
from datetime import datetime as dt
from random import choice

import pytz, asyncio
from bs4 import BeautifulSoup as bs
from telethon.tl.types import DocumentAttributeVideo
from requests import Session
from cloudscraper import create_scraper
from pyUltroid.fns.tools import get_google_images, metadata

from . import (
    HNDLR,
    ULTConfig,
    async_searcher,
    bash,
    downloader,
    eod,
    get_string,
    mediainfo,
    quotly,
    ultroid_bot,
    ultroid_cmd,
    uploader,
)
from .beautify import all_col

File = []
scraper = create_scraper()

@ultroid_cmd(
    pattern="getaudio$",
)
async def daudtoid(e):
    if not e.reply_to:
        return await eod(e, get_string("spcltool_1"))
    r = await e.get_reply_message()
    if not mediainfo(r.media).startswith(("audio", "video")):
        return await eod(e, get_string("spcltool_1"))
    xxx = await e.eor(get_string("com_1"))
    dl = r.file.name or "input.mp4"
    c_time = time.time()
    file = await downloader(
        f"resources/downloads/{dl}",
        r.media.document,
        xxx,
        c_time,
        f"Downloading {dl}...",
    )

    File.append(file.name)
    await xxx.edit(get_string("spcltool_2"))


@ultroid_cmd(
    pattern="addaudio$",
)
async def adaudroid(e):
    if not e.reply_to:
        return await eod(e, get_string("spcltool_3"))
    r = await e.get_reply_message()
    if not mediainfo(r.media).startswith("video"):
        return await eod(e, get_string("spcltool_3"))
    if not (File and os.path.exists(File[0])):
        return await e.edit(f"`First reply an audio with {HNDLR}addaudio`")
    xxx = await e.eor(get_string("com_1"))
    dl = r.file.name or "input.mp4"
    c_time = time.time()
    file = await downloader(
        f"resources/downloads/{dl}",
        r.media.document,
        xxx,
        c_time,
        f"Downloading {dl}...",
    )

    await xxx.edit(get_string("spcltool_5"))
    await bash(
        f'ffmpeg -i "{file.name}" -i "{File[0]}" -shortest -c:v copy -c:a aac -map 0:v:0 -map 1:a:0 output.mp4'
    )
    out = "output.mp4"
    mmmm = await uploader(out, out, time.time(), xxx, f"Uploading {out}...")
    data = await metadata(out)
    width = data["width"]
    height = data["height"]
    duration = data["duration"]
    attributes = [
        DocumentAttributeVideo(
            duration=duration, w=width, h=height, supports_streaming=True
        )
    ]
    await e.client.send_file(
        e.chat_id,
        mmmm,
        thumb=ULTConfig.thumb,
        attributes=attributes,
        force_document=False,
        reply_to=e.reply_to_msg_id,
    )
    await xxx.delete()
    os.remove(out)
    os.remove(file.name)
    File.clear()
    os.remove(File[0])


@ultroid_cmd(
    pattern=r"dob( (.*)|$)",
)
async def hbd(event):
    match = event.pattern_match.group(1).strip()
    if not match:
        return await event.eor(get_string("spcltool_6"))
    if event.reply_to_msg_id:
        kk = await event.get_reply_message()
        nam = await kk.get_sender()
        name = nam.first_name
    else:
        name = ultroid_bot.me.first_name
    zn = pytz.timezone("Asia/Kolkata")
    abhi = dt.now(zn)
    kk = match.split("/")
    p = kk[0]
    r = kk[1]
    s = kk[2]
    day = int(p)
    month = r
    try:
        jn = dt.strptime(match, "%d/%m/%Y")
    except BaseException:
        return await event.eor(get_string("spcltool_6"))
    jnm = zn.localize(jn)
    zinda = abhi - jnm
    barsh = (zinda.total_seconds()) / (365.242 * 24 * 3600)
    saal = int(barsh)
    mash = (barsh - saal) * 12
    mahina = int(mash)
    divas = (mash - mahina) * (365.242 / 12)
    din = int(divas)
    samay = (divas - din) * 24
    ghanta = int(samay)
    pehl = (samay - ghanta) * 60
    mi = int(pehl)
    sec = (pehl - mi) * 60
    slive = int(sec)
    y = int(s) + saal + 1
    m = int(r)
    brth = dt(y, m, day)
    cm = dt(abhi.year, brth.month, brth.day)
    ish = (cm - abhi.today()).days + 1
    dan = ish
    if dan == 0:
        hp = "`Happy BirthDay To U🎉🎊`"
    elif dan < 0:
        okk = 365 + ish
        hp = f"{okk} Days Left 🥳"
    elif dan > 0:
        hp = f"{ish} Days Left 🥳"
    if month == "01":
        sign = "Capricorn" if (day < 20) else "Aquarius"
    elif month == "02":
        sign = "Aquarius" if (day < 19) else "Pisces"
    elif month == "03":
        sign = "Pisces" if (day < 21) else "Aries"
    elif month == "04":
        sign = "Aries" if (day < 20) else "Taurus"
    elif month == "05":
        sign = "Taurus" if (day < 21) else "Gemini"
    elif month == "06":
        sign = "Gemini" if (day < 21) else "Cancer"
    elif month == "07":
        sign = "Cancer" if (day < 23) else "Leo"
    elif month == "08":
        sign = "Leo" if (day < 23) else "Virgo"
    elif month == "09":
        sign = "Virgo" if (day < 23) else "Libra"
    elif month == "10":
        sign = "Libra" if (day < 23) else "Scorpio"
    elif month == "11":
        sign = "Scorpio" if (day < 22) else "Sagittarius"
    elif month == "12":
        sign = "Sagittarius" if (day < 22) else "Capricorn"
    json = await async_searcher(
        f"https://aztro.sameerkumar.website/?sign={sign}&day=today",
        post=True,
        re_json=True,
    )
    dd = json.get("current_date")
    ds = json.get("description")
    lt = json.get("lucky_time")
    md = json.get("mood")
    cl = json.get("color")
    ln = json.get("lucky_number")
    await event.delete()
    await event.client.send_message(
        event.chat_id,
        f"""
    Name -: {name}

D.O.B -:  {match}

Lived -:  {saal}yr, {mahina}m, {din}d, {ghanta}hr, {mi}min, {slive}sec

Birthday -: {hp}

Zodiac -: {sign}

**Horoscope On {dd} -**

`{ds}`

    Lucky Time :-        {lt}
    Lucky Number :-   {ln}
    Lucky Color :-        {cl}
    Mood :-                   {md}
    """,
        reply_to=event.reply_to_msg_id,
    )

session = Session()

@ultroid_cmd(pattern="sticker( (.*)|$)")
async def _(event):
    x = event.pattern_match.group(1).strip()
    if not x:
        return await event.eor("`Give something to search`")
    uu = await event.eor(get_string("com_1"))
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    
    max_retries = 3
    retry_count = 0
    
    while retry_count < max_retries:
        try:
            response = scraper.get(
                f"https://combot.org/telegram/stickers?q={x}",
                headers=headers
            ).content
            
            # Check if response contains Cloudflare challenge
            if "Just a moment..." in response.decode():
                retry_count += 1
                await asyncio.sleep(2) # Wait before retry
                continue
                
            z = bs(response, "html.parser")
            packs = z.find_all("a", {"class": "stickerset__title"})
            
            if not packs:
                return await uu.edit(get_string("spcltool_9"))
                
            break # Success - exit loop
            
        except Exception as er:
            retry_count += 1
            await asyncio.sleep(2)
            continue
    
    if retry_count >= max_retries:
        return await uu.edit("`Failed to fetch stickers after multiple retries`")
    try:
        sticks = {}
        for pack in packs:
            href = pack.get("href")
            title = pack.text.strip()
            if href:
                href = f"https://t.me/addstickers/{href.split('/')[-1]}"
                sticks[href] = title

        if not sticks:
            return await uu.edit(get_string("spcltool_9"))

        a = "SᴛɪᴄᴋEʀs Aᴠᴀɪʟᴀʙʟᴇ ~\n\n"
        for href, title in sticks.items():
            a += f"<a href={href}>{title}</a>\n"
        await uu.edit(a, parse_mode="html")
        
    except Exception as e:
        await uu.edit(f"`Error: {str(e)}`\nTry again later.")

@ultroid_cmd(pattern="wall( (.*)|$)")
async def wall(event):
    inp = event.pattern_match.group(1).strip()
    if not inp:
        return await event.eor("`Give me something to search..`")
    nn = await event.eor(get_string("com_1"))
    query = f"hd {inp}"
    images = await get_google_images(query)
    for z in range(5):
        await event.client.send_file(event.chat_id, file=images[z]["original"])
    await nn.delete()


@ultroid_cmd(pattern="q( (.*)|$)", manager=True, allow_pm=True)
async def quott_(event):
    match = event.pattern_match.group(1).strip()
    if not event.is_reply:
        return await event.eor("`Reply to Message..`")
    msg = await event.eor(get_string("com_1"))
    reply = await event.get_reply_message()
    replied_to, reply_ = None, None
    if match:
        spli_ = match.split(maxsplit=1)
        if (spli_[0] in ["r", "reply"]) or (
            spli_[0].isdigit() and int(spli_[0]) in range(1, 21)
        ):
            if spli_[0].isdigit():
                if not event.client._bot:
                    reply_ = await event.client.get_messages(
                        event.chat_id,
                        min_id=event.reply_to_msg_id - 1,
                        reverse=True,
                        limit=int(spli_[0]),
                    )
                else:
                    id_ = reply.id
                    reply_ = []
                    for msg_ in range(id_, id_ + int(spli_[0])):
                        msh = await event.client.get_messages(event.chat_id, ids=msg_)
                        if msh:
                            reply_.append(msh)
            else:
                replied_to = await reply.get_reply_message()
            try:
                match = spli_[1]
            except IndexError:
                match = None
    user = None
    if not reply_:
        reply_ = reply
    if match:
        match = match.split(maxsplit=1)
    if match:
        if match[0].startswith("@") or match[0].isdigit():
            try:
                match_ = await event.client.parse_id(match[0])
                user = await event.client.get_entity(match_)
            except ValueError:
                pass
            match = match[1] if len(match) == 2 else None
        else:
            match = match[0]
    if match == "random":
        match = choice(all_col)
    try:
        file = await quotly.create_quotly(
            reply_, bg=match, reply=replied_to, sender=user
        )
    except Exception as er:
        return await msg.edit(str(er))
    message = await reply.reply("Quotly by Ultroid", file=file)
    os.remove(file)
    await msg.delete()
    return message
