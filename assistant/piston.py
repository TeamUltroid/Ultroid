# Ultroid - UserBot
# Copyright (C) 2021 TeamUltroid
#
# This file is a part of < https://github.com/TeamUltroid/Ultroid/ >
# PLease read the GNU Affero General Public License in
# <https://www.github.com/TeamUltroid/Ultroid/blob/main/LICENSE/>.

from pistonapi import PistonAPI

from . import *


@in_pattern("run")
async def piston_run(event):
    piston = PistonAPI()
    version = None
    try:
        lang = event.text.split()[1]
        code = event.text.split(maxsplit=2)[2]
    except IndexError:
        result = await event.builder.article(
            title="Bad Query",
            description="Usage: [Language] [code]",
            text=f'**Inline Usage**\n\n`@{asst.me.username} run python print("hello world")`\n\n[Language List](https://telegra.ph/Ultroid-09-01-6)',
        )
        return await event.answer([result])
    if lang in piston.languages.keys():
        version = piston.languages[lang]["version"]
    if not version:
        result = await event.builder.article(
            title="Unsupported Language",
            description="Usage: [Language] [code]",
            text=f'**Inline Usage**\n\n`@{asst.me.username} run python print("hello world")`\n\n[Language List](https://telegra.ph/Ultroid-09-01-6)',
        )
        return await event.answer([result])
    output = piston.execute(language=lang, version=version, code=code) or "Success"
    if len(output) > 3000:
        output = output[:3000] + "..."
    result = await event.builder.article(
        title="Result",
        description=output,
        text=f"• **Language:**\n`{lang}`\n\n• **Code:**\n`{code}`\n\n• **Result:**\n`{output}`",
        buttons=Button.switch_inline("Fork", query=event.text, same_peer=True),
    )
    await event.answer([result], switch_pm="• Piston •", switch_pm_param="start")
