#
# Ultroid - UserBot
#
# This file is a part of < https://github.com/TeamUltroid/Ultroid/ >
# PLease read the GNU Affero General Public License in
# <https://www.github.com/TeamUltroid/Ultroid/blob/main/LICENSE/>.
"""
✘ Commands Available -

• `{i}gadget <search query>`
    Gadget Search from Telegram.

"""
import requests
from bs4 import BeautifulSoup as bs

from . import *


@ultroid_cmd(pattern="gadget ?(.*)")
async def mobs(e):
    mat = e.pattern_match.group(1)
    if not mat:
        await eor(e, "Please Give a Mobile Name to look for.")
    query = mat.replace(" ", "%20")
    jwala = f"https://gadgets.ndtv.com/search?searchtext={query}"
    c = requests.get(jwala).content
    b = bs(c, "html.parser", from_encoding="utf-8")
    bt = await eor(e, "`Processing...`")
    try:
        out = "**📱 Mobile / Gadgets Search**\n\n"
        re = b.find_all("div", "rvw-imgbox")
        li = re[0].findNext()["href"]
        mg = re[0].findNext().findNext().findNext()
        tit = mg["title"]
        cont = requests.get(li).content
        nu = bs(cont, "html.parser", from_encoding="utf-8")
        req = nu.find_all("div", "_pdsd")
        imu = nu.find_all("source", type="image/webp")[0]["srcset"].split("?")[0]
        out += f"☑️ **[{tit}]({li})**\n\n"
        for fp in req:
            ty = fp.findNext()
            out += f"- **{ty.text}** - `{ty.findNext().text}`\n"
        out += "_"
        await e.reply(out, file=imu)
        if e.out:
            await bt.delete()
    except Exception as a:
        print(a)
        await eor(e, "No Results Found")
