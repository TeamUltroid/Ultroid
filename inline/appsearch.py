from html import unescape

from telethon.tl.types import InputWebDocument as wb

from .. import Button, async_searcher, get_string, in_pattern

APP_CACHE = {}
RECENTS = {}
PLAY_API = "https://googleplay.onrender.com/api/apps?q="


@in_pattern("app", owner=True, button={"App Search": "app telegram"})
async def _(e):
    try:
        f = e.text.split(maxsplit=1)[1].lower()
    except IndexError:
        get_string("instu_1")
        res = []
        if APP_CACHE and RECENTS.get(e.sender_id):
            res.extend(
                APP_CACHE[a][0] for a in RECENTS[e.sender_id] if APP_CACHE.get(a)
            )
        return await e.answer(
            res, switch_pm=get_string("instu_2"), switch_pm_param="start"
        )
    try:
        return await e.answer(
            APP_CACHE[f], switch_pm="Application Searcher.", switch_pm_param="start"
        )
    except KeyError:
        pass
    foles = []
    url = PLAY_API + f.replace(" ", "+")
    aap = await async_searcher(url, re_json=True)
    for z in aap["results"][:50]:
        url = "https://play.google.com/store/apps/details?id=" + z["appId"]
        name = z["title"]
        desc = unescape(z["summary"])[:300].replace("<br>", "\n") + "..."
        dev = z["developer"]["devId"]
        text = f"**••Aᴘᴘ Nᴀᴍᴇ••** [{name}]({url})\n"
        text += f"**••Dᴇᴠᴇʟᴏᴘᴇʀ••** `{dev}`\n"
        text += f"**••Dᴇsᴄʀɪᴘᴛɪᴏɴ••**\n`{desc}`"
        foles.append(
            await e.builder.article(
                title=name,
                description=dev,
                thumb=wb(z["icon"], 0, "image/jpeg", []),
                text=text,
                link_preview=True,
                buttons=[
                    [Button.url("Lɪɴᴋ", url=url)],
                    [
                        Button.switch_inline(
                            "Mᴏʀᴇ Aᴘᴘs",
                            query="app ",
                            same_peer=True,
                        ),
                        Button.switch_inline(
                            "Sʜᴀʀᴇ",
                            query=f"app {f}",
                            same_peer=False,
                        ),
                    ],
                ],
            ),
        )
    APP_CACHE.update({f: foles})
    if RECENTS.get(e.sender_id):
        RECENTS[e.sender_id].append(f)
    else:
        RECENTS.update({e.sender_id: [f]})
    await e.answer(foles, switch_pm="Application Searcher.", switch_pm_param="start")
