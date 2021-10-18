# Ultroid - UserBot
# Copyright (C) 2021 TeamUltroid
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

from . import Redis, eor, udB, ultroid_cmd


@ultroid_cmd(pattern="setdb ?(.*)", fullsudo=True)
async def _(ult):
    try:
        delim = " " if re.search("[|]", ult.pattern_match.group(1)) is None else " | "
        data = ult.pattern_match.group(1).split(delim, maxsplit=1)
        udB.set(data[0], data[1])
        redisdata = Redis(data[0])
        await eor(
            ult,
            "DB Key Value Pair Updated\nKey : `{}`\nValue : `{}`".format(
                data[0],
                redisdata,
            ),
        )
    except BaseException:
        await eor(ult, "`Something Went Wrong`")


@ultroid_cmd(pattern="deldb ?(.*)", fullsudo=True)
async def _(ult):
    try:
        key = ult.pattern_match.group(1)
        k = udB.delete(key)
        if k == 0:
            return await eor(ult, "`No Such Key.`")
        await eor(ult, f"`Successfully deleted key {key}`")
    except BaseException:
        await eor(ult, "`Something Went Wrong`")


@ultroid_cmd(pattern="rendb ?(.*)", fullsudo=True)
async def _(ult):
    delim = " " if re.search("[|]", ult.pattern_match.group(1)) is None else " | "
    data = ult.pattern_match.group(1).split(delim)
    if Redis(data[0]):
        try:
            udB.rename(data[0], data[1])
            await eor(
                ult,
                "DB Key Rename Successful\nOld Key : `{}`\nNew Key : `{}`".format(
                    data[0],
                    data[1],
                ),
            )
        except BaseException:
            await eor(ult, "Something went wrong ...")
    else:
        await eor(ult, "Key not found")
