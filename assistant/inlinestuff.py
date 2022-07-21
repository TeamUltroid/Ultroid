# Ultroid - UserBot
# Copyright (C) 2021-2022 TeamUltroid
#
# This file is a part of < https://github.com/TeamUltroid/Ultroid/ >
# PLease read the GNU Affero General Public License in
# <https://www.github.com/TeamUltroid/Ultroid/blob/main/LICENSE/>.

import base64
import inspect
from datetime import datetime
from random import choice
from re import compile as re_compile

from bs4 import BeautifulSoup as bs
from pyUltroid.functions.misc import google_search
from pyUltroid.functions.tools import (
    _webupload_cache,
    async_searcher,
    get_ofox,
    saavn_search,
    webuploader,
)
from telethon import Button
from telethon.tl.alltlobjects import LAYER, tlobjects
from telethon.tl.types import DocumentAttributeAudio as Audio
from telethon.tl.types import InputWebDocument as wb

from . import *
from . import _ult_cache

SUP_BUTTONS = [
    [
        Button.url("• Repo •", url="https://github.com/TeamUltroid/Ultroid"),
        Button.url("• Support •", url="t.me/ultroidsupportchat"),
    ],
]

ofox = "https://telegra.ph/file/231f0049fcd722824f13b.jpg"
gugirl = "https://telegra.ph/file/0df54ae4541abca96aa11.jpg"
ultpic = "https://telegra.ph/file/4136aa1650bc9d4109cc5.jpg"

apis = [
    "QUl6YVN5QXlEQnNZM1dSdEI1WVBDNmFCX3c4SkF5NlpkWE5jNkZV",
    "QUl6YVN5QkYwenhMbFlsUE1wOXh3TVFxVktDUVJxOERnZHJMWHNn",
    "QUl6YVN5RGRPS253blB3VklRX2xiSDVzWUU0Rm9YakFLSVFWMERR",
]


