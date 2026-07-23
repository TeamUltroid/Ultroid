# Ultroid - UserBot
# Copyright (C) 2021-2026 TeamUltroid
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

-> [Username Tracker](https://t.me/UltroidUpdates/24)
-> [Keeping Custom Addons Repo](https://t.me/UltroidUpdates/28)
-> [Disabling Deploy message](https://t.me/UltroidUpdates/27)
-> [Setting up TimeZone](https://t.me/UltroidUpdates/22)
-> [About Inline PmPermit](https://t.me/UltroidUpdates/21)
-> [About Dual Mode](https://t.me/UltroidUpdates/18)
-> [Custom Thumbnail](https://t.me/UltroidUpdates/13)
-> [About FullSudo](https://t.me/UltroidUpdates/11)
-> [Setting Up PmBot](https://t.me/UltroidUpdates/2)
-> [Also Check](https://t.me/UltroidUpdates/14)

**• To Know About Updates**
  - Join @TeamUltroid.""",
    4: f"""• `To Know All Available Commands`

  - `{HNDLR}help`
  - `{HNDLR}cmds`""",
    5: """• **For Any Other Query or Suggestion**
  - Move to **@UltroidSupportChat**.

• Thanks for Reaching till END.""",
}


def _onboard_text():
    lang = udB.get_key("language") or "en"
    hndlr = udB.get_key("HNDLR") or "."
    pmpermit = "on" if udB.get_key("PMLOG") or udB.get_key("PMREQUEST") else "default"
    addons = "on" if udB.get_key("ADDONS") else "off"
    autojoin = "skipped" if udB.get_key("SKIP_AUTOJOIN") else "allowed"
    return f"""⚙️ **Quick setup**

Current values (tap to toggle / cycle):

• **Language**: `{lang}`
• **Handler (HNDLR)**: `{hndlr}`
• **Addons**: `{addons}`
• **Auto-join @TheUltroid**: `{autojoin}`

Use `{hndlr}setdb KEY value` for advanced keys.
When finished, tap **Done**."""


def _onboard_buttons():
    return [
        [
            Button.inline("Language", "onboard_lang"),
            Button.inline("Handler", "onboard_hndlr"),
        ],
        [
            Button.inline("Toggle Addons", "onboard_addons"),
            Button.inline("Toggle Auto-join", "onboard_join"),
        ],
        [
            Button.inline("PM Permit tip", "onboard_pm"),
            Button.inline("Done ✓", "onboard_done"),
        ],
    ]


@callback(re.compile("initft_(\\d+)"))
async def init_depl(e):
    CURRENT = int(e.data_match.group(1))
    if CURRENT == 5:
        return await e.edit(
            STRINGS[5],
            buttons=[
                Button.inline("<< Back", "initbk_4"),
                Button.inline("⚙️ Quick setup", "onboard_menu"),
            ],
            link_preview=False,
        )

    await e.edit(
        STRINGS[CURRENT],
        buttons=[
            Button.inline("<<", f"initbk_{str(CURRENT - 1)}"),
            Button.inline(">>", f"initft_{str(CURRENT + 1)}"),
        ],
        link_preview=False,
    )


@callback(re.compile("initbk_(\\d+)"))
async def ineiq(e):
    CURRENT = int(e.data_match.group(1))
    if CURRENT == 1:
        return await e.edit(
            STRINGS[1],
            buttons=[
                Button.inline("Start Back >>", "initft_2"),
                Button.inline("⚙️ Quick setup", "onboard_menu"),
            ],
            link_preview=False,
        )

    await e.edit(
        STRINGS[CURRENT],
        buttons=[
            Button.inline("<<", f"initbk_{str(CURRENT - 1)}"),
            Button.inline(">>", f"initft_{str(CURRENT + 1)}"),
        ],
        link_preview=False,
    )


@callback("onboard_menu")
async def onboard_menu(e):
    await e.edit(_onboard_text(), buttons=_onboard_buttons(), link_preview=False)


@callback("onboard_lang")
async def onboard_lang(e):
    # Cycle a small set of common languages present under strings/
    langs = ["en", "hi", "ar", "id", "pt", "es", "ru", "tr"]
    cur = udB.get_key("language") or "en"
    try:
        nxt = langs[(langs.index(cur) + 1) % len(langs)]
    except ValueError:
        nxt = "en"
    udB.set_key("language", nxt)
    await e.answer(f"Language → {nxt}")
    await e.edit(_onboard_text(), buttons=_onboard_buttons(), link_preview=False)


@callback("onboard_hndlr")
async def onboard_hndlr(e):
    options = [".", "!", "/", "?", "$"]
    cur = udB.get_key("HNDLR") or "."
    try:
        nxt = options[(options.index(cur) + 1) % len(options)]
    except ValueError:
        nxt = "."
    udB.set_key("HNDLR", nxt)
    await e.answer(f"HNDLR → {nxt} (restart recommended)")
    await e.edit(_onboard_text(), buttons=_onboard_buttons(), link_preview=False)


@callback("onboard_addons")
async def onboard_addons(e):
    cur = bool(udB.get_key("ADDONS"))
    udB.set_key("ADDONS", not cur)
    await e.answer("Addons " + ("on" if not cur else "off") + " (restart to apply)")
    await e.edit(_onboard_text(), buttons=_onboard_buttons(), link_preview=False)


@callback("onboard_join")
async def onboard_join(e):
    cur = bool(udB.get_key("SKIP_AUTOJOIN"))
    udB.set_key("SKIP_AUTOJOIN", not cur)
    await e.answer("Auto-join " + ("skipped" if not cur else "allowed"))
    await e.edit(_onboard_text(), buttons=_onboard_buttons(), link_preview=False)


@callback("onboard_pm")
async def onboard_pm(e):
    h = udB.get_key("HNDLR") or "."
    await e.answer("See tip in message", alert=False)
    await e.edit(
        f"""🛡 **PM Permit**

Protect your PM with:
• `{h}setdb PMLOG True` — log private messages
• Official plugin: `{h}help pmpermit` (if loaded)

Back to setup when ready.""",
        buttons=[[Button.inline("« Back", "onboard_menu")]],
        link_preview=False,
    )


@callback("onboard_done")
async def onboard_done(e):
    udB.set_key("ONBOARD_DONE", "Done")
    h = udB.get_key("HNDLR") or "."
    await e.edit(
        f"""✅ **Setup saved.**

• Some toggles need a restart (`{h}restart`) to fully apply.
• Help: `{h}help` · Health: `python -m pyUltroid doctor` on the host.""",
        buttons=[[Button.inline("« Intro", "initft_1")]],
        link_preview=False,
    )
