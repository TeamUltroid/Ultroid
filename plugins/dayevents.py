# Ultroid - UserBot
# Copyright (C) 2021 TeamUltroid
#
# This file is a part of < https://github.com/TeamUltroid/Ultroid/ >
# PLease read the GNU Affero General Public License in
# <https://www.github.com/TeamUltroid/Ultroid/blob/main/LICENSE/>.

"""
✘ Commands Available -

• `{i}eod` or `{i}eod <dd/mm>`
    `Get Event of the Day`
"""

import re
from datetime import datetime as dr

import requests as r
from bs4 import BeautifulSoup as bs

from . import *


@ultroid_cmd(pattern="eod ?(.*)")
async def diela(e):
    match = e.pattern_match.group(1)
    m = await eor(e, "`Processing... `")
    li = "https://daysoftheyear.com"
    te = "♻️ **Events of the Day**\n\n"
    if match:
        date = match.split("/")[0]
        month = match.split("/")[1]
        li += "/days/2021/" + month + "/" + date
        te = f"♻️ **Events for {match}/2021**\n\n"
    else:
        da = dr.today().strftime("%F").split("-")
        li += "/days/2021/" + da[1] + "/" + da[2]
    ct = r.get(li).content
    bt = bs(ct, "html.parser", from_encoding="utf-8")
    ml = bt.find_all("a", "js-link-target", href=re.compile("daysoftheyear.com/days"))
    for eve in ml[:5]:
        te += "• " + f'[{eve.text}]({eve["href"]})\n'
    await m.edit(te, link_preview=False)
