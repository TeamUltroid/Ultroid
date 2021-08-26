from pistonapi import PistonAPI
from pyUltroid.dB.core import *
from telethon import events

# By @TechiError


@tgbot.on(events.InlineQuery(pattern=r"run (.*)"))
async def teamultroid(event: events.InlineQuery.Event):
    builder = event.builder
    bot = await tgbot.get_me()
    bot.username
    piston = PistonAPI()
    if event.query.user_id in sed:

        omk = event.text.split(" ", maxsplit=1)[1]
        if omk is not None:
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
    else:
        return  # By @TechiError
