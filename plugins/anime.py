# Ultroid - UserBot
# Copyright (C) 2021-2023 TeamUltroid
#
# This file is a part of < https://github.com/TeamUltroid/Ultroid/ >
# PLease read the GNU Affero General Public License in
# <https://www.github.com/TeamUltroid/Ultroid/blob/main/LICENSE/>.

"""
✘ Commands Available -

• `{i}character <character name>`
   Fetch anime character details.
"""

import jikanpy

from . import *


@ultroid_cmd(pattern="character ?(.*)")
async def anime_char_search(event):
    xx = await event.eor(get_string("com_1"))
    char_name = event.pattern_match.group(1)
    if not char_name:
        await eod(xx, "`Enter the name of a character too please!`", time=5)
    jikan = jikanpy.jikan.Jikan()
    try:
        s = jikan.search("character", char_name)
    except jikanpy.exceptions.APIException:
        return await eod(xx, "`Couldn't find character!`", time=5)
    a = s["results"][0]["mal_id"]
    char_json = jikan.character(a)
    pic = char_json["image_url"]
    msg = f"**[{char_json['name']}]({char_json['url']})**"
    if char_json["name_kanji"] != "Japanese":
        msg += f" [{char_json['name_kanji']}]\n"
    else:
        msg += "\n"
    if char_json["nicknames"]:
        nicknames_string = ", ".join(char_json["nicknames"])
        msg += f"\n**Nicknames** : `{nicknames_string}`\n"
    about = char_json["about"].split("\n", 1)[0].strip().replace("\n", "")
    msg += f"\n**About**: __{about}__"
    await event.reply(msg, file=pic, force_document=False)
    await xx.delete()
