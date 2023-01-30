# Ultroid - UserBot
# Copyright (C) 2020 TeamUltroid
#
# This file is a part of < https://github.com/TeamUltroid/Ultroid/ >
# PLease read the GNU Affero General Public License in
# <https://www.github.com/TeamUltroid/Ultroid/blob/main/LICENSE/>

import re
from bs4 import BeautifulSoup as bs
from telethon.tl.types import InputWebDocument as wb
from .. import get_string, async_searcher, in_pattern, InlinePlugin

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
<<<<<<< HEAD
    le = "https://www.xda-developers.com/search/" + query.replace(" ", "+")
    ct = await async_searcher(le, re_content=True)
    ml = bs(ct, "html.parser", from_encoding="utf-8")
    ml = ml.find_all("div", re.compile("layout_post_"), id=re.compile("post-"))
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
=======
    le = "https://www.xda-developers.com/search/?q=" + query.replace(" ", "+")
    ct = await async_searcher(le, re_content=True)
    ml = bs(ct, "html.parser", from_encoding="utf-8")
    ml = ml.find_all("article", re.compile("browse-clip"))
    out = []
    for on in ml:
        thumb = on.find_all("source")[-1].get("srcset")
        title = on.find("h3", "bc-title")
        href = "https://www.xda-developers.com" + title.find("a").get("href")
        desc = on.find("p", "bc-excerpt").text
        title = title.text
        thumb = wb(thumb, 0, "image/jpeg", []).
        text = f"[{title}]({href})"
        out.append(
            await event.builder.article(
                title=title, description=desc, url=href, thumb=thumb, text=text
>>>>>>> 14824172f5009252912019ef99b23b1ffd12fe9e
            )
        )
    uppar = "|| XDA Search Results ||" if out else "No Results Found :("
    await event.answer(out, switch_pm=uppar, switch_pm_param="start")


InlinePlugin.update({"Search on XDA": "xda telegram"})
