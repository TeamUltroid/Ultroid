# Ultroid - UserBot
# Copyright (C) 2020 TeamUltroid
#
# This file is a part of < https://github.com/TeamUltroid/Ultroid/ >
# PLease read the GNU Affero General Public License in
# <https://www.github.com/TeamUltroid/Ultroid/blob/main/LICENSE/>.

import random
import re
from urllib.request import urlopen

import play_scraper
import requests
from bs4 import BeautifulSoup
from rextester_py import rexec_aio
from rextester_py.rextester_aio import UnknownLanguage
from pyUltroid.functions import GoogleSearch, YahooSearch
from telethon import Button
from telethon.tl.types import InputWebDocument as wb

from . import *

gugirl = "https://telegra.ph/file/0df54ae4541abca96aa11.jpg"
yeah = "https://telegra.ph/file/e3c67885e16a194937516.jpg"
ps = "https://telegra.ph/file/de0b8d9c858c62fae3b6e.jpg"


@in_pattern("go")
@in_owner
async def gsearch(q_event):
    try:
        match = q_event.text.split(" ", maxsplit=1)[1]
    except IndexError:
        kkkk = q_event.builder.article(
            title="Search Something",
            thumb=wb(gugirl, 0, "image/jpeg", []),
            text="**Gᴏᴏɢʟᴇ Sᴇᴀʀᴄʜ**\n\nYou didn't search anything",
            buttons=Button.switch_inline("Sᴇᴀʀᴄʜ Aɢᴀɪɴ", query="go ", same_peer=True),
        )
        await q_event.answer([kkkk])
    searcher = []
    page = re.findall(r"page=\d+", match)
    try:
        page = page[0]
        page = page.replace("page=", "")
        match = match.replace("page=" + page[0], "")
    except IndexError:
        page = 1
    search_args = (str(match), int(page), cache=False)
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
                                "Sᴇᴀʀᴄʜ Aɢᴀɪɴ", query="go ", same_peer=True
                            ),
                            Button.switch_inline(
                                "Sʜᴀʀᴇ", query=f"go {match}", same_peer=False
                            ),
                        ],
                    ],
                )
            )
        except IndexError:
            break
    await q_event.answer(searcher)


@in_pattern("rex")
@in_owner
async def rextester(event):
    builder = event.builder
    try:
        omk = event.text.split(" ", maxsplit=1)[1]
        if omk is not None:
            if "|" in omk:
                lang, code = omk.split("|")
            else:
                lang = "python 3"
                code = omk
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
            await event.answer([resultm])
    except UnknownLanguage:
        resultm = builder.article(
            title="Error",  # By @ProgrammingError
            description="Invalid language choosen",
            text="The list of valid languages are\n\nc#, vb.net, f#, java, python, c (gcc), \nc++ (gcc), php, pascal, objective-c, haskell, \nruby, perl, lua, nasm, sql server, javascript, lisp, prolog, go, scala, \nscheme, node.js, python 3, octave, c (clang), \nc++ (clang), c++ (vc++), c (vc), d, r, tcl, mysql, postgresql, oracle, swift, \nbash, ada, erlang, elixir, ocaml, \nkotlin, brainfuck, fortran\n\n\n Format to use Rextester is `@Yourassistantusername rex langcode|code`",
        )
        await event.answer([resultm])


