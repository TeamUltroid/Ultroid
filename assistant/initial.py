# Ultroid - UserBot
# Copyright (C) 2021 TeamUltroid
#
# This file is a part of < https://github.com/TeamUltroid/Ultroid/ >
# PLease read the GNU Affero General Public License in
# <https://www.github.com/TeamUltroid/Ultroid/blob/main/LICENSE/>.

import re

from . import *

STRINGS = {
    1: """🎇 **Thanks for Deploying Ultroid Userbot!**

• Here, are the Some Basic stuff from, where you can Know, about its Usage.""",
    2: """🎉** About Ultroid**

🧿 Ultroid is Pluggable and powerful Telethon Userbot, made in Python from Scratch. It is Aimed to Increase Security along with Addition of Other Useful Features.

❣ Made by **@TeamUltroid**""",
    3: """**💡• FAQs •**

-> [Setting up TimeZone](https://t.me/UltroidUpdates/22)
-> [About Inline PmPermit](https://t.me/UltroidUpdates/21)
-> [About Dual Mode](https://t.me/UltroidUpdates/18)
-> [Custom Thumbnail](https://t.me/UltroidUpdates/13)
-> [About FullSudo](https://t.me/UltroidUpdates/11)
-> [Setting Up PmBot](https://t.me/UltroidUpdates/2)
-> [Also Check](https://t.me/UltroidUpdates/14)

**• To Know About Updates**
  - Join @TheUltroid.""",
    4: """• `To Know All Available Commands`

  - `{HNDLR}help`
  - `{HNDLR}cmds`""",
    5: """• **For Any Other Query or Suggestion**
  - Move to **@UltroidSupport**.

• Thanks for Reaching till EnD.""",
}

CURRENT = 1


@callback(re.compile("^initft$"))
async def init_depl(e):
    if CURRENT == 4:
        return await e.edit(STRINGS[5], buttons=Button.inline("<< Back", "initbk"))
    CURRENT += 1
    await e.edit(STRINGS[CURRENT])


@callback(re.compile("^initbk$"))
async def ineiq(e):
    if CURRENT == 2:
        return await e.edit(STRINGS[1], buttons=Button.inline("Start Back", "initft"))
    CURRENT -= 1
    await e.edit(STRINGS[CURRENT])
