# Ultroid - UserBot
#
# This file is a part of < https://github.com/TeamUltroid/Ultroid/ >
# PLease read the GNU Affero General Public License in
# <https://www.github.com/TeamUltroid/Ultroid/blob/main/LICENSE/>.
"""
✘ Commands Available -

• `{i}eod` or `{i}eod <dd/mm>`
    `Get Event of the Day`

• `{i}pntrst <link/id>`
    Download and send pinterest pins

• `{i}gadget <search query>`
    Gadget Search from Telegram.

• `{i}randomuser`
   Generate details about a random user.
"""

import os

from bs4 import BeautifulSoup as bs
from requests import get
from datetime import datetime as dt
from . import *

_base = "https://pinterestdownloader.com/download?url="


def gib_link(link):
    if link.startswith("https"):
        return _base + link.replace(":", "%3A").replace("/", "%2F")
    return _base + f"https%3A%2F%2Fpin.it%2F{link}"


@ultroid_cmd(pattern="eod ?(.*)")
async def diela(e):
    match = e.pattern_match.group(1)
    m = await eor(e, get_string("com_1"))
    li = "https://daysoftheyear.com"
    te = "🎊 **Events of the Day**\n\n"
    if match:
        date = match.split("/")[0]
        month = match.split("/")[1]
        li += "/days/2021/" + month + "/" + date
        te = get_string("eod_2").format(match)
    else:
        da = dr.today().strftime("%F").split("-")
        li += "/days/2021/" + da[1] + "/" + da[2]
    ct = r.get(li).content
    bt = bs(ct, "html.parser", from_encoding="utf-8")
    ml = bt.find_all("a", "js-link-target", href=re.compile("daysoftheyear.com/days"))
    for eve in ml[:5]:
        te += "• " + f'[{eve.text}]({eve["href"]})\n'
    await m.edit(te, link_preview=False)

@ultroid_cmd(
    pattern="pntrst ?(.*)",
)
async def pinterest(e):
    m = e.pattern_match.group(1)
    get_link = get(gib_link(m)).text
    hehe = bs(get_link, "html.parser")
    hulu = hehe.find_all("a", {"class": "download_button"})
    if len(hulu) < 1:
        await eor(e, "`Wrong link or private pin.`", time=5)
    elif len(hulu) > 1:
        video = await fast_download(hulu[0]["href"])
        thumb = await fast_download(hulu[1]["href"])
        await e.delete()
        await e.client.send_file(e.chat_id, video, thumb=thumb, caption=f"Pin:- {m}")
        [os.remove(file) for file in [video, thumb]]
    else:
        await e.delete()
        await e.client.send_file(e.chat_id, hulu[0]["href"], caption=f"Pin:- {m}")


@ultroid_cmd(pattern="gadget ?(.*)")
async def mobs(e):
    mat = e.pattern_match.group(1)
    if not mat:
        await eor(e, "Please Give a Mobile Name to look for.")
    query = mat.replace(" ", "%20")
    jwala = f"https://gadgets.ndtv.com/search?searchtext={query}"
    c = await async_searcher(jwala)
    b = bs(c, "html.parser", from_encoding="utf-8")
    co = b.find_all("div", "rvw-imgbox")
    if not co:
        return await eor(e, "No Results Found!")
    bt = await eor(e, get_string("com_1"))
    out = "**📱 Mobile / Gadgets Search**\n\n"
    li = co[0].find("a")
    imu, title = None, li.find("img")["title"]
    cont = await async_searcher(li["href"])
    nu = bs(cont, "html.parser", from_encoding="utf-8")
    req = nu.find_all("div", "_pdsd")
    imu = nu.find_all(
        "img", src=re.compile("https://i.gadgets360cdn.com/products/large/")
    )
    if imu:
        imu = imu[0]["src"].split("?")[0] + "?downsize=*:420&output-quality=80"
    out += f"☑️ **[{title}]({li['href']})**\n\n"
    for fp in req:
        ty = fp.findNext()
        out += f"- **{ty.text}** - `{ty.findNext().text}`\n"
    out += "_"
    await e.reply(out, file=imu)
    await bt.delete()


@ultroid_cmd(pattern="randomuser")
async def _gen_data(event):
    x = await eor(event, get_string("com_1"))
    msg, pic = get_random_user_data()
    await event.reply(file=pic, message=msg)
    await x.delete()
