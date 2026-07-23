# Ultroid - UserBot
# Copyright (C) 2021-2026 TeamUltroid
#
# This file is a part of < https://github.com/TeamUltroid/Ultroid/ >
# PLease read the GNU Affero General Public License in
# <https://www.github.com/TeamUltroid/Ultroid/blob/main/LICENSE/>.


from . import get_help

__doc__ = get_help("help_database")


import re

from pyUltroid.startup.settings_schema import (
    KNOWN_KEYS,
    coerce_value,
    format_keys_help,
)

from . import Redis, eor, get_string, udB, ultroid_cmd


@ultroid_cmd(pattern="setdb( (.*)|$)", fullsudo=True)
async def _(ult):
    match = ult.pattern_match.group(1).strip()
    if not match:
        return await ult.eor("Provide key and value to set!\nTip: `.keys` lists known keys.")
    try:
        delim = " " if re.search("[|]", match) is None else " | "
        data = match.split(delim, maxsplit=1)
        if data[0] in ["--extend", "-e"]:
            data = data[1].split(maxsplit=1)
            data[1] = f"{str(udB.get_key(data[0]))} {data[1]}"
        if len(data) < 2:
            return await ult.eor("Provide both key and value.")
        key, raw = data[0], data[1]
        try:
            value, warn = coerce_value(key, raw)
        except ValueError as er:
            meta = KNOWN_KEYS.get(key)
            hint = f" ({meta[0]}: {meta[2]})" if meta else ""
            return await ult.eor(f"**Invalid value for** `{key}`{hint}\n`{er}`")
        udB.set_key(key, value)
        msg = (
            f"**DB Key Value Pair Updated\nKey :** `{key}`\n**Value :** `{value!r}`"
        )
        if warn:
            msg += f"\n\n⚠️ {warn}"
        await ult.eor(msg)

    except BaseException:
        await ult.eor(get_string("com_7"))


@ultroid_cmd(pattern="keys( (.*)|$)", fullsudo=True)
async def keys_cmd(ult):
    filt = ult.pattern_match.group(1).strip() or None
    text = format_keys_help(filt)
    if len(text) > 3900:
        text = text[:3900] + "\n…"
    await ult.eor(text)


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
                f"**DB Key Rename Successful\nOld Key :** `{data[0]}`\n**New Key :** `{data[1]}`",
            )

        except BaseException:
            await ult.eor(get_string("com_7"))
    else:
        await ult.eor("Key not found")
