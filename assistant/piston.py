from pistonapi import PistonAPI
from pyUltroid.dB.core import *
from telethon import events

from . import *

# By @TechiError


@in_pattern(r"run (.*)")
async def teamultroid(event: events.InlineQuery.Event):
    builder = event.builder
    piston = PistonAPI()
    try:
        omk = event.text.split(" ", maxsplit=1)[1]
    except IndexError:
        return await event.answer(
            [], switch_pm="Enter Code...", switch_pm_param="start"
        )
    if "|" in omk:
        lang, code = omk.split("|")
    else:
        lang = "python 3"
        code = omk
    output = piston.execute(language=lang, code=code)
    outputt = output
    resultm = builder.article(
        title="Code",  # By @TechiError
        description=f"Language-`{lang}` & Code-`{code}`",
        text=f"Language:\n`{lang}`\n\nCode:\n`{code}`\n\nResult:\n`{outputt}`",
    )
    await event.answer([resultm])
