# Ultroid - UserBot
# Copyright (C) 2021 TeamUltroid
#
# This file is a part of < https://github.com/TeamUltroid/Ultroid/ >
# PLease read the GNU Affero General Public License in
# <https://www.github.com/TeamUltroid/Ultroid/blob/main/LICENSE/>.
"""
✘ Commands Available -

• `{i}akinator`
    `Start Akinator Game`.

"""

import re

import akinator
from telethon.errors import BotMethodInvalidError

from . import Button, asst, callback, get_string, in_pattern, types, ultroid_cmd

games = {}
aki_photo = "https://telegra.ph/file/b0ff07069e8637783fdae.jpg"


@ultroid_cmd(pattern="akinator")
async def doit(e):
    sta = akinator.Akinator()
    games.update({e.chat_id: {e.id: sta}})
    try:
        m = await e.client.inline_query(asst.me.username, f"aki_{e.chat_id}_{e.id}")
        await m[0].click(e.chat_id)
    except BotMethodInvalidError:
        return await asst.send_file(
            e.chat_id,
            aki_photo,
            buttons=Button.inline(get_string("aki_2"), data=f"aki_{e.chat_id}_{e.id}"),
        )
    if e.out:
        await e.delete()


@callback(re.compile("aki_?(.*)"), owner=True)
async def doai(e):
    adt = e.pattern_match.group(1).decode("utf-8")
    dt = adt.split("_")
    ch = int(dt[0])
    mid = int(dt[1])
    await e.edit(get_string("com_1"))
    try:
        qu = games[ch][mid].start_game(child_mode=True)
        # child mode should be promoted
    except KeyError:
        return await e.answer(get_string("aki_1"), alert=True)
    bts = [Button.inline(o, f"aka_{adt}_{o}") for o in ["Yes", "No", "Idk"]]
    cts = [Button.inline(o, f"aka_{adt}_{o}") for o in ["Probably", "Probably Not"]]

    bts = [bts, cts]
    # ignored Back Button since it makes the Pagination looks Bad
    await e.edit("Q. " + qu, buttons=bts)


@callback(re.compile("aka_?(.*)"), owner=True)
async def okah(e):
    mk = e.pattern_match.group(1).decode("utf-8").split("_")
    ch = int(mk[0])
    mid = int(mk[1])
    ans = mk[2]
    try:
        gm = games[ch][mid]
    except KeyError:
        await e.answer(get_string("aki_3"))
        return
    text = gm.answer(ans)
    if gm.progression >= 80:
        gm.win()
        gs = gm.first_guess
        text = "It's " + gs["name"] + "\n " + gs["description"]
        return await e.edit(text, file=gs["absolute_picture_path"])
    bts = [Button.inline(o, f"aka_{ch}_{mid}_{o}") for o in ["Yes", "No", "Idk"]]
    cts = [
        Button.inline(o, f"aka_{ch}_{mid}_{o}") for o in ["Probably", "Probably Not"]
    ]

    bts = [bts, cts]
    await e.edit(text, buttons=bts)


@in_pattern(re.compile("aki_?(.*)"), owner=True)
async def eiagx(e):
    bts = Button.inline(get_string("aki_2"), data=e.text)
    ci = types.InputWebDocument(aki_photo, 0, "image/jpeg", [])
    ans = [
        await e.builder.article(
            "Akinator",
            type="photo",
            content=ci,
            text="Akinator",
            thumb=ci,
            buttons=bts,
            include_media=True,
        )
    ]
    await e.answer(ans)
