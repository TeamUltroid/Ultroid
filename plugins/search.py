# Ultroid - UserBot
# Copyright (C) 2021-2022 TeamUltroid
#
# This file is a part of < https://github.com/TeamUltroid/Ultroid/ >
# PLease read the GNU Affero General Public License in
# <https://www.github.com/TeamUltroid/Ultroid/blob/main/LICENSE/>.
"""
✘ Commands Available -

• `{i}saavn <search query>`
    Download songs from Saavn.

• `{i}google <query>`
    For doing google search.

• `{i}github <username>`
    Get full information of the users github profile.

• `{i}img <query>`
  `{i}img <query> ; <no of results>`
    For doing Images search.

• `{i}reverse`
    Reply an Image or sticker to find its sauce.
"""
import os
from shutil import rmtree

import requests
from bs4 import BeautifulSoup as bs

try:
    from PIL import Image
except ImportError:
    Image = None
try:
    import cv2
except ImportError:
    cv2 = None
from telethon.tl.types import DocumentAttributeAudio

from pyUltroid.fns.google_image import googleimagesdownload
from pyUltroid.fns.misc import google_search
from pyUltroid.fns.tools import saavn_search

from . import async_searcher, con, eod, fast_download, get_string, ultroid_cmd


@ultroid_cmd(
    pattern="github (.*)",
)
async def gitsearch(event):
    usrname = event.pattern_match.group(1).strip()
    if not usrname:
        return await event.eor(get_string("srch_1"))
    url = f"https://api.github.com/users/{usrname}"
    ult = await async_searcher(url, re_json=True)
    try:
        uname = ult["login"]
        uid = ult["id"]
        upic = f"https://avatars.githubusercontent.com/u/{uid}"
        ulink = ult["html_url"]
        uacc = ult["name"]
        ucomp = ult["company"]
        ublog = ult["blog"]
        ulocation = ult["location"]
        ubio = ult["bio"]
        urepos = ult["public_repos"]
        ufollowers = ult["followers"]
        ufollowing = ult["following"]
    except BaseException:
        return await event.eor(get_string("srch_2"))
    fullusr = f"""
**[GITHUB]({ulink})**
**Name** - {uacc}
**UserName** - {uname}
**ID** - {uid}
**Company** - {ucomp}
**Blog** - {ublog}
**Location** - {ulocation}
**Bio** - {ubio}
**Repos** - {urepos}
**Followers** - {ufollowers}
**Following** - {ufollowing}
"""
    await event.respond(fullusr, file=upic)
    await event.delete()


@ultroid_cmd(
    pattern="google( (.*)|$)",
    manager=True,
)
async def google(event):
    inp = event.pattern_match.group(1).strip()
    if not inp:
        return await eod(event, get_string("autopic_1"))
    x = await event.eor(get_string("com_2"))
    gs = await google_search(inp)
    if not gs:
        return await eod(x, get_string("autopic_2").format(inp))
    out = ""
    for res in gs:
        text = res["title"]
        url = res["link"]
        des = res["description"]
        out += f" 👉🏻  [{text}]({url})\n`{des}`\n\n"
    omk = f"**Google Search Query:**\n`{inp}`\n\n**Results:**\n{out}"
    await x.eor(omk, link_preview=False)


@ultroid_cmd(pattern="img( (.*)|$)")
async def goimg(event):
    query = event.pattern_match.group(1).strip()
    if not query:
        return await event.eor(get_string("autopic_1"))
    nn = await event.eor(get_string("com_1"))
    lmt = 5
    if ";" in query:
        try:
            lmt = int(query.split(";")[1])
            query = query.split(";")[0]
        except BaseException:
            pass
    try:
        gi = googleimagesdownload()
        args = {
            "keywords": query,
            "limit": lmt,
            "format": "jpg",
            "output_directory": "./resources/downloads/",
        }
        pth = await gi.download(args)
        ok = pth[0][query]
    except BaseException:
        return await nn.edit(get_string("autopic_2").format(query))
    await event.reply(file=ok, message=query)
    rmtree(f"./resources/downloads/{query}/")
    await nn.delete()


@ultroid_cmd(pattern="reverse$")
async def reverse(event):
    reply = await event.get_reply_message()
    if not reply:
        return await event.eor("`Reply to an Image`")
    ult = await event.eor(get_string("com_1"))
    dl = await reply.download_media()
    file = await con.convert(dl, convert_to="png")
    img = Image.open(file)
    x, y = img.size
    files = {"encoded_image": (file, open(file, "rb"))}
    grs = requests.post(
        "https://www.google.com/searchbyimage/upload",
        files=files,
        allow_redirects=False,
    )
    loc = grs.headers.get("Location")
    response = await async_searcher(
        loc,
        headers={
            "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:58.0) Gecko/20100101 Firefox/58.0",
        },
    )
    xx = bs(response, "html.parser")
    div = xx.find_all("div", {"class": "r5a77d"})[0]
    alls = div.find("a")
    link = alls["href"]
    text = alls.text
    await ult.edit(f"`Dimension ~ {x} : {y}`\nSauce ~ [{text}](google.com{link})")
    gi = googleimagesdownload()
    args = {
        "keywords": text,
        "limit": 2,
        "format": "jpg",
        "output_directory": "./resources/downloads/",
    }
    pth = await gi.download(args)
    ok = pth[0][text]
    await event.client.send_file(
        event.chat_id,
        ok,
        album=True,
        caption="Similar Images Realted to Search",
    )
    rmtree(f"./resources/downloads/{text}/")
    os.remove(file)


@ultroid_cmd(
    pattern="saavn( (.*)|$)",
)
async def siesace(e):
    song = e.pattern_match.group(1).strip()
    if not song:
        return await e.eor("`Give me Something to Search", time=5)
    eve = await e.eor(f"`Searching for {song} on Saavn...`")
    try:
        data = (await saavn_search(song))[0]
    except IndexError:
        return await eve.eor(f"`{song} not found on saavn.`")
    try:
        title = data["title"]
        url = data["url"]
        img = data["image"]
        duration = data["duration"]
        performer = data["artists"]
    except KeyError:
        return await eve.eor("`Something went wrong.`")
    song, _ = await fast_download(url, filename=f"{title}.m4a")
    thumb, _ = await fast_download(img, filename=f"{title}.jpg")
    song, _ = await e.client.fast_uploader(song, to_delete=True)
    await eve.eor(
        file=song,
        text=f"`{title}`\n`From Saavn`",
        attributes=[
            DocumentAttributeAudio(
                duration=int(duration),
                title=title,
                performer=performer,
            )
        ],
        supports_streaming=True,
        thumb=thumb,
    )
    await eve.delete()
    os.remove(thumb)
