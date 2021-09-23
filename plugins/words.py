# Ultroid - UserBot
# Copyright (C) 2021 TeamUltroid
#
# This file is a part of < https://github.com/TeamUltroid/Ultroid/ >
# PLease read the GNU Affero General Public License in
# <https://www.github.com/TeamUltroid/Ultroid/blob/main/LICENSE/>.
"""
✘ Commands Available -

• `{i}meaning <word>`
    Get the meaning of the word.

• `{i}synonym <word>`
    Get all synonyms.

• `{i}antonym <word>`
    Get all antonyms.

• `{i}ud <word>`
    Fetch word defenition from urbandictionary.
"""
import io

import aiohttp
from pyUltroid.functions.tools import async_searcher

from . import eor, ultroid_cmd


@ultroid_cmd(pattern="meaning ?(.*)", type=["official", "manager"])
async def mean(event):
    wrd = event.pattern_match.group(1)
    if not wrd:
        return await eor(event, "`Give a Word to Find Its Meaning..`")
    url = "https://api.dictionaryapi.dev/api/v2/entries/en/" + wrd
    out = await async_searcher(url, re_json=True)
    try:
        return await eor(event, out["title"])
    except (KeyError, TypeError):
        pass
    text = f"**Word :** `{wrd}`\n"
    meni = out[0]["meanings"][0]
    defi = meni["definations"][0]
    text += f"**Meaning :** __{defi['definition']}__\n\n"
    text += f"**Example :** __{defi['definition']['example']}"
    if defi["synonyms"]:
        text += "\n\n**Synonyms :**" + "".join(f" {a}," for a in defi["synonyms"])
    if defi["antonyms"]:
        text += "\n\n**Antonyms :**" + "".join(f" {a}," for a in defi["antonyms"])
    if len(text) > 4096:
        with io.BytesIO(str.encode(text)) as fle:
            fle.name = f"{wrd}-meanings.txt"
            await event.reply(
                file=fle,
                force_document=True,
                caption=f"Meanings of {wrd}",
            )
            await event.delete()
    else:
        await eor(event, text)


@ultroid_cmd(
    pattern="synonym",
)
async def mean(event):
    wrd = event.text.split(" ", maxsplit=1)[1]
    ok = dictionary.synonym(wrd)
    x = get_string("wrd_2").format(wrd)
    try:
        for c, i in enumerate(ok, start=1):
            x += f"**{c}.** `{i}`\n"
        if len(x) > 4096:
            with io.BytesIO(str.encode(x)) as fle:
                fle.name = f"{wrd}-synonyms.txt"
                await event.client.send_file(
                    event.chat_id,
                    fle,
                    force_document=True,
                    allow_cache=False,
                    caption=f"Synonyms of {wrd}",
                    reply_to=event.reply_to_msg_id,
                )
                await event.delete()
        else:
            await event.edit(x)
    except Exception as e:
        await event.edit(f"No synonym found!!\n{e}")


@ultroid_cmd(
    pattern="antonym",
)
async def mean(event):
    evid = event.message.id
    wrd = event.text.split(" ", maxsplit=1)[1]
    ok = dictionary.antonym(wrd)
    x = get_string("wrd_3").format(wrd)
    c = 1
    try:
        for c, i in enumerate(ok, start=1):
            x += f"**{c}.** `{i}`\n"
        if len(x) > 4096:
            with io.BytesIO(str.encode(x)) as fle:
                fle.name = f"{wrd}-antonyms.txt"
                await event.client.send_file(
                    event.chat_id,
                    fle,
                    force_document=True,
                    allow_cache=False,
                    caption=f"Antonyms of {wrd}",
                    reply_to=evid,
                )
                await event.delete()
        else:
            await event.edit(x)
    except Exception as e:
        await event.edit(f"No antonym found!!\n{e}")


@ultroid_cmd(pattern="ud (.*)")
async def _(event):
    word = event.pattern_match.group(1)
    if not word:
        return await eor(event, "`No word given!`")
    async with aiohttp.ClientSession() as ses:
        async with ses.get(
            "http://api.urbandictionary.com/v0/define", params={"term": word}
        ) as out:
            out = await out.json()
    try:
        out = out["list"][0]
    except IndexError:
        return await eor(event, f"**No result found for** `{word}`")
    await eor(
        event,
        f"**Text**: `{out['word']}`\n\n**Meaning**: `{out['definition']}`\n\n**Example**: __{out['example']}__",
    )
