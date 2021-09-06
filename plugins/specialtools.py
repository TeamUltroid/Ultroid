# Ultroid - UserBot
# Copyright (C) 2021 TeamUltroid
#
# This file is a part of < https://github.com/TeamUltroid/Ultroid/ >
# PLease read the GNU Affero General Public License in
# <https://www.github.com/TeamUltroid/Ultroid/blob/main/LICENSE/>.
"""
✘ Commands Available -

• `{i}wspr <username>`
    Send secret message..

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
from shutil import rmtree

import pytz
import requests
from bs4 import BeautifulSoup as b
from hachoir.metadata import extractMetadata
from hachoir.parser import createParser
from pyUltroid.functions.google_image import googleimagesdownload
from telethon.tl.types import DocumentAttributeVideo

from . import *

File = []


@ultroid_cmd(
    pattern="getaudio$",
)
async def daudtoid(e):
    if not e.reply_to:
        return await eod(e, "Reply To Audio or video")
    r = await e.get_reply_message()
    if not mediainfo(r.media).startswith(("audio", "video")):
        return await eod(e, "Reply To Audio or video")
    xxx = await eor(e, "`processing...`")
    dl = r.file.name
    c_time = time.time()
    file = await downloader(
        "resources/downloads/" + dl,
        r.media.document,
        xxx,
        c_time,
        "Downloading " + dl + "...",
    )
    File.append(file.name)
    await xxx.edit("`Done.. Now reply to video In which u want to add this Audio`")


@ultroid_cmd(
    pattern="addaudio$",
)
async def adaudroid(e):
    if not e.reply_to:
        return await eod(e, "Reply To video")
    r = await e.get_reply_message()
    if not mediainfo(r.media).startswith("video"):
        return await eod(e, "Reply To video")
    if not File or os.path.exists(File[0]):
        return await xx.edit("`First reply an audio with .aw`")
    xxx = await eor(e, "`processing...`")
    dl = r.file.name
    c_time = time.time()
    file = await downloader(
        "resources/downloads/" + dl,
        r.media.document,
        xxx,
        c_time,
        "Downloading " + dl + "...",
    )
    await xxx.edit(f"Downloaded Successfully, Now Adding Your Audio to video")
    await bash(
        f'ffmpeg -i "{file.name}" -i "{File[0]}" -shortest -c:v copy -c:a aac -map 0:v:0 -map 1:a:0 output.mp4'
    )
    out = "output.mp4"
    mmmm = await uploader(
        out,
        out,
        time.time(),
        xxx,
        "Uploading " + out + "...",
    )
    metadata = extractMetadata(createParser(out))
    duration = metadata.get("duration").seconds
    hi, _ = await bash(f'mediainfo "{out}" | grep "Height"')
    wi, _ = await bash(f'mediainfo "{out}" | grep "Width"')
    height = int(hi.split(":")[1].split("pixels")[0].replace(" ", ""))
    width = int(wi.split(":")[1].split("pixels")[0].replace(" ", ""))
    attributes = [
        DocumentAttributeVideo(
            duration=duration, w=width, h=height, supports_streaming=True
        )
    ]
    await e.client.send_file(
        e.chat_id,
        mmmm,
        thumb="resources/extras/ultroid.jpg",
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
    pattern=r"dob ?(.*)",
)
async def hbd(event):
    if not event.pattern_match.group(1):
        return await eor(event, "`Put input in dd/mm/yyyy format`")
    if event.reply_to_msg_id:
        kk = await event.get_reply_message()
        nam = await event.client.get_entity(kk.from_id)
        name = nam.first_name
    else:
        name = ultroid_bot.me.first_name
    zn = pytz.timezone("Asia/Kolkata")
    abhi = dt.now(zn)
    n = event.text
    q = n[5:]
    kk = q.split("/")
    p = kk[0]
    r = kk[1]
    s = kk[2]
    day = int(p)
    month = r
    paida = q
    try:
        jn = dt.strptime(paida, "%d/%m/%Y")
    except BaseException:
        return await eor(event, "`Put input in dd/mm/yyyy format`")
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
    y = int(s) + int(saal) + 1
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
    if month == "12":
        sign = "Sagittarius" if (day < 22) else "Capricorn"
    elif month == "01":
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
        sign = "Libra" if (day < 23) else "Scorpion"
    elif month == "11":
        sign = "Scorpio" if (day < 22) else "Sagittarius"
    sign = f"{sign}"
    params = (("sign", sign), ("today", day))
    response = requests.post("https://aztro.sameerkumar.website/", params=params)
    json = response.json()
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

D.O.B -:  {paida}

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


@ultroid_cmd(pattern="sticker ?(.*)")
async def _(event):
    x = event.pattern_match.group(1)
    if not x:
        return await eor(event, "`Give something to search`")
    uu = await eor(event, "`Processing...`")
    z = request.get("https://combot.org/telegram/stickers?q=" + x).text
    xx = b(z, "lxml")
    title = xx.find_all("div", "sticker-pack__title")
    link = xx.find_all("a", target="_blank")
    if not link:
        return await uu.edit("Found Nothing")
    a = "SᴛɪᴄᴋEʀs Aᴡᴀɪʟᴀʙʟᴇ ~"
    for xxx, yyy in zip(title, link):
        v = xxx.get_text()
        w = yyy["href"]
        d = f"\n\n[{v}]({w})"
        if d not in a:
            a += d
    await uu.edit(a)


@ultroid_cmd(pattern="wall ?(.*)")
async def wall(event):
    inp = event.pattern_match.group(1)
    if not inp:
        return await eor(event, "`Give me something to search..`")
    nn = await eor(event, "`Processing Keep Patience...`")
    query = f"hd {inp}"
    gi = googleimagesdownload()
    args = {
        "keywords": query,
        "limit": 10,
        "format": "jpg",
        "output_directory": "./resources/downloads/",
    }
    gi.download(args)
    xx = choice(os.listdir(os.path.abspath(f"./resources/downloads/{query}/")))
    await event.client.send_file(event.chat_id, f"./resources/downloads/{query}/{xx}")
    rmtree(f"./resources/downloads/{query}/")
    await nn.delete()
