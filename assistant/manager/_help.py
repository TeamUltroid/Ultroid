# Ultroid - UserBot
# Copyright (C) 2021 TeamUltroid
#
# This file is a part of < https://github.com/TeamUltroid/Ultroid/ >
# PLease read the GNU Affero General Public License in
# <https://www.github.com/TeamUltroid/Ultroid/blob/main/LICENSE/>.

from . import *

START = """
🪅 **Help Menu** 🪅

✘  /start : Check I am Alive or not.
✘  /help : Get This Message.
✘  /repo : Get Bot's Repo..

🧑‍💻 Join **@TheUltroid**
"""

STRINGS = {"admintools": ""}


@ultroid_cmd(pattern="help", type="assistant")
async def helpish(event):
    if not event.is_private:
        url = "https://t.me/" + asst.me.username + "?start=start"
        return await event.reply(
            "Contact me in PM for help!", buttons=Button.url("Click me for Help", url)
        )
    if str(event.sender_id) in owner_and_sudos():
        return
    await event.reply(START)
