# Ultroid - UserBot
# Copyright (C) 2020 TeamUltroid
#
# This file is a part of < https://github.com/TeamUltroid/Ultroid/ >
# PLease read the GNU Affero General Public License in
# <https://www.github.com/TeamUltroid/Ultroid/blob/main/LICENSE/>.

"""
✘ Commands Available -

"""

import re
from . import *

@in_pattern("calc")
@in_owner
async def _(e):
    m = ["AC","C", "⌫", "%", "7", "8", "9", "+", "4", "5", "6", "-", "1","2","3","x","00","0",".","÷"]
    tultd = [Button.inline(f"{x}", data=f"calc{x}") for x in m]
    lst = list(zip(tultd [::4], tultd[1::4], tultd [2::4], tultd[3::4]))
    lst.append([Button.inline("=", data="calc=")])
    calc = e.builder.article("Calc", text="Noice Inline Calculator", buttons=lst)
    await e.answer([calc])

@callback(re.compile("calc(.*)"))
@owner
async def _(e):
    x = (e.data_match.group(1)).decode()
    if x=="AC":
        udB.delete("calc")
        return await e.edit("Noice Inline Calculator", buttons=[Button.inline("Open Calculator Again",data="recalc")])
    elif x=="C":
        udB.delete("calc")
        return await e.answer("cleared", cache_time=0, alert=True)
    elif x=="⌫":
        get = udB.get("calc")
        if get:
            return udB.set("calc", get[:-1])
    elif x=="%":
        get = udB.get("calc")
        if get:
            return udB.set("calc", get + "/100")
    elif x=="÷":
        get = udB.get("calc")
        if get:
            return udB.set("calc", get + "/")
    elif x=="x":
        get = udB.get("calc")
        if get:
            return udB.set("calc", get + "*")
        return
    elif x=="=":
        get = udB.get("calc")
        if get:
            if get.endswith(("*",".","/","-","+")):
                get = get[:-1]
            out = await calcc(get, e)
            try:
                num = int(out)
                return await e.answer(f"Answer : {num}", cache_time=0, alert=True)
            except BaseException:
                udB.delete('calc')
                return await e.answer("None", cache_time=0, alert=True)
        return await e.answer("None", cache_time=0, alert=True)
    else:
        get = udB.get("calc")
        if get:
            return udB.set("calc", get + x)
        return udB.set("calc", x)
        
@callback("recalc")
@owner
async def _(e):
    m = ["AC","C", "⌫", "%", "7", "8", "9", "+", "4", "5", "6", "-", "1","2","3","x","00","0",".","÷"]
    tultd = [Button.inline(f"{x}", data=f"calc{x}") for x in m]
    lst = list(zip(tultd [::4], tultd[1::4], tultd [2::4], tultd[3::4]))
    lst.append([Button.inline("=", data="calc=")])
    await e.edit("Noice Inline Calculator", buttons=lst)
    


HELP.update({f"{__name__.split('.')[1]}": f"{__doc__.format(i=HNDLR)}"})

