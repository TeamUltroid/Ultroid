# Ultroid - UserBot
# Copyright (C) 2021 TeamUltroid
#
# This file is a part of < https://github.com/TeamUltroid/Ultroid/ >
# PLease read the GNU Affero General Public License in
# <https://www.github.com/TeamUltroid/Ultroid/blob/main/LICENSE/>.

import base64
import os
import urllib
from random import choice
from re import compile as re_compile
from re import findall

import requests
from bs4 import BeautifulSoup
from orangefoxapi import OrangeFoxAPI
from play_scraper import search
from search_engine_parser import GoogleSearch, YahooSearch
from telethon import Button
from telethon.tl.types import InputWebDocument as wb

from plugins._inline import SUP_BUTTONS

from . import *
from . import humanbytes as hb

ofox = "https://telegra.ph/file/231f0049fcd722824f13b.jpg"
gugirl = "https://telegra.ph/file/0df54ae4541abca96aa11.jpg"
yeah = "https://telegra.ph/file/e3c67885e16a194937516.jpg"
ps = "https://telegra.ph/file/de0b8d9c858c62fae3b6e.jpg"
ultpic = "https://telegra.ph/file/4136aa1650bc9d4109cc5.jpg"

ofox_api = OrangeFoxAPI()

api1 = base64.b64decode("QUl6YVN5QXlEQnNZM1dSdEI1WVBDNmFCX3c4SkF5NlpkWE5jNkZV").decode(
    "ascii"
)
api2 = base64.b64decode("QUl6YVN5QkYwenhMbFlsUE1wOXh3TVFxVktDUVJxOERnZHJMWHNn").decode(
    "ascii"
)
api3 = base64.b64decode("QUl6YVN5RGRPS253blB3VklRX2xiSDVzWUU0Rm9YakFLSVFWMERR").decode(
    "ascii"
)


@in_pattern("ofox")
@in_owner
async def _(e):
    try:
        match = e.text.split(" ", maxsplit=1)[1]
    except IndexError:
        kkkk = e.builder.article(
            title="Enter Device Codename",
            thumb=wb(ofox, 0, "image/jpeg", []),
            text="**OFᴏx🦊Rᴇᴄᴏᴠᴇʀʏ**\n\nYou didn't search anything",
            buttons=Button.switch_inline("Sᴇᴀʀᴄʜ Aɢᴀɪɴ", query="ofox ", same_peer=True),
        )
        await e.answer([kkkk])
    a = ofox_api.releases(codename=match)
    c = ofox_api.devices(codename=match)
    if len(a.data) > 0:
        fox = []
        for b in a.data:
            ver = b.version
            release = b.type
            size = hb(b.size)
            for z in c.data:
                fullname = z.full_name
                code = z.codename
                link = f"https://orangefox.download/device/{code}"
                text = f"**••OʀᴀɴɢᴇFᴏx Rᴇᴄᴏᴠᴇʀʏ Fᴏʀ•[•]({ofox})** {fullname}\n"
                text += f"**••Cᴏᴅᴇɴᴀᴍᴇ••** {code}\n"
                text += f"**••Bᴜɪʟᴅ Tʏᴘᴇ••** {release}\n"
                text += f"**••Vᴇʀsɪᴏɴ••** {ver}\n"
                text += f"**••Sɪᴢᴇ••** {size}\n"
                fox.append(
                    await e.builder.article(
                        title=f"{fullname}",
                        description=f"{ver}\n{release}",
                        text=text,
                        thumb=wb(ofox, 0, "image/jpeg", []),
                        link_preview=True,
                        buttons=[
                            Button.url("Dᴏᴡɴʟᴏᴀᴅ", url=f"{link}"),
                            Button.switch_inline(
                                "Sᴇᴀʀᴄʜ Aɢᴀɪɴ", query="ofox ", same_peer=True
                            ),
                        ],
                    )
                )
        await e.answer(
            fox, switch_pm="OrangeFox Recovery Search.", switch_pm_param="start"
        )
    else:
        await e.answer(
            [], switch_pm="OrangeFox Recovery Search.", switch_pm_param="start"
        )