@in_pattern("ofox", owner=True)
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
        return await e.answer([kkkk])
    device, releases = await get_ofox(match)
    if device.get("detail") is None:
        fox = []
        fullname = device["full_name"]
        codename = device["codename"]
        str(device["supported"])
        maintainer = device["maintainer"]["name"]
        link = f"https://orangefox.download/device/{codename}"
        for data in releases["data"]:
            release = data["type"]
            version = data["version"]
            size = humanbytes(data["size"])
            release_date = datetime.utcfromtimestamp(data["date"]).strftime("%Y-%m-%d")
            text = f"[\xad]({ofox})**OʀᴀɴɢᴇFᴏx Rᴇᴄᴏᴠᴇʀʏ Fᴏʀ**\n\n"
            text += f"`  Fᴜʟʟ Nᴀᴍᴇ: {fullname}`\n"
            text += f"`  Cᴏᴅᴇɴᴀᴍᴇ: {codename}`\n"
            text += f"`  Mᴀɪɴᴛᴀɪɴᴇʀ: {maintainer}`\n"
            text += f"`  Bᴜɪʟᴅ Tʏᴘᴇ: {release}`\n"
            text += f"`  Vᴇʀsɪᴏɴ: {version}`\n"
            text += f"`  Sɪᴢᴇ: {size}`\n"
            text += f"`  Bᴜɪʟᴅ Dᴀᴛᴇ: {release_date}`"
            fox.append(
                await e.builder.article(
                    title=f"{fullname}",
                    description=f"{version}\n{release_date}",
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


@in_pattern("fl2lnk ?(.*)", owner=True)
async def _(e):
    match = e.pattern_match.group(1)
    chat_id, msg_id = match.split(":")
    filename = _webupload_cache[int(chat_id)][int(msg_id)]
    if "/" in filename:
        filename = filename.split("/")[-1]
    __cache = f"{chat_id}:{msg_id}"
    buttons = [
        [
            Button.inline("anonfiles", data=f"flanonfiles//{__cache}"),
            Button.inline("transfer", data=f"fltransfer//{__cache}"),
        ],
        [
            Button.inline("bayfiles", data=f"flbayfiles//{__cache}"),
            Button.inline("x0.at", data=f"flx0.at//{__cache}"),
        ],
        [
            Button.inline("file.io", data=f"flfile.io//{__cache}"),
            Button.inline("siasky", data=f"flsiasky//{__cache}"),
        ],
    ]
    try:
        lnk = [
            await e.builder.article(
                title=f"Upload {filename}",
                text=f"**File:**\n{filename}",
                buttons=buttons,
            )
        ]
    except BaseException as er:
        LOGS.exception(er)
        lnk = [
            await e.builder.article(
                title="fl2lnk",
                text="File not found",
            )
        ]
    await e.answer(lnk, switch_pm="File to Link.", switch_pm_param="start")


@callback(
    re_compile(
        "fl(.*)",
    ),
    owner=True,
)
async def _(e):
    t = (e.data).decode("UTF-8")
    data = t[2:]
    host = data.split("//")[0]
    chat_id, msg_id = data.split("//")[1].split(":")
    filename = _webupload_cache[int(chat_id)][int(msg_id)]
    if "/" in filename:
        filename = filename.split("/")[-1]
    await e.edit(f"Uploading `{filename}` on {host}")
    link = (await webuploader(chat_id, msg_id, host)).strip().replace("\n", "")
    await e.edit(f"Uploaded `{filename}` on {host}.", buttons=Button.url("View", link))


@in_pattern("repo", owner=True)
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


@in_pattern("go", owner=True)
async def gsearch(q_event):
    try:
        match = q_event.text.split(maxsplit=1)[1]
    except IndexError:
        return await q_event.answer(
            [], switch_pm="Google Search. Enter a query!", switch_pm_param="start"
        )
    searcher = []
    gresults = await google_search(match)
    for i in gresults:
        try:
            title = i["title"]
            link = i["link"]
            desc = i["description"]
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


@in_pattern("mods", owner=True)
async def _(e):
    try:
        quer = e.text.split(" ", maxsplit=1)[1]
    except IndexError:
        return await e.answer(
            [], switch_pm="Mod Apps Search. Enter app name!", switch_pm_param="start"
        )
    page = 1
    start = (page - 1) * 3 + 1
    da = base64.b64decode(choice(apis)).decode("ascii")
    url = f"https://www.googleapis.com/customsearch/v1?key={da}&cx=25b3b50edb928435b&q={quer}&start={start}"
    data = await async_searcher(url, re_json=True)
    search_items = data.get("items")
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


# Inspired by @FindXDaBot


@in_pattern("xda", owner=True)
async def xda_dev(event):
    QUERY = event.text.split(maxsplit=1)
    try:
        query = QUERY[1]
    except IndexError:
        return await event.answer(
            [], switch_pm=get_string("instu_3"), switch_pm_param="start"
        )
    le = "https://www.xda-developers.com/search/" + query.replace(" ", "+")
    ct = await async_searcher(le, re_content=True)
    ml = bs(ct, "html.parser", from_encoding="utf-8")
    ml = ml.find_all("div", re_compile("layout_post_"), id=re_compile("post-"))
    out = []
    for on in ml:
        data = on.find_all("img", "xda_image")[0]
        title = data["alt"]
        thumb = data["src"]
        hre = on.find_all("div", "item_content")[0].find("h4").find("a")["href"]
        desc = on.find_all("div", "item_meta clearfix")[0].text
        thumb = wb(thumb, 0, "image/jpeg", [])
        text = f"[{title}]({hre})"
        out.append(
            await event.builder.article(
                title=title, description=desc, url=hre, thumb=thumb, text=text
            )
        )
    uppar = "No Results Found :(" if not out else "|| XDA Search Results ||"
    await event.answer(out, switch_pm=uppar, switch_pm_param="start")


APP_CACHE = {}
RECENTS = {}


@in_pattern("app", owner=True)
async def _(e):
    try:
        f = e.text.split(" ", maxsplit=1)[1].lower()
    except IndexError:
        get_string("instu_1")
        res = []
        if APP_CACHE and RECENTS.get(e.sender_id):
            for a in RECENTS[e.sender_id]:
                if APP_CACHE.get(a):
                    res.append(APP_CACHE[a][0])
        return await e.answer(
            res, switch_pm=get_string("instu_2"), switch_pm_param="start"
        )
    try:
        return await e.answer(
            APP_CACHE[f], switch_pm="Application Searcher.", switch_pm_param="start"
        )
    except KeyError:
        pass
    foles = []
    base_uri = "https://play.google.com"
    url = f"{base_uri}/store/search?q={f.replace(' ', '%20')}&c=apps"
    aap = await async_searcher(url, re_content=True)
    b_ = bs(aap, "html.parser", from_encoding="utf-8")
    aap = b_.find_all("div", "Vpfmgd")
    for z in aap[:10]:
        url = base_uri + z.find("a")["href"]
        scra = await async_searcher(url, re_content=True)
        bp = bs(scra, "html.parser", from_encoding="utf-8")
        name = z.find("div", "WsMG1c nnK0zc")["title"]
        desc = (
            str(bp.find("div", jsname="sngebd"))
            .replace('<div jsname="sngebd">', "")
            .replace("<br/>", "\n")
            .replace("</div>", "")[:300]
            + "..."
        )
        dev = z.find("div", "KoLSrc").text
        icon = z.find("img", "T75of QNCnCf")["data-src"]
        text = f"**••Aᴘᴘ Nᴀᴍᴇ••** [{name}]({icon})\n"
        text += f"**••Dᴇᴠᴇʟᴏᴘᴇʀ••** `{dev}`\n"
        text += f"**••Dᴇsᴄʀɪᴘᴛɪᴏɴ••**\n`{desc}`"
        foles.append(
            await e.builder.article(
                title=name,
                description=dev,
                thumb=wb(icon, 0, "image/jpeg", []),
                text=text,
                link_preview=True,
                buttons=[
                    [Button.url("Lɪɴᴋ", url=url)],
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
    APP_CACHE.update({f: foles})
    if RECENTS.get(e.sender_id):
        RECENTS[e.sender_id].append(f)
    else:
        RECENTS.update({e.sender_id: [f]})
    await e.answer(foles, switch_pm="Application Searcher.", switch_pm_param="start")


PISTON_URI = "https://emkc.org/api/v2/piston/"
PISTON_LANGS = {}


@in_pattern("run", owner=True)
async def piston_run(event):
    try:
        lang = event.text.split()[1]
        code = event.text.split(maxsplit=2)[2]
    except IndexError:
        result = await event.builder.article(
            title="Bad Query",
            description="Usage: [Language] [code]",
            thumb=wb(
                "https://telegra.ph/file/e33c57fc5f1044547e4d8.jpg", 0, "image/jpeg", []
            ),
            text=f'**Inline Usage**\n\n`@{asst.me.username} run python print("hello world")`\n\n[Language List](https://telegra.ph/Ultroid-09-01-6)',
        )
        return await event.answer([result])
    if not PISTON_LANGS:
        se = await async_searcher(PISTON_URI + "runtimes", re_json=True)
        PISTON_LANGS.update({lang.pop("language"): lang for lang in se})
    if lang in PISTON_LANGS.keys():
        version = PISTON_LANGS[lang]["version"]
    else:
        result = await event.builder.article(
            title="Unsupported Language",
            description="Usage: [Language] [code]",
            thumb=wb(
                "https://telegra.ph/file/e33c57fc5f1044547e4d8.jpg", 0, "image/jpeg", []
            ),
            text=f'**Inline Usage**\n\n`@{asst.me.username} run python print("hello world")`\n\n[Language List](https://telegra.ph/Ultroid-09-01-6)',
        )
        return await event.answer([result])
    output = await async_searcher(
        PISTON_URI + "execute",
        post=True,
        json={"language": lang, "version": version, "files": [{"content": code}]},
        re_json=True,
    )
    output = output["run"]["output"] or get_string("instu_4")
    if len(output) > 3000:
        output = output[:3000] + "..."
    result = await event.builder.article(
        title="Result",
        description=output,
        text=f"• **Language:**\n`{lang}`\n\n• **Code:**\n`{code}`\n\n• **Result:**\n`{output}`",
        thumb=wb(
            "https://telegra.ph/file/871ee4a481f58117dccc4.jpg", 0, "image/jpeg", []
        ),
        buttons=Button.switch_inline("Fork", query=event.text, same_peer=True),
    )
    await event.answer([result], switch_pm="• Piston •", switch_pm_param="start")


FDROID_ = {}


@in_pattern("fdroid", owner=True)
async def do_magic(event):
    try:
        match = event.text.split(" ", maxsplit=1)[1].lower()
    except IndexError:
        return await event.answer(
            [], switch_pm="Enter Query to Search", switch_pm_param="start"
        )
    if FDROID_.get(match):
        return await event.answer(
            FDROID_[match], switch_pm=f"• Results for {match}", switch_pm_param="start"
        )
    link = "https://search.f-droid.org/?q=" + match.replace(" ", "+")
    content = await async_searcher(link, re_content=True)
    BSC = bs(content, "html.parser", from_encoding="utf-8")
    ress = []
    for dat in BSC.find_all("a", "package-header")[:10]:
        image = dat.find("img", "package-icon")["src"]
        if image.endswith("/"):
            image = "https://telegra.ph/file/a8dd4a92c5a53a89d0eff.jpg"
        title = dat.find("h4", "package-name").text.strip()
        desc = dat.find("span", "package-summary").text.strip()
        text = f"• **Name :** `{title}`\n\n"
        text += f"• **Description :** `{desc}`\n"
        text += f"• **License :** `{dat.find('span', 'package-license').text.strip()}`"
        imga = wb(image, 0, "image/jpeg", [])
        ress.append(
            await event.builder.article(
                title=title,
                type="photo",
                description=desc,
                text=text,
                content=imga,
                thumb=imga,
                include_media=True,
                buttons=[
                    Button.inline(
                        "• Download •", "fd" + dat["href"].split("packages/")[-1]
                    ),
                    Button.switch_inline("• Share •", query=event.text),
                ],
            )
        )
    msg = f"Showing {len(ress)} Results!" if ress else "No Results Found"
    FDROID_.update({match: ress})
    await event.answer(ress, switch_pm=msg, switch_pm_param="start")


_koo_ = {}


@in_pattern("koo", owner=True)
async def koo_search(ult):
    """Search Users on koo with API"""
    try:
        match = ult.text.split(maxsplit=1)[1].lower()
        match_ = match
    except IndexError:
        return await ult.answer(
            [], switch_pm="Enter Query to Search..", switch_pm_param="start"
        )
    if _koo_.get(match):
        return await ult.answer(
            _koo_[match], switch_pm="• Koo Search •", switch_pm_param="start"
        )
    res = []
    se_ = None
    key_count = None
    if " | " in match:
        match = match.split(" | ", maxsplit=1)
        try:
            key_count = int(match[1])
        except ValueError:
            pass
        match = match[0]
    match = match.replace(" ", "+")
    req = await async_searcher(
        f"https://www.kooapp.com/apiV1/search?query={match}&searchType=EXPLORE",
        re_json=True,
    )
    if key_count:
        try:
            se_ = [req["feed"][key_count - 1]]
        except KeyError:
            pass
    if not se_:
        se_ = req["feed"]
    for count, feed in enumerate(se_[:10]):
        if feed["uiItemType"] == "search_profile":
            count += 1
            item = feed["items"][0]
            profileImage = (
                item["profileImageBaseUrl"]
                if item.get("profileImageBaseUrl")
                else "https://telegra.ph/file/dc28e69bd7ea2c0f25329.jpg"
            )
            extra = await async_searcher(
                "https://www.kooapp.com/apiV1/users/handle/" + item["userHandle"],
                re_json=True,
            )
            img = wb(profileImage, 0, "image/jpeg", [])
            text = f"‣ **Name :** `{item['name']}`"
            if extra.get("title"):
                text += f"\n‣ **Title :** `{extra['title']}`"
            text += f"\n‣ **Username :** `@{item['userHandle']}`"
            if extra.get("description"):
                text += f"\n‣ **Description :** `{extra['description']}`"
            text += f"\n‣ **Followers :** `{extra['followerCount']}`    ‣ **Following :** {extra['followingCount']}"
            if extra.get("socialProfile") and extra["socialProfile"].get("website"):
                text += f"\n‣ **Website :** {extra['socialProfile']['website']}"
            res.append(
                await ult.builder.article(
                    title=item["name"],
                    description=item.get("title") or f"@{item['userHandle']}",
                    type="photo",
                    content=img,
                    thumb=img,
                    include_media=True,
                    text=text,
                    buttons=[
                        Button.url(
                            "View", "https://kooapp.com/profile/" + item["userHandle"]
                        ),
                        Button.switch_inline(
                            "• Share •",
                            query=ult.text if key_count else ult.text + f" | {count}",
                        ),
                    ],
                )
            )
    if not res:
        switch = "No Results Found :("
    else:
        _koo_.update({match_: res})
        switch = f"Showing {len(res)} Results!"
    await ult.answer(res, switch_pm=switch, switch_pm_param="start")


# Thanks to OpenSource
_bearer_collected = [
    "AAAAAAAAAAAAAAAAAAAAALIKKgEAAAAA1DRuS%2BI7ZRKiagD6KHYmreaXomo%3DP5Vaje4UTtEkODg0fX7nCh5laSrchhtLxeyEqxXpv0w9ZKspLD",
    "AAAAAAAAAAAAAAAAAAAAAL5iUAEAAAAAmo6FYRjqdKlI3cNziIm%2BHUQB9Xs%3DS31pj0mxARMTOk2g9dvQ1yP9wknvY4FPBPUlE00smJcncw4dPR",
    "AAAAAAAAAAAAAAAAAAAAAN6sVgEAAAAAMMjMMWrwgGyv7YQOWN%2FSAsO5SGM%3Dg8MG9Jq93Rlllaok6eht7HvRCruN4Vpzp4NaVsZaaHHWSTzKI8",
]


@in_pattern("twitter", owner=True)
async def twitter_search(event):
    try:
        match = event.text.split(maxsplit=1)[1].lower()
    except IndexError:
        return await event.answer(
            [], switch_pm="Enter Query to Search", switch_pm_param="start"
        )
    try:
        return await event.answer(
            _ult_cache["twitter"][match],
            switch_pm="• Twitter Search •",
            switch_pm_param="start",
        )
    except KeyError:
        pass
    headers = {"Authorization": "bearer " + choice(_bearer_collected)}
    res = await async_searcher(
        f"https://api.twitter.com/1.1/users/search.json?q={match}",
        headers=headers,
        re_json=True,
    )
    reso = []
    for user in res:
        thumb = wb(user["profile_image_url_https"], 0, "image/jpeg", [])
        if user.get("profile_banner_url"):
            url = user["profile_banner_url"]
            text = f"[\xad]({url})• **Name :** `{user['name']}`\n"
        else:
            text = f"• **Name :** `{user['name']}`\n"
        text += f"• **Description :** `{user['description']}`\n"
        text += f"• **Username :** `@{user['screen_name']}`\n"
        text += f"• **Followers :** `{user['followers_count']}`    • **Following :** `{user['friends_count']}`\n"
        pro_ = "https://twitter.com/" + user["screen_name"]
        text += f"• **Link :** [Click Here]({pro_})\n_"
        reso.append(
            await event.builder.article(
                title=user["name"],
                description=user["description"],
                url=pro_,
                text=text,
                thumb=thumb,
            )
        )
    swi_ = "No User Found :(" if not reso else f"🐦 Showing {len(reso)} Results!"
    await event.answer(reso, switch_pm=swi_, switch_pm_param="start")
    if _ult_cache.get("twitter"):
        _ult_cache["twitter"].update({match: reso})
    else:
        _ult_cache.update({"twitter": {match: reso}})


_savn_cache = {}


@in_pattern("saavn", owner=True)
async def savn_s(event):
    try:
        query = event.text.split(maxsplit=1)[1].lower()
    except IndexError:
        return await event.answer(
            [], switch_pm="Enter Query to search 🔍", switch_pm_param="start"
        )
    if query in _savn_cache:
        return await event.answer(
            _savn_cache[query],
            switch_pm=f"Showing Results for {query}",
            switch_pm_param="start",
        )
    results = await saavn_search(query)
    swi = "No Results Found!" if not results else "🎵 Saavn Search"
    res = []
    for song in results:
        thumb = wb(song["image"], 0, "image/jpeg", [])
        text = f"• **Title :** {song['song']}"
        text += f"\n• **Year :** {song['year']}"
        text += f"\n• **Lang :** {song['language']}"
        text += f"\n• **Artist :** {song['primary_artists']}"
        text += f"\n• **Release Date :** {song['release_date']}"
        res.append(
            await event.builder.article(
                title=song["song"],
                type="audio",
                text=text,
                include_media=True,
                buttons=Button.switch_inline(
                    "Search Again 🔍", query="saavn", same_peer=True
                ),
                thumb=thumb,
                content=wb(
                    song["media_url"],
                    0,
                    "audio/mp4",
                    [
                        Audio(
                            title=song["song"],
                            duration=int(song["duration"]),
                            performer=song["primary_artists"],
                        )
                    ],
                ),
            )
        )
    await event.answer(res, switch_pm=swi, switch_pm_param="start")
    _savn_cache.update({query: res})


_OMG = {}


@in_pattern("omgu", owner=True)
async def omgubuntu(ult):
    try:
        match = ult.text.split(maxsplit=1)[1].lower()
    except IndexError:
        return await ult.answer(
            [], switch_pm="Enter Query to search...", switch_pm_param="start"
        )
    if _OMG.get(match):
        return await ult.answer(
            _OMG[match], switch_pm="OMG Ubuntu Search :]", switch_pm_param="start"
        )
    get_web = "https://www.omgubuntu.co.uk/?s=" + match.replace(" ", "+")
    get_ = await async_searcher(get_web, re_content=True)
    BSC = bs(get_, "html.parser", from_encoding="utf-8")
    res = []
    for cont in BSC.find_all("div", "sbs-layout__item"):
        img = cont.find("div", "sbs-layout__image")
        url = img.find("a")["href"]
        src = img.find("img")["src"]
        con = cont.find("div", "sbs-layout__content")
        tit = con.find("a", "layout__title-link")
        title = tit.text.strip()
        desc = con.find("p", "layout__description").text.strip()
        text = f"[{title.strip()}]({url})\n\n{desc}"
        img = wb(src, 0, "image/jpeg", [])
        res.append(
            await ult.builder.article(
                title=title,
                type="photo",
                description=desc,
                url=url,
                text=text,
                buttons=Button.switch_inline(
                    "Search Again", query=ult.text, same_peer=True
                ),
                include_media=True,
                content=img,
                thumb=img,
            )
        )
    await ult.answer(
        res,
        switch_pm=f"Showing {len(res)} results!" if res else "No Results Found :[",
        switch_pm_param="start",
    )
    _OMG[match] = res


@in_pattern("tl", owner=True)
async def inline_tl(ult):
    try:
        match = ult.text.split(maxsplit=1)[1]
    except IndexError:
        text = f"**Telegram TlObjects Searcher.**\n__(Don't use if you don't know what it is!)__\n\n• Example Usage\n`@{asst.me.username} tl GetFullUserRequest`"
        return await ult.answer(
            [
                await ult.builder.article(
                    title="How to Use?",
                    description="Tl Searcher by Ultroid",
                    url="https://t.me/TheUltroid",
                    text=text,
                )
            ],
            switch_pm="Tl Search 🔍",
            switch_pm_param="start",
        )
    res = []
    for key in tlobjects.values():
        if match.lower() in key.__name__.lower():
            tyyp = "Function" if "tl.functions." in str(key) else "Type"
            text = f"**Name:** `{key.__name__}`\n"
            text += f"**Category:** `{tyyp}`\n"
            text += f"\n`from {key.__module__} import {key.__name__}`\n\n"
            args = str(inspect.signature(key))[1:][:-1]
            if args:
                text += "**Parameter:**\n"
                for para in args.split(","):
                    text += " " * 4 + "`" + para + "`\n"
            text += f"\n**Layer:** `{LAYER}`"
            res.append(
                await ult.builder.article(
                    title=key.__name__,
                    description=tyyp,
                    url="https://t.me/TheUltroid",
                    text=text[:4000],
                )
            )
    if not res:
        mo = f"No Results for {match}!"
    else:
        mo = f"Showing {len(res)} results!"
    await ult.answer(res[:50], switch_pm=mo, switch_pm_param="start")


@in_pattern("gh", owner=True)
async def gh_feeds(ult):
    try:
        username = ult.text.split(maxsplit=1)[1]
    except IndexError:
        return await ult.answer(
            [],
            switch_pm="Enter Github Username to see feeds...",
            switch_pm_param="start",
        )
    if not username.endswith("."):
        return await ult.answer(
            [], switch_pm="End your query with . to search...", switch_pm_param="start"
        )
    username = username[:-1]
    data = await async_searcher(
        f"https://api.github.com/users/{username}/events", re_json=True
    )
    if not isinstance(data, list):
        msg = ""
        for ak in list(data.keys()):
            msg += ak + ": `" + data[ak] + "`\n"
        return await ult.answer(
            [
                await ult.builder.article(
                    title=data["message"], text=msg, link_preview=False
                )
            ],
            cache_time=300,
            switch_pm="Error!!!",
            switch_pm_param="start",
        )
    res = []
    res_ids = []
    for cont in data[:50]:
        text = f"<b><a href='https://github.com/{username}'>@{username}</a></b>"
        title = f"@{username}"
        extra = None
        if cont["type"] == "PushEvent":
            text += " pushed in"
            title += " pushed in"
            dt = cont["payload"]["commits"][-1]
            url = "https://github.com/" + dt["url"].split("/repos/")[-1]
            extra = f"\n-> <b>message:</b> <code>{dt['message']}</code>"
        elif cont["type"] == "IssueCommentEvent":
            title += " commented at"
            text += " commented at"
            url = cont["payload"]["comment"]["html_url"]
        elif cont["type"] == "CreateEvent":
            title += " created"
            text += " created"
            url = "https://github.com/" + cont["repo"]["name"]
        elif cont["type"] == "PullRequestEvent":
            if (
                cont["payload"]["pull_request"].get("user", {}).get("login")
                != username.lower()
            ):
                continue
            url = cont["payload"]["pull_request"]["html_url"]
            text += " created a pull request in"
            title += " created a pull request in"
        elif cont["type"] == "ForkEvent":
            text += " forked"
            title += " forked"
            url = cont["payload"]["forkee"]["html_url"]
        else:
            continue
        repo = cont["repo"]["name"]
        repo_url = "https://github.com/" + repo
        title += " " + repo
        text += f" <b><a href='{repo_url}'>{repo}</a></b>"
        if extra:
            text += extra
        thumb = wb(cont["actor"]["avatar_url"], 0, "image/jpeg", [])
        article = await ult.builder.article(
            title=title,
            text=text,
            url=repo_url,
            parse_mode="html",
            link_preview=False,
            thumb=thumb,
            buttons=[
                Button.url("View", url),
                Button.switch_inline("Search again", query=ult.text, same_peer=True),
            ],
        )
        if article.id not in res_ids:
            res_ids.append(article.id)
            res.append(article)
    if res:
        msg = f"Showing {len(res)} feeds!"
    else:
        msg = "Nothing Found"
    await ult.answer(res, cache_time=5000, switch_pm=msg, switch_pm_param="start")
