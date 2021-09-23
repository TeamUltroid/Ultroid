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
from bs4 import BeautifulSoup as bs

from . import *


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
    bt = await eor(e, "`Processing...`")
    imu = None
    out = "**📱 Mobile / Gadgets Search**\n\n"
    li = co[0].find("a")
    cont = await async_searcher(li["href"])
    nu = bs(cont, "html.parser", from_encoding="utf-8")
    req = nu.find_all("div", "_pdsd")
    imu = nu.find_all(
        "img", src=re.compile("https://i.gadgets360cdn.com/products/large/")
    )
    if imu:
        imu = imu[0]["src"]
    out += f"☑️ **[{li['title']}]({li['href']})**\n\n"
    for fp in req:
        ty = fp.findNext()
        out += f"- **{ty.text}** - `{ty.findNext().text}`\n"
    out += "_"
    await e.reply(out, file=imu)
    await bt.delete()