@in_pattern("fl2lnk ?(.*)")
@in_owner
async def _(e):
    file_path = e.pattern_match.group(1)
    file_name = file_path.split("/")[-1]
    bitton = [
        [
            Button.inline("anonfiles", data=f"flanonfiles//{file_path}"),
            Button.inline("transfer", data=f"fltransfer//{file_path}"),
        ],
        [
            Button.inline("bayfiles", data=f"flbayfiles//{file_path}"),
            Button.inline("x0", data=f"flx0//{file_path}"),
        ],
        [
            Button.inline("file.io", data=f"flfile.io//{file_path}"),
            Button.inline("siasky", data=f"flsiasky//{file_path}"),
        ],
    ]
    try:
        lnk = e.builder.article(
            title="fl2lnk",
            text=f"**File:**\n{file_name}",
            buttons=bitton,
        )
    except BaseException:
        lnk = e.builder.article(
            title="fl2lnk",
            text="File not found",
        )
    await e.answer([lnk], switch_pm="File to Link.", switch_pm_param="start")


@callback(
    re_compile(
        "fl(.*)",
    ),
)
@owner
async def _(e):
    t = (e.data).decode("UTF-8")
    data = t[2:]
    host = data.split("//")[0]
    file = data.split("//")[1]
    file_name = file.split("/")[-1]
    await e.edit(f"Uploading `{file_name}` on {host}")
    await dloader(e, host, file)


@in_pattern("repo")
@in_owner
async def repo(e):
    res = [
        await e.builder.article(
            title="Ultroid Userbot",
            description="Userbot | Telethon",
            thumb=wb(ultpic, 0, "image/jpeg", []),
            text="• **ULTROID USERBOT** •",
            buttons=SUP_BUTTONS,
        ),
    ]
    await e.answer(res, switch_pm="Ultroid Repo.", switch_pm_param="start")


@in_pattern("go")
@in_owner
async def gsearch(q_event):
    try:
        match = q_event.text.split(" ", maxsplit=1)[1]
    except IndexError:
        await q_event.answer(
            [], switch_pm="Google Search. Enter a query!", switch_pm_param="start"
        )
    searcher = []
    page = findall(r"page=\d+", match)
    cache = False
    try:
        page = page[0]
        page = page.replace("page=", "")
        match = match.replace("page=" + page[0], "")
    except IndexError:
        page = 1
    search_args = (str(match), int(page), bool(cache))
    gsearch = GoogleSearch()
    gresults = await gsearch.async_search(*search_args)
    msg = ""
    for i in range(len(gresults["links"])):
        try:
            title = gresults["titles"][i]
            link = gresults["links"][i]
            desc = gresults["descriptions"][i]
            msg += f"👉[{title}]({link})\n`{desc}`\n\n"
            searcher.append(
                await q_event.builder.article(
                    title=title,
                    description=desc,
                    thumb=wb(gugirl, 0, "image/jpeg", []),
                    text=f"**Gᴏᴏɢʟᴇ Sᴇᴀʀᴄʜ**\n\n**••Tɪᴛʟᴇ••**\n`{title}`\n\n**••Dᴇsᴄʀɪᴘᴛɪᴏɴ••**\n`{desc}`",
                    link_preview=False,
                    buttons=[
                        [Button.url("Lɪɴᴋ", url=f"{link}")],
                        [
                            Button.switch_inline(
                                "Sᴇᴀʀᴄʜ Aɢᴀɪɴ",
                                query="go ",
                                same_peer=True,
                            ),
                            Button.switch_inline(
                                "Sʜᴀʀᴇ",
                                query=f"go {match}",
                                same_peer=False,
                            ),
                        ],
                    ],
                ),
            )
        except IndexError:
            break
    await q_event.answer(searcher, switch_pm="Google Search.", switch_pm_param="start")


