# Ultroid - UserBot
# Copyright (C) 2021-2026 TeamUltroid
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
    languages = get_languages() or {}
    lang_buttons = [
        Button.inline(
            f"{info['natively']} [{code.lower()}]",
            data=f"set_{code}",
        )
        for code, info in languages.items()
    ]
    
    buttons = [
        lang_buttons[i : i + 2]
        for i in range(0, len(lang_buttons), 2)
    ]
    buttons.append([Button.inline("« Bᴀᴄᴋ Mᴇɴᴜ", data="mainmenu")])
    
    await event.edit(get_string("ast_4"), buttons=buttons)


@callback(re.compile(b"set_(.*)"), owner=True)
async def settt(event):
    lang = event.data_match.group(1).decode("utf-8")
    languages = get_languages() or {}
    native_name = languages.get(lang, {}).get("natively", lang)
    
    ULTConfig.lang = lang
    if lang == "en":
        udB.del_key("language")
    else:
        udB.set_key("language", lang)

    text = (
        "🌐 **Lᴀɴɢᴜᴀɢᴇ Sᴜᴄᴄᴇssғᴜʟʟʏ Sᴇᴛ!**\n\n"
        f"• **Sᴇʟᴇᴄᴛᴇᴅ Lᴀɴɢᴜᴀɢᴇ:** `{native_name}` `[{lang.upper()}]`"
    )
    
    await event.edit(
        text,
        buttons=get_back_button("lang"),
    )
