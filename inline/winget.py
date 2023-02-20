# Ultroid - UserBot
# Copyright (C) 2020 TeamUltroid
#
# This file is a part of < https://github.com/TeamUltroid/Ultroid/ >
# PLease read the GNU Affero General Public License in
# <https://www.github.com/TeamUltroid/Ultroid/blob/main/LICENSE/>

from telethon.tl.custom import Button

from . import async_searcher, get_string, in_pattern


@in_pattern("winget", owner=True, button={"Search Winget": "winget telegram"})
async def search_winget(event):
    QUERY = event.text.split(maxsplit=1)
    try:
        query = QUERY[1]
    except IndexError:
        return await event.answer(
            [], switch_pm=get_string("instu_3"), switch_pm_param="start"
        )
    le = (
        "https://api.winget.run/v2/packages?ensureContains=true&partialMatch=true&take=20&query="
        + query.replace(" ", "+")
    )
    ct = await async_searcher(le, re_json=True)
    out = []
    for on in ct["Packages"]:
        data = on["Latest"]
        name = data["Name"]
        homep = data.get("Homepage")
        text = f"> **{name}**\n - {data['Description']}\n\n`winget install {on['Id']}`\n\n**Version:** `{on['Versions'][0]}`\n"
        text += "**Tags:**" + " ".join([f"#{_}" for _ in data["Tags"]])
        if homep:
            text += f"\n\n{homep}"
        out.append(
            await event.builder.article(
                title=name,
                description=data["Description"],
                url=homep,
                text=text,
                buttons=Button.switch_inline(
                    "Search Again", "winget", same_peer=True),
            )
        )
    uppar = "|> Winget Results" if out else "No Results Found :("
    await event.answer(out, switch_pm=uppar, switch_pm_param="start", cache_time=3000)