@in_pattern("rex")
@in_owner
async def rextester(event):
    builder = event.builder
    try:
        omk = event.text.split(" ", maxsplit=1)[1]
        if omk is not None:
            if "|" in omk:
                lang, codee = omk.split("|")
            else:
                lang = "python3"
                codee = omk
            if lang == "php":
                code = f"<?php {codee} ?>"
            else:
                code = codee
            output = await rexec_aio(lang, code)
            stats = output.stats
            if output.errors is not None:
                outputt = output.errors
                resultm = builder.article(
                    title="Code",
                    description=f"Language-`{lang}` & Code-`{code}`",
                    text=f"Language:\n`{lang}`\n\nCode:\n`{code}`\n\nErrors:\n`{outputt}`\n\nStats:\n`{stats}`",
                )
            else:  # By @ProgrammingError
                outputt = output.results
                resultm = builder.article(
                    title="Code",  # By @ProgrammingError
                    description=f"Language-`{lang}` & Code-`{code}`",
                    text=f"Language:\n`{lang}`\n\nCode:\n`{code}`\n\nResult:\n`{outputt}`\n\nStats:\n`{stats}`",
                )
            await event.answer(
                [resultm], switch_pm="RexTester.", switch_pm_param="start"
            )
    except UnknownLanguage:
        resultm = builder.article(
            title="Error",  # By @ProgrammingError
            description="Invalid language choosen",
            text=f"The list of valid languages are\n\n{rex_langs}\n\n\nFormat to use Rextester is `@Yourassistantusername rex langcode|code`",
        )
        await event.answer(
            [resultm], switch_pm="RexTester. Invalid Language!", switch_pm_param="start"
        )


@in_pattern("yahoo")
@in_owner
async def yahoosearch(q_event):
    try:
        match = q_event.text.split(" ", maxsplit=1)[1]
    except IndexError:
        await q_event.answer(
            [], switch_pm="Yahoo Search. Enter a query!", switch_pm_param="start"
        )
    searcher = []
    page = findall(r"page=\d+", match)
    cache = False
    try:
        page = page[0]
        page = page.replace("page=", "")
        match = match.replace("page=" + page[0], "")
    except IndexError:
        page = 1
    search_args = (str(match), int(page), bool(cache))
    gsearch = YahooSearch()
    gresults = await gsearch.async_search(*search_args)
    msg = ""
    for i in range(len(gresults["links"])):
        try:
            title = gresults["titles"][i]
            link = gresults["links"][i]
            desc = gresults["descriptions"][i]
            msg += f"👉[{title}]({link})\n`{desc}`\n\n"
            searcher.append(
                await q_event.builder.article(
                    title=title,
                    description=desc,
                    thumb=wb(yeah, 0, "image/jpeg", []),
                    text=f"**Yᴀʜᴏᴏ Sᴇᴀʀᴄʜ**\n\n**••Tɪᴛʟᴇ••**\n`{title}`\n\n**••Dᴇsᴄʀɪᴘᴛɪᴏɴ••**\n`{desc}`",
                    link_preview=False,
                    buttons=[
                        [Button.url("Lɪɴᴋ", url=f"{link}")],
                        [
                            Button.switch_inline(
                                "Sᴇᴀʀᴄʜ Aɢᴀɪɴ",
                                query="yahoo ",
                                same_peer=True,
                            ),
                            Button.switch_inline(
                                "Sʜᴀʀᴇ",
                                query=f"yahoo {match}",
                                same_peer=False,
                            ),
                        ],
                    ],
                ),
            )
        except IndexError:
            break
    await q_event.answer(searcher, switch_pm="Yahoo Search.", switch_pm_param="start")


@in_pattern("app")
@in_owner
async def _(e):
    try:
        f = e.text.split(" ", maxsplit=1)[1]
    except IndexError:
        await e.answer(
            [], switch_pm="App search. Enter app name!", switch_pm_param="start"
        )
    foles = []
    aap = search(f)
    for z in aap:
        name = z["title"]
        desc = z["description"]
        price = z["price"]
        dev = z["developer"]
        icon = z["icon"]
        url = z["url"]
        ids = z["app_id"]
        text = f"**••Aᴘᴘ Nᴀᴍᴇ••** [{name}]({icon})\n"
        text += f"**••Dᴇᴠᴇʟᴏᴘᴇʀ••** `{dev}`\n"
        text += f"**••Pʀɪᴄᴇ••** `{price}`\n\n"
        text += f"**••Dᴇsᴄʀɪᴘᴛɪᴏɴ••**\n`{desc}`"
        foles.append(
            await e.builder.article(
                title=name,
                description=ids,
                thumb=wb(ps, 0, "image/jpeg", []),
                text=text,
                link_preview=True,
                buttons=[
                    [Button.url("Lɪɴᴋ", url=f"https://play.google.com{url}")],
                    [
                        Button.switch_inline(
                            "Mᴏʀᴇ Aᴘᴘs",
                            query="app ",
                            same_peer=True,
                        ),
                        Button.switch_inline(
                            "Sʜᴀʀᴇ",
                            query=f"app {f}",
                            same_peer=False,
                        ),
                    ],
                ],
            ),
        )
    await e.answer(foles, switch_pm="Application Searcher.", switch_pm_param="start")


