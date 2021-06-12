# Ultroid - UserBot
# Copyright (C) 2021 TeamUltroid
#
# This file is a part of < https://github.com/TeamUltroid/Ultroid/ >
# PLease read the GNU Affero General Public License in
# <https://www.github.com/TeamUltroid/Ultroid/blob/main/LICENSE/>.

"""
✘ Commands Available -

**DataBase Commands, do not use if you don't know what it is.**

• `{i}setredis key | value`
    Redis Set Value.
    e.g :
    `{i}setredis hi there`
    `{i}setredis hi there | ultroid here`

• `{i}delredis key`
    Delete Key from Redis DB

• `{i}renredis old keyname | new keyname`
    Update Key Name
"""

import re

from . import *


@ultroid_cmd(
    pattern="setredis ?(.*)",
)
async def _(ult):
    if not ult.out:
        if not is_fullsudo(ult.sender_id):
            return await eod(ult, "`This Command Is Sudo Restricted.`")
    ok = await eor(ult, "`...`")
    try:
        delim = " " if re.search("[|]", ult.pattern_match.group(1)) is None else " | "
        data = ult.pattern_match.group(1).split(delim, maxsplit=1)
        udB.set(data[0], data[1])
        redisdata = Redis(data[0])
        await ok.edit(
            "Redis Key Value Pair Updated\nKey : `{}`\nValue : `{}`".format(
                data[0],
                redisdata,
            ),
        )
    except BaseException:
        await ok.edit("`Something Went Wrong`")


@ultroid_cmd(
    pattern="delredis ?(.*)",
)
async def _(ult):
    if not ult.out:
        if not is_fullsudo(ult.sender_id):
            return await eod(ult, "`This Command Is Sudo Restricted.`")
    ok = await eor(ult, "`Deleting data from Redis ...`")
    try:
        key = ult.pattern_match.group(1)
        k = udB.delete(key)
        if k == 0:
            return await ok.edit("`No Such Key.`")
        await ok.edit(f"`Successfully deleted key {key}`")
    except BaseException:
        await ok.edit("`Something Went Wrong`")


@ultroid_cmd(
    pattern="renredis ?(.*)",
)
async def _(ult):
    if not ult.out:
        if not is_fullsudo(ult.sender_id):
            return await eod(ult, "`This Command Is Sudo Restricted.`")
    ok = await eor(ult, "`...`")
    delim = " " if re.search("[|]", ult.pattern_match.group(1)) is None else " | "
    data = ult.pattern_match.group(1).split(delim)
    if Redis(data[0]):
        try:
            udB.rename(data[0], data[1])
            await ok.edit(
                "Redis Key Rename Successful\nOld Key : `{}`\nNew Key : `{}`".format(
                    data[0],
                    data[1],
                ),
            )
        except BaseException:
            await ok.edit("Something went wrong ...")
    else:
        await ok.edit("Key not found")
