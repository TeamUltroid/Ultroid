# Ultroid - UserBot
# Copyright (C) 2021 TeamUltroid
#
# This file is a part of < https://github.com/TeamUltroid/Ultroid/ >
# PLease read the GNU Affero General Public License in
# <https://www.github.com/TeamUltroid/Ultroid/blob/main/LICENSE/>.

from pistonapi import PistonAPI
from telethon import events

from . import *

# By @TechiError


@in_pattern(r"run")
async def teamultroid(event: events.InlineQuery.Event):
    builder = event.builder
    piston = PistonAPI()
    version = None
    try:
        omk = event.text.split(" ", maxsplit=1)[1]
    except IndexError:
        return await event.answer(
            [], switch_pm="Enter Code...", switch_pm_param="start"
        )
    if " | " in omk:
        lang, code = omk.split(" | ")
    else:
        lang = "python 3"
        code = omk
    if lang in piston.languages.keys():
        version = piston.languages[lang]["version"]
    if not version:
        return await event.answer(
            [], switch_pm="Unsupported Language!", switch_pm_param="start"
        )
    output = piston.execute(language=lang, version=version, code=code) or "Success"
    result = await builder.article(
        title="∆ Execute ∆",  # By @TechiError
        description=f"Language-`{lang}`",
        text=f"**Language:**\n`{lang}`\n\n**Code:**\n`{code}`\n\n**Result:**\n`{output}`",
        buttons=Button.switch_inline("Use Again..", query=omk, same_peer=True)
    )
    await event.answer([result], switch_pm="• Piston •", switch_pm_param="start")
