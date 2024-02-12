# Ultroid - UserBot
# Copyright (C) 2021-2024 TeamUltroid
#
# This file is a part of < https://github.com/TeamUltroid/Ultroid/ >
# PLease read the GNU Affero General Public License in
# <https://www.github.com/TeamUltroid/Ultroid/blob/main/LICENSE/>.

import re

from . import (
    Button,
    ULTConfig,
    callback,
    get_back_button,
    get_languages,
    get_string,
    udB,
)


@callback("lang", owner=True)
async def setlang(event):
    languages = get_languages()
    tultd = [
        Button.inline(
            f"{languages[ult]['natively']} [{ult.lower()}]",
            data=f"set_{ult}",
        )
        for ult in languages
    ]
    buttons = list(zip(tultd[::2], tultd[1::2]))
    if len(tultd) % 2 == 1:
        buttons.append((tultd[-1],))
    buttons.append([Button.inline("« Back", data="mainmenu")])
    await event.edit(get_string("ast_4"), buttons=buttons)


@callback(re.compile(b"set_(.*)"), owner=True)
async def settt(event):
    lang = event.data_match.group(1).decode("UTF-8")
    languages = get_languages()
    ULTConfig.lang = lang
    udB.del_key("language") if lang == "en" else udB.set_key("language", lang)
    await event.edit(
        f"Your language has been set to {languages[lang]['natively']} [{lang}].",
        buttons=get_back_button("lang"),
    )
