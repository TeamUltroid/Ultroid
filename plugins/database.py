# Ultroid - UserBot
# Copyright (C) 2021-2022 TeamUltroid
#
# This file is a part of < https://github.com/TeamUltroid/Ultroid/ >
# PLease read the GNU Affero General Public License in
# <https://www.github.com/TeamUltroid/Ultroid/blob/main/LICENSE/>.
"""
✘ Commands Available -

• **DataBase Commands, do not use if you don't know what it is.**

• `{i}setdb key | value`
    Set Value in Database.
    e.g :
    `{i}setdb hi there`
    `{i}setdb hi there | ultroid here`

• `{i}deldb key`
    Delete Key from DB.

• `{i}rendb old keyname | new keyname`
    Update Key Name
"""

import re

from . import Redis, eor, get_string, udB, ultroid_cmd


@ultroid_cmd(pattern="setdb( (.*)|$)", fullsudo=True)
async def _(ult):
    match = ult.pattern_match.group(1).strip()
    if not match:
        return await ult.eor("Provide key and value to set!")
    try:
        delim = " " if re.search("[|]", match) is None else " | "
        data = match.split(delim, maxsplit=1)
        if data[0] in ["--extend", "-e"]:
            data = data[1].split(maxsplit=1)
            data[1] = str(udB.get_key(data[0])) + " " + data[1]
        udB.set_key(data[0], data[1])
        redisdata = Redis(data[0])
        await ult.eor(
            "**DB Key Value Pair Updated\nKey :** `{}`\n**Value :** `{}`".format(
                data[0],
                redisdata,
            ),
        )
    except BaseException:
        await ult.eor(get_string("com_7"))


@ultroid_cmd(pattern="deldb( (.*)|$)", fullsudo=True)
async def _(ult):
    key = ult.pattern_match.group(1).strip()
    if not key:
        return await ult.eor("Give me a key name to delete!", time=5)
    _ = key.split(maxsplit=1)
    try:
        if _[0] == "-m":
            for key in _[1].split():
                k = udB.del_key(key)
            key = _[1]
        else:
            k = udB.del_key(key)
        if k == 0:
            return await ult.eor("`No Such Key.`")
        await ult.eor(f"`Successfully deleted key {key}`")
    except BaseException:
        await ult.eor(get_string("com_7"))


@ultroid_cmd(pattern="rendb( (.*)|$)", fullsudo=True)
async def _(ult):
    match = ult.pattern_match.group(1).strip()
    if not match:
        return await ult.eor("`Provide Keys name to rename..`")
    delim = " " if re.search("[|]", match) is None else " | "
    data = match.split(delim)
    if Redis(data[0]):
        try:
            udB.rename(data[0], data[1])
            await eor(
                ult,
                "**DB Key Rename Successful\nOld Key :** `{}`\n**New Key :** `{}`".format(
                    data[0],
                    data[1],
                ),
            )
        except BaseException:
            await ult.eor(get_string("com_7"))
    else:
        await ult.eor("Key not found")
