from . import ultroid_cmd, get_string, async_searcher
from bs4 import BeautifulSoup as bs


@ultroid_cmd(pattern="sticker( (.*)|$)")
async def _(event):
    x = event.pattern_match.group(1).strip()
    if not x:
        return await event.eor("`Give something to search`")
    uu = await event.eor(get_string("com_1"))
    z = bs(
        await async_searcher(f"https://combot.org/telegram/stickers?q={x}"),
        "html.parser",
    )

    packs = z.find_all("div", "sticker-pack__header")
    sticks = {
        c.a["href"]: c.find("div", {"class": "sticker-pack__title"}).text for c in packs
    }

    if not sticks:
        return await uu.edit(get_string("spcltool_9"))
    a = "SᴛɪᴄᴋEʀs Aᴠᴀɪʟᴀʙʟᴇ ~\n\n"
    for _, value in sticks.items():
        a += f"<a href={_}>{value}</a>\n"
    await uu.edit(a, parse_mode="html")
