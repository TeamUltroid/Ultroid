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
import asyncurban
from PyDictionary import PyDictionary

from . import *

dictionary = PyDictionary()


@ultroid_cmd(pattern="meaning", type=["official", "manager"], ignore_dualmode=True)
async def mean(event):
    event.message.id
    xx = await eor(event, get_string("com_1"))
    wrd = event.text.split(" ", maxsplit=1)[1]
    ok = dictionary.meaning(wrd)
    try:
        p = ok["Noun"]
    except BaseException:
        return await xx.edit("Oops! No such word found!!")
    x = get_string("wrd_1").format(wrd)
    c = 1
    for i in p:
        x += f"**{c}.** `{i}`\n"
        c += 1
    if len(x) > 4096:
        with io.BytesIO(str.encode(x)) as fle:
            fle.name = f"{wrd}-meanings.txt"
            await event.reply(
                file=out_file,
                force_document=True,
                caption=f"Meanings of {wrd}",
            )
            await xx.delete()
    else:
        await xx.edit(x)


@ultroid_cmd(
    pattern="synonym",
)
async def mean(event):
    evid = event.message.id
    xx = await eor(event, get_string("com_1"))
    wrd = event.text.split(" ", maxsplit=1)[1]
    ok = dictionary.synonym(wrd)
    x = get_string("wrd_2").format(wrd)
    c = 1
    try:
        for i in ok:
            x += f"**{c}.** `{i}`\n"
            c += 1
        if len(x) > 4096:
            with io.BytesIO(str.encode(x)) as fle:
                fle.name = f"{wrd}-synonyms.txt"
                await event.client.send_file(
                    event.chat_id,
                    out_file,
                    force_document=True,
                    allow_cache=False,
                    caption=f"Synonyms of {wrd}",
                    reply_to=evid,
                )
                await xx.delete()
        else:
            await xx.edit(x)
    except Exception as e:
        await xx.edit(f"No synonym found!!\n{str(e)}")


@ultroid_cmd(
    pattern="antonym",
)
async def mean(event):
    evid = event.message.id
    xx = await eor(event, get_string("com_1"))
    wrd = event.text.split(" ", maxsplit=1)[1]
    ok = dictionary.antonym(wrd)
    x = get_string("wrd_3").format(wrd)
    c = 1
    try:
        for i in ok:
            x += f"**{c}.** `{i}`\n"
            c += 1
        if len(x) > 4096:
            with io.BytesIO(str.encode(x)) as fle:
                fle.name = f"{wrd}-antonyms.txt"
                await event.client.send_file(
                    event.chat_id,
                    out_file,
                    force_document=True,
                    allow_cache=False,
                    caption=f"Antonyms of {wrd}",
                    reply_to=evid,
                )
                await xx.delete()
        else:
            await xx.edit(x)
    except Exception as e:
        await xx.edit(f"No antonym found!!\n{str(e)}")


@ultroid_cmd(pattern="ud (.*)")
async def _(event):
    xx = await eor(event, get_string("com_1"))
    word = event.pattern_match.group(1)
    if word is None:
        return await xx.edit("`No word given!`")
    urban = asyncurban.UrbanDictionary()
    try:
        mean = await urban.get_word(word)
        await xx.edit(
            f"**Text**: `{mean.word}`\n\n**Meaning**: `{mean.definition}`\n\n**Example**: __{mean.example}__",
        )
    except asyncurban.WordNotFoundError:
        await xx.edit(f"**No result found for** `{word}`")
