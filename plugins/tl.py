import inspect

from telethon.tl.alltlobjects import LAYER, tlobjects

from core.decorators._assistant import asst, in_pattern


@in_pattern("tl", owner=True)
async def inline_tl(ult):
    try:
        match = ult.text.split(maxsplit=1)[1]
    except IndexError:
        text = f"**Telegram TlObjects Searcher.**\n__(Don't use if you don't know what it is!)__\n\n• Example Usage\n`@{asst.me.username} tl GetFullUserRequest`"
        return await ult.answer(
            [
                await ult.builder.article(
                    title="How to Use?",
                    description="Tl Searcher by Ultroid",
                    url="https://t.me/TeamUltroid",
                    text=text,
                )
            ],
            switch_pm="Tl Search 🔍",
            switch_pm_param="start",
        )
    res = []
    for key in tlobjects.values():
        if match.lower() in key.__name__.lower():
            tyyp = "Function" if "tl.functions." in str(key) else "Type"
            text = f"**Name:** `{key.__name__}`\n"
            text += f"**Category:** `{tyyp}`\n"
            text += f"\n`from {key.__module__} import {key.__name__}`\n\n"
            if args := str(inspect.signature(key))[1:][:-1]:
                text += "**Parameter:**\n"
                for para in args.split(","):
                    text += " " * 4 + "`" + para + "`\n"
            text += f"\n**Layer:** `{LAYER}`"
            res.append(
                await ult.builder.article(
                    title=key.__name__,
                    description=tyyp,
                    url="https://t.me/TeamUltroid",
                    text=text[:4000],
                )
            )
    mo = f"Showing {len(res)} results!" if res else f"No Results for {match}!"
    await ult.answer(res[:50], switch_pm=mo, switch_pm_param="start")
