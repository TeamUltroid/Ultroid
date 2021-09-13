# Ultroid - UserBot
# Copyright (C) 2021 TeamUltroid
#
# This file is a part of < https://github.com/TeamUltroid/Ultroid/ >
# PLease read the GNU Affero General Public License in
# <https://www.github.com/TeamUltroid/Ultroid/blob/main/LICENSE/>.
"""
✘ Commands Available -

•`{i}calc` - Inline Calculator

"""
import re

from . import *

m = [
    "AC",
    "C",
    "⌫",
    "%",
    "7",
    "8",
    "9",
    "+",
    "4",
    "5",
    "6",
    "-",
    "1",
    "2",
    "3",
    "x",
    "00",
    "0",
    ".",
    "÷",
]
tultd = [Button.inline(f"{x}", data=f"calc{x}") for x in m]
lst = list(zip(tultd[::4], tultd[1::4], tultd[2::4], tultd[3::4]))
lst.append([Button.inline("=", data="calc=")])


@ultroid_cmd(pattern="calc")
async def icalc(e):
    udB.delete("calc")
    if e.client._bot:
        return await e.reply("• Ultroid Inline Calculator •", buttons=lst)
    results = await e.client.inline_query(asst.me.username, "calc")
    await results[0].click(e.chat_id, silent=True, hide_via=True)
    await e.delete()


@in_pattern("calc")
@in_owner
async def _(e):
    calc = e.builder.article("Calc", text="• Ultroid Inline Calculator •", buttons=lst)
    await e.answer([calc])


@callback(re.compile("calc(.*)"))
@owner
async def _(e):
    x = (e.data_match.group(1)).decode()
    if x == "AC":
        udB.delete("calc")
        await e.edit(
            "• Ultroid Inline Calculator •",
            buttons=[Button.inline("Open Calculator Again", data="recalc")],
        )
    elif x == "C":
        udB.delete("calc")
        await e.answer("cleared")
    elif x == "⌫":
        get = udB.get("calc")
        if get:
            udB.set("calc", get[:-1])
            await e.answer(str(get[:-1]))
    elif x == "%":
        get = udB.get("calc")
        if get:
            udB.set("calc", get + "/100")
            await e.answer(str(get + "/100"))
    elif x == "÷":
        get = udB.get("calc")
        if get:
            udB.set("calc", get + "/")
            await e.answer(str(get + "/"))
    elif x == "x":
        get = udB.get("calc")
        if get:
            udB.set("calc", get + "*")
            await e.answer(str(get + "*"))
    elif x == "=":
        get = udB.get("calc")
        if get:
            if get.endswith(("*", ".", "/", "-", "+")):
                get = get[:-1]
            out = await calcc(get, e)
            try:
                num = float(out)
                await e.answer(f"Answer : {num}", cache_time=0, alert=True)
            except BaseException:
                udB.delete("calc")
                await e.answer("Error", cache_time=0, alert=True)
        await e.answer("None")
    else:
        get = udB.get("calc")
        if get:
            udB.set("calc", get + x)
            await e.answer(str(get + x))
        udB.set("calc", x)
        await e.answer(str(x))


@callback("recalc")
@owner
async def _(e):
    m = [
        "AC",
        "C",
        "⌫",
        "%",
        "7",
        "8",
        "9",
        "+",
        "4",
        "5",
        "6",
        "-",
        "1",
        "2",
        "3",
        "x",
        "00",
        "0",
        ".",
        "÷",
    ]
    tultd = [Button.inline(f"{x}", data=f"calc{x}") for x in m]
    lst = list(zip(tultd[::4], tultd[1::4], tultd[2::4], tultd[3::4]))
    lst.append([Button.inline("=", data="calc=")])
    await e.edit("Noice Inline Calculator", buttons=lst)