@in_pattern("yahoo")
@in_owner
async def gsearch(q_event):
    try:
        match = q_event.text.split(" ", maxsplit=1)[1]
    except IndexError:
        kkkk = q_event.builder.article(
            title="Search Something",
            thumb=wb(yeah, 0, "image/jpeg", []),
            text="**Yᴀʜᴏᴏ Sᴇᴀʀᴄʜ**\n\nYou didn't search anything",
            buttons=Button.switch_inline(
                "Sᴇᴀʀᴄʜ Aɢᴀɪɴ", query="yahoo ", same_peer=True
            ),
        )
        await q_event.answer([kkkk])
    searcher = []
    page = re.findall(r"page=\d+", match)
    try:
        page = page[0]
        page = page.replace("page=", "")
        match = match.replace("page=" + page[0], "")
    except IndexError:
        page = 1
    search_args = (str(match), int(page), cache=False)
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
                                "Sᴇᴀʀᴄʜ Aɢᴀɪɴ", query="yahoo ", same_peer=True
                            ),
                            Button.switch_inline(
                                "Sʜᴀʀᴇ", query=f"yahoo {match}", same_peer=False
                            ),
                        ],
                    ],
                )
            )
        except IndexError:
            break
    await q_event.answer(searcher)


@in_pattern("app")
@in_owner
async def _(e):
    try:
        f = e.text.split(" ", maxsplit=1)[1]
    except IndexError:
        kkkk = e.builder.article(
            title="Search Something",
            thumb=wb(ps, 0, "image/jpeg", []),
            text="**Pʟᴀʏ Sᴛᴏʀᴇ**\n\nYou didn't search anything",
            buttons=Button.switch_inline("Sᴇᴀʀᴄʜ Aɢᴀɪɴ", query="app ", same_peer=True),
        )
        await e.answer([kkkk])
    foles = []
    aap = play_scraper.search(f)
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
    await e.answer(foles)


@in_pattern("mods")
@in_owner
async def _(e):
    try:
        quer = e.text.split(" ", maxsplit=1)[1]
    except IndexError:
        kkkk = e.builder.article(
            title="Search Something",
            text="**Mᴏᴅᴅᴇᴅ Aᴘᴘs**\n\nYou didn't search anything",
            buttons=Button.switch_inline("Sᴇᴀʀᴄʜ Aɢᴀɪɴ", query="mods ", same_peer=True),
        )
        await e.answer([kkkk])
    page = 1
    start = (page - 1) * 3 + 1
    urd = random.randrange(1, 3)
    if urd == 1:
        da = "AIzaSyAyDBsY3WRtB5YPC6aB_w8JAy6ZdXNc6FU"
    if urd == 2:
        da = "AIzaSyBF0zxLlYlPMp9xwMQqVKCQRq8DgdrLXsg"
    if urd == 3:
        da = "AIzaSyDdOKnwnPwVIQ_lbH5sYE4FoXjAKIQV0DQ"
    url = f"https://www.googleapis.com/customsearch/v1?key={da}&cx=25b3b50edb928435b&q={quer}&start={start}"
    data = requests.get(url).json()
    search_items = data.get("items")
    play_scraper.search(quer)
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
                            "Mᴏʀᴇ Mᴏᴅs", query="mods ", same_peer=True
                        ),
                        Button.switch_inline(
                            "Sʜᴀʀᴇ", query=f"mods {quer}", same_peer=False
                        ),
                    ],
                ],
            )
        )
    await e.answer(modss)


@in_pattern("clipart")
@in_owner
async def clip(e):
    try:
        quer = e.text.split(" ", maxsplit=1)[1]
    except IndexError:
        kkkk = e.builder.article(
            title="Search Something",
            text="**Cʟɪᴘᴀʀᴛ Sᴇᴀʀᴄʜ**\n\nYou didn't search anything",
            buttons=Button.switch_inline(
                "Sᴇᴀʀᴄʜ Aɢᴀɪɴ", query="clipart ", same_peer=True
            ),
        )
        await e.answer([kkkk])
    quer = quer.replace(" ", "+")
    sear = f"https://clipartix.com/search/{quer}"
    html = urlopen(sear)
    bs = BeautifulSoup(html, "html.parser", from_encoding="utf-8")
    resul = bs.find_all("img", "attachment-full size-full")
    buil = e.builder
    hm = []
    for res in resul:
        hm += [buil.photo(include_media=True, file=res["src"])]
    await e.answer(hm, gallery=True)
