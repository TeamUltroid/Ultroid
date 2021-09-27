# Ultroid - UserBot
# Copyright (C) 2021 TeamUltroid
#
# This file is a part of < https://github.com/TeamUltroid/Ultroid/ >
# PLease read the GNU Affero General Public License in
# <https://www.github.com/TeamUltroid/Ultroid/blob/main/LICENSE/>.
"""
✘ Commands Available -

• `{i}botecho text (optional -\n[button_text_1](https://t.me/TheUltroid)\n[button_text_2](https://t.me/TeamUltroid))`
   Send a message from your assistant bot.
"""

from pyUltroid.functions.tools import create_tl_btn, get_msg_button

from . import *


@ultroid_cmd(pattern="button")
async def butt(event):
    text = event.text.split(maxsplit=1)
    if not len(text) > 1:
        return await eor(
            event,
            f"**Please give some text in correct format.**",
        )
    text, buttons = get_msg_button(text)
    if buttons:
        buttons = create_tl_btn(buttons)
    return await something(event, text, None, btn)
