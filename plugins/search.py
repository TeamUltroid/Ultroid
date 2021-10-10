# Ultroid - UserBot
# Copyright (C) 2021 TeamUltroid
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
from PIL import Image
from pyUltroid.functions.google_image import googleimagesdownload
from pyUltroid.functions.misc import google_search
from telethon.tl.types import DocumentAttributeAudio

from . import (
    async_searcher,
    eod,
    eor,
    get_string,
    saavn_dl,
    time,
    ultroid_cmd,
    uploader,
)


@ultroid_cmd(
    pattern="github (.*)",
)
async def gitsearch(event):
    usrname = event.pattern_match.group(1)
    if not usrname:
        return await eor(event, get_string("srch_1"))
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
        return await eor(event, get_string("srch_2"))
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
    pattern="google ?(.*)",
    type=["official", "manager"],
)
async def google(event):
    inp = event.pattern_match.group(1)
    if not inp:
        return await eod(event, get_string("autopic_1"))
    x = await eor(event, get_string("com_2"))
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
    await eor(x, omk, link_preview=False)


@ultroid_cmd(pattern="img ?(.*)")
async def goimg(event):
    query = event.pattern_match.group(1)
    if not query:
        return await eor(event, get_string("autopic_1"))
    nn = await eor(event, get_string("com_1"))
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
        pth = gi.download(args)
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
        return await eor(event, "`Reply to an Image`")
    ult = await eor(event, get_string("com_1"))
    dl = await reply.download_media()
    img = Image.open(dl)
    x, y = img.size
    file = {"encoded_image": (dl, open(dl, "rb"))}
    grs = requests.post(
        "https://www.google.com/searchbyimage/upload",
        files=file,
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
    pth = gi.download(args)
    ok = pth[0][text]
    await event.client.send_file(
        event.chat_id,
        ok,
        album=True,
        caption="Similar Images Realted to Search",
    )
    rmtree(f"./resources/downloads/{text}/")
    os.remove(dl)


@ultroid_cmd(
    pattern="saavn ?(.*)",
)
async def siesace(e):
    song = e.pattern_match.group(1)
    if not song:
        return await eor(e, "`Give me Something to Search", time=5)
    hmm = time.time()
    lol = await eor(e, f"`Searching {song} on Saavn...`")
    song, duration, performer, thumb = await saavn_dl(song)
    if not song:
        return await eod(lol, get_string("srch_3"))
    title = song.split(".")[0]
    okk = await uploader(song, song, hmm, lol, "Uploading " + title + "...")
    await e.reply(
        file=okk,
        message=f"`{title}`\n`From Saavn`",
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
    await lol.delete()
    [os.remove(x) for x in [song, thumb]]
