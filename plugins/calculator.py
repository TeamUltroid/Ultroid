# Ultroid - UserBot
# Copyright (C) 2021-2024 TeamUltroid
#
# This file is a part of < https://github.com/TeamUltroid/Ultroid/ >
# PLease read the GNU Affero General Public License in
# <https://www.github.com/TeamUltroid/Ultroid/blob/main/LICENSE/>.


from . import get_help

__doc__ = get_help("help_calculator")

import re

from . import Button, asst, callback, get_string, in_pattern, udB, ultroid_cmd

CALC = {}

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
    udB.del_key("calc")
    if e.client._bot:
        return await e.reply(get_string("calc_1"), buttons=lst)
    results = await e.client.inline_query(asst.me.username, "calc")
    await results[0].click(e.chat_id, silent=True, hide_via=True)
    await e.delete()


@in_pattern("calc", owner=True)
async def _(e):
    calc = e.builder.article("Calc", text=get_string("calc_1"), buttons=lst)
    await e.answer([calc])


@callback(re.compile("calc(.*)"), owner=True)
async def _(e):
    x = (e.data_match.group(1)).decode()
    user = e.query.user_id
    get = None
    if x == "AC":
        if CALC.get(user):
            CALC.pop(user)
        await e.edit(
            get_string("calc_1"),
            buttons=[Button.inline(get_string("calc_2"), data="recalc")],
        )
    elif x == "C":
        if CALC.get(user):
            CALC.pop(user)
        await e.answer("cleared")
    elif x == "⌫":
        if CALC.get(user):
            get = CALC[user]
        if get:
            CALC.update({user: get[:-1]})
            await e.answer(str(get[:-1]))
    elif x == "%":
        if CALC.get(user):
            get = CALC[user]
        if get:
            CALC.update({user: f"{get}/100"})
            await e.answer(str(f"{get}/100"))
    elif x == "÷":
        if CALC.get(user):
            get = CALC[user]
        if get:
            CALC.update({user: f"{get}/"})
            await e.answer(str(f"{get}/"))
    elif x == "x":
        if CALC.get(user):
            get = CALC[user]
        if get:
            CALC.update({user: f"{get}*"})
            await e.answer(str(f"{get}*"))
    elif x == "=":
        if CALC.get(user):
            get = CALC[user]
        if get:
            if get.endswith(("*", ".", "/", "-", "+")):
                get = get[:-1]
            out = eval(get)
            try:
                num = float(out)
                await e.answer(f"Answer : {num}", cache_time=0, alert=True)
            except BaseException:
                CALC.pop(user)
                await e.answer(get_string("sf_8"), cache_time=0, alert=True)
        await e.answer("None")
    else:
        if CALC.get(user):
            get = CALC[user]
        if get:
            CALC.update({user: get + x})
            return await e.answer(str(get + x))
        CALC.update({user: x})
        await e.answer(str(x))


@callback("recalc", owner=True)
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
    await e.edit(get_string("calc_1"), buttons=lst)
