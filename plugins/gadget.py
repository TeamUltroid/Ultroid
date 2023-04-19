import re

from bs4 import BeautifulSoup as bs
from utilities.helper import fetch

from .. import fetch, get_string, ultroid_cmd


@ultroid_cmd(pattern="gadget( (.*)|$)")
async def mobs(e):
    mat = e.pattern_match.group(1).strip()
    if not mat:
        await e.eor("Please Give a Mobile Name to look for.")
    query = mat.replace(" ", "%20")
    jwala = f"https://gadgets.ndtv.com/search?searchtext={query}"
    c = await fetch(jwala)
    b = bs(c, "html.parser", from_encoding="utf-8")
    co = b.find_all("div", "rvw-imgbox")
    if not co:
        return await e.eor("No Results Found!")
    bt = await e.eor(get_string("com_1"))
    out = "**📱 Mobile / Gadgets Search**\n\n"
    li = co[0].find("a")
    imu, title = None, li.find("img")["title"]
    cont = await fetch(li["href"])
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
