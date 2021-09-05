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

ADMINTOOLS = """✘ **AdminTools** ✘

• /pin : Pins the Replied Message
• /pinned : Get Pinned message in chat.
• /unpin : Unpin the Replied message
• /unpin all : Unpin all Pinned Messages.

• /ban (username/id/reply) : Ban the User
• /unban (username/id/reply) : UnBan the User.

• /mute (username/id/reply) : Mute the User.
• /unmute (username/id/reply) : Unmute the User.

• /tban (username/id/reply) (time) : Temporary ban a user
• /tmute (username/id/reply) (time) : temporary Mutes a User.

• /purge (purge messages)"""

STRINGS = {"Admintools": ADMINTOOLS}


@asst_cmd("help")
async def helpish(event):
    if not event.is_private:
        url = "https://t.me/" + asst.me.username + "?start=start"
        return await event.reply(
            "Contact me in PM for help!", buttons=Button.url("Click me for Help", url)
        )
    if str(event.sender_id) in owner_and_sudos():
        return
    BTTS = []
    keys = STRINGS
    count = 0
    while count != len(list(keys)):
        BT = []
        for i in list(keys)[:2]:
            count += 1
            BT.append(Button.inline(i, "hlp_" + i))
            del keys[i]
        BTTS.append(BT)
    await event.reply(START, buttons=BTTS)
