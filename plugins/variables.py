# Ultroid - UserBot
# Copyright (C) 2021 TeamUltroid
#
# This file is a part of < https://github.com/TeamUltroid/Ultroid/ >
# PLease read the GNU Affero General Public License in
# <https://www.github.com/TeamUltroid/Ultroid/blob/main/LICENSE/>.

"""
✘ Commands Available -

• `{i}get var <variable name>`
   Get value of the given variable name.

• `{i}get type <variable name>`
   Get variable type.

• `{i}get redis <key>`
   Get redis value of the given key.

• `{i}get keys`
   Get all redis keys.
"""

import os

from . import *


@ultroid_cmd(pattern="get", fullsudo=True)
async def get_var(event):
    if len(event.text) > 4 and " " in event.text[4]:
        opt = event.text.split(" ", maxsplit=2)[1]
    else:
        return
    x = await eor(event, get_string("com_1"))
    if opt != "keys":
        try:
            varname = event.text.split(" ", maxsplit=2)[2]
        except IndexError:
            return await eor(x, "Such a var doesn't exist!", time=5)
    if opt == "var":
        c = 0
        # try redis
        val = udB.get(varname)
        if val is not None:
            c += 1
            await x.edit(
                f"**Variable** - `{varname}`\n**Value**: `{val}`\n**Type**: Redis Key."
            )
        # try env vars
        val = os.getenv(varname)
        if val is not None:
            c += 1
            await x.edit(
                f"**Variable** - `{varname}`\n**Value**: `{val}`\n**Type**: Env Var."
            )

        if c == 0:
            await eor(x, "Such a var doesn't exist!", time=5)

    elif opt == "type":
        c = 0
        # try redis
        val = udB.get(varname)
        if val is not None:
            c += 1
            await x.edit(f"**Variable** - `{varname}`\n**Type**: Redis Key.")
        # try env vars
        val = os.getenv(varname)
        if val is not None:
            c += 1
            await x.edit(f"**Variable** - `{varname}`\n**Type**: Env Var.")

        if c == 0:
            await eor(x, "Such a var doesn't exist!", time=5)

    elif opt == "redis":
        val = udB.get(varname)
        if val is not None:
            await x.edit(f"**Key** - `{varname}`\n**Value**: `{val}`")
        else:
            await eor(x, "No such key!", time=5)

    elif opt == "keys":
        keys = sorted(udB.keys())
        msg = "".join(
            f"• `{i}`" + "\n"
            for i in keys
            if not i.isdigit()
            and not i.startswith("-")
            and not i.startswith("GBAN_REASON_")
        )

        await x.edit(f"**List of Redis Keys :**\n{msg}")
