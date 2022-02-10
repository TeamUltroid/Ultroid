# Ultroid - UserBot
#
# This file is a part of < https://github.com/TeamUltroid/Ultroid/ >
# PLease read the GNU Affero General Public License in
# <https://www.github.com/TeamUltroid/Ultroid/blob/main/LICENSE/>.
"""
✘ Commands Available -

• `{i}eod`
    `Get Event of the Today`

• `{i}pntrst <link/id>`
    Download and send pinterest pins

• `{i}gadget <search query>`
    Gadget Search from Telegram.

• `{i}randomuser`
   Generate details about a random user.

• `{i}ascii <reply image>`
    Convert replied image into html.
"""

import calendar
import os
from datetime import datetime as dt

from bs4 import BeautifulSoup as bs
from htmlwebshot import WebShot
from img2html.converter import Img2HTMLConverter

from . import async_searcher, get_random_user_data, get_string, re, ultroid_cmd


@ultroid_cmd(pattern="eod$")
async def diela(e):
    m = await e.eor(get_string("com_1"))
    li = "https://daysoftheyear.com"
    te = "🎊 **Events of the Day**\n\n"
    da = dt.today()
    month = da.strftime("%b")
    li += "/days/" + month + "/" + da.strftime("%F").split("-")[2]
    ct = await async_searcher(li, re_content=True)
    bt = bs(ct, "html.parser", from_encoding="utf-8")
    ml = bt.find_all("a", "js-link-target", href=re.compile("daysoftheyear.com/days"))
    for eve in ml[:5]:
        te += "• " + f'[{eve.text}]({eve["href"]})\n'
    await m.edit(te, link_preview=False)


@ultroid_cmd(
    pattern="pntrst( (.*)|$)",
)
async def pinterest(e):
    m = e.pattern_match.group(1).strip()
    if not m:
        return await e.eor("`Give pinterest link.`", time=3)
    soup = await async_searcher(
        "https://www.expertstool.com/download-pinterest-video/",
        data={"url": m},
        post=True,
    )
    try:
        _soup = bs(soup, "html.parser").find("table").tbody.find_all("tr")
    except BaseException:
        return await e.eor("`Wrong link or private pin.`", time=5)
    if len(_soup) > 1:
        file = _soup[1]
    else:
        file = _soup[0]
    file = file.td.a["href"]
    await e.client.send_file(e.chat_id, file, caption=f"Pin:- {m}")


@ultroid_cmd(pattern="gadget( (.*)|$)")
async def mobs(e):
    mat = e.pattern_match.group(1).strip()
    if not mat:
        await e.eor("Please Give a Mobile Name to look for.")
    query = mat.replace(" ", "%20")
    jwala = f"https://gadgets.ndtv.com/search?searchtext={query}"
    c = await async_searcher(jwala)
    b = bs(c, "html.parser", from_encoding="utf-8")
    co = b.find_all("div", "rvw-imgbox")
    if not co:
        return await e.eor("No Results Found!")
    bt = await e.eor(get_string("com_1"))
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
    if imu == []:
        imu = None
    await e.reply(out, file=imu, link_preview=False)
    await bt.delete()


@ultroid_cmd(pattern="randomuser")
async def _gen_data(event):
    x = await event.eor(get_string("com_1"))
    msg, pic = await get_random_user_data()
    await event.reply(file=pic, message=msg)
    await x.delete()


@ultroid_cmd(
    pattern="ascii( (.*)|$)",
)
async def _(e):
    if not e.reply_to_msg_id:
        return await e.eor(get_string("ascii_1"))
    m = await e.eor(get_string("ascii_2"))
    img = await (await e.get_reply_message()).download_media()
    char = (
        "■"
        if not e.pattern_match.group(1).strip()
        else e.pattern_match.group(1).strip()
    )
    converter = Img2HTMLConverter(char=char)
    html = converter.convert(img)
    shot = WebShot(quality=85)
    pic = await shot.create_pic_async(html=html)
    await m.delete()
    await e.reply(file=pic)
    os.remove(pic)
    os.remove(img)