@in_pattern("mods")
@in_owner
async def _(e):
    try:
        quer = e.text.split(" ", maxsplit=1)[1]
    except IndexError:
        await e.answer(
            [], switch_pm="Mod Apps Search. Enter app name!", switch_pm_param="start"
        )
    page = 1
    start = (page - 1) * 3 + 1
    da = choice([api1, api2, api3])
    url = f"https://www.googleapis.com/customsearch/v1?key={da}&cx=25b3b50edb928435b&q={quer}&start={start}"
    data = requests.get(url).json()
    search_items = data.get("items")
    search(quer)
    modss = []
    for a in search_items:
        title = a.get("title")
        desc = a.get("snippet")
        link = a.get("link")
        text = f"**••Tɪᴛʟᴇ••** `{title}`\n\n"
        text += f"**Dᴇsᴄʀɪᴘᴛɪᴏɴ** `{desc}`"
        modss.append(
            await e.builder.article(
                title=title,
                description=desc,
                text=text,
                link_preview=True,
                buttons=[
                    [Button.url("Dᴏᴡɴʟᴏᴀᴅ", url=f"{link}")],
                    [
                        Button.switch_inline(
                            "Mᴏʀᴇ Mᴏᴅs",
                            query="mods ",
                            same_peer=True,
                        ),
                        Button.switch_inline(
                            "Sʜᴀʀᴇ",
                            query=f"mods {quer}",
                            same_peer=False,
                        ),
                    ],
                ],
            ),
        )
    await e.answer(modss, switch_pm="Search Mod Applications.", switch_pm_param="start")


@in_pattern("ebooks")
@in_owner
async def clip(e):
    try:
        quer = e.text.split(" ", maxsplit=1)[1]
    except IndexError:
        await e.answer(
            [], switch_pm="Enter Query to Look for EBook", switch_pm_param="start"
        )
        return
    quer = quer.replace(" ", "+")
    sear = f"http://www.gutenberg.org/ebooks/search/?query={quer}&submit_search=Go%21"
    magma = requests.get(sear).content
    bs = BeautifulSoup(magma, "html.parser", from_encoding="utf-8")
    out = bs.find_all("img")
    Alink = bs.find_all("a", "link")
    if len(out) == 0:
        return await e.answer(
            [], switch_pm="No Results Found !", switch_pm_param="start"
        )
    buil = e.builder
    dont_take = [
        "Authors",
        "Did you mean",
        "Sort Alpha",
        "Sort by",
        "Subjects",
        "Bookshelves",
    ]
    hm = []
    titles = []
    for num in Alink:
        try:
            rt = num.find("span", "title").text
            if not rt.startswith(tuple(dont_take)):
                titles.append(rt)
        except BaseException:
            pass
    for rs in range(len(out)):
        if "/cache/epub" in out[rs]["src"]:
            link = out[rs]["src"]
            num = link.split("/")[3]
            hm.append(
                buil.document(
                    title=titles[rs],
                    description="GutenBerg Search",
                    file="https://gutenberg.org" + link.replace("small", "medium"),
                    text=f"**• Ebook Search**\n\n->> `{titles[rs]}`",
                    buttons=Button.inline("Get as Doc", data=f"ebk_{num}"),
                )
            )
    await e.answer(hm, switch_pm="Ebooks Search", switch_pm_param="start")


@callback(re_compile("ebk_(.*)"))
async def eupload(event):
    match = event.pattern_match.group(1).decode("utf-8")
    await event.answer("Uploading..")
    try:
        await event.edit(
            file=f"https://www.gutenberg.org/files/{match}/{match}-pdf.pdf"
        )
    except BaseException:
        book = "Ultroid-Book.epub"
        urllib.request.urlretrieve(
            "https://www.gutenberg.org/ebooks/132.epub.images", book
        )
        fn, media, _ = await asst._file_to_media(
            book, thumb="resources/extras/ultroid.jpg"
        )
        await event.edit(file=media)
        os.remove(book)
