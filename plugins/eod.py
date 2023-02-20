import re
from datetime import datetime as dt

from bs4 import BeautifulSoup as bs

from . import async_searcher, get_string, ultroid_cmd


@ultroid_cmd(pattern="eod$")
async def diela(e):
    m = await e.eor(get_string("com_1"))
    li = "https://daysoftheyear.com"
    te = "🎊 **Events of the Day**\n\n"
    da = dt.now()
    month = da.strftime("%b")
    li += f"/days/{month}/" + da.strftime("%F").split("-")[2]
    ct = await async_searcher(li)
    bt = bs(ct, "html.parser", from_encoding="utf-8")
    ml = bt.find_all(
        "a",
        "js-link-target",
        href=re.compile("daysoftheyear.com/days"))
    for eve in ml[:5]:
        te += f'• [{eve.text}]({eve["href"]})\n'
    await m.edit(te, link_preview=False)
