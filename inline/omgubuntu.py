# Ultroid - UserBot
# Copyright (C) 2021-2022 TeamUltroid
#
# This file is a part of < https://github.com/TeamUltroid/Ultroid/ >
# PLease read the GNU Affero General Public License in
# <https://www.github.com/TeamUltroid/Ultroid/blob/main/LICENSE/>.


from bs4 import BeautifulSoup as bs
from telethon.tl.custom import Button
from telethon.tl.types import InputWebDocument as wb

from .. import async_searcher, in_pattern

_OMG = {}


@in_pattern("omgu", owner=True, button={"OᴍɢUʙᴜɴᴛᴜ": "omgu cutefish"})
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
    get_ = await async_searcher(get_web)
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
