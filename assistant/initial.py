# Ultroid - UserBot
# Copyright (C) 2021-2026 TeamUltroid
#
# This file is a part of < https://github.com/TeamUltroid/Ultroid/ >
# PLease read the GNU Affero General Public License in
# <https://www.github.com/TeamUltroid/Ultroid/blob/main/LICENSE/>.

import re

from . import *

STRINGS = {
    1: """🎆 **Tʜᴀɴᴋs ғᴏʀ Dᴇᴘʟᴏʏɪɴɢ Uʟᴛʀᴏɪᴅ U sᴇʀʙᴏᴛ!**

• Welcome aboard! Here is a quick guide to help you get started with the basics.""",
    2: """🎉 **Aʙᴏᴜᴛ Uʟᴛʀᴏɪᴅ**

🧿 **Ultroid** is a pluggable, feature-rich, and high-performance Telethon Userbot written in Python from scratch. Designed with maximum security and efficiency in mind.

❤️ **Dᴇᴠᴇʟᴏᴘᴇᴅ ʙʏ @TeamUltroid**""",
    3: """💡 **Fʀᴇǫᴜᴇɴᴛʟʏ Asᴋᴇᴅ Qᴜᴇsᴛɪᴏɴs (FAQs)**

📌 [Username Tracker](https://t.me/UltroidUpdates/24)
📌 [Keeping Custom Addons Repo](https://t.me/UltroidUpdates/28)
📌 [Disabling Deploy Message](https://t.me/UltroidUpdates/27)
📌 [Setting Up TimeZone](https://t.me/UltroidUpdates/22)
📌 [About Inline PM Permit](https://t.me/UltroidUpdates/21)
📌 [About Dual Mode](https://t.me/UltroidUpdates/18)
📌 [Custom Thumbnail Guide](https://t.me/UltroidUpdates/13)
📌 [About FullSudo Permissions](https://t.me/UltroidUpdates/11)
📌 [Setting Up PM Bot](https://t.me/UltroidUpdates/2)
📌 [Additional Useful Info](https://t.me/UltroidUpdates/14)

📢 **Sᴛᴀʏ Uᴘᴅᴀᴛᴇᴅ:** Join **@TeamUltroid** for news!""",
    4: f"""📜 **Aᴠᴀɪʟᴀʙʟᴇ Cᴏᴍᴍᴀɴᴅs**

To explore all available commands and features, run:
• `{HNDLR}help` — Interactive help menu
• `{HNDLR}cmds` — Complete command list""",
    5: """💬 **Sᴜᴘᴘᴏʀᴛ & Cᴏᴍᴍᴜɴɪᴛʏ**

• **Hᴀᴠᴇ ǫᴜᴇsᴛɪᴏɴs ᴏʀ sᴜɢɢᴇsᴛɪᴏɴs?**
  Feel free to join our support group: **@UltroidSupportChat**

✨ *Thank you for reaching the end! Enjoy using Ultroid.*""",
}


@callback(re.compile(r"initft_(\d+)"))
async def init_depl(e):
    current = int(e.data_match.group(1))
    text = STRINGS.get(current, STRINGS[5])

    if current >= 5:
        buttons = [Button.inline("« Bᴀᴄᴋ", "initbk_4")]
    else:
        buttons = [
            [
                Button.inline("« Bᴀᴄᴋ", f"initbk_{current - 1}"),
                Button.inline("Nᴇxᴛ »", f"initft_{current + 1}"),
            ]
        ]

    await e.edit(text, buttons=buttons, link_preview=False)


@callback(re.compile(r"initbk_(\d+)"))
async def ineiq(e):
    current = int(e.data_match.group(1))
    text = STRINGS.get(current, STRINGS[1])

    if current <= 1:
        buttons = [Button.inline("Sᴛᴀʀᴛ Tᴏᴜʀ »", "initft_2")]
    else:
        buttons = [
            [
                Button.inline("« Bᴀᴄᴋ", f"initbk_{current - 1}"),
                Button.inline("Nᴇxᴛ »", f"initft_{current + 1}"),
            ]
        ]

    await e.edit(text, buttons=buttons, link_preview=False)
