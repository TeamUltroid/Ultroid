# Ultroid - UserBot
# Copyright (C) 2021 TeamUltroid
#
# This file is a part of < https://github.com/TeamUltroid/Ultroid/ >
# PLease read the GNU Affero General Public License in
# <https://www.github.com/TeamUltroid/Ultroid/blob/main/LICENSE/>.

from . import *

HELP_TEXT = f"""
• **List of All Available Vc Commands :**

  - `/play <search query/youtube link/reply to File>`
  - `/play <channel username/id, where to play><search query/youtube link/reply to File>`
      Plays Music in Voice Call of Specified or Current Chat.

 -  `/radio <M3U8 url/Radio Link/Youtube Live Stream Link>`
      Plays Music Live, Depending on Entered Query.

  - `/playfrom <Channel Username/Id> ; <limit of songs>`
      Takes Music Files from Channel/Chat and Plays it.

  - `/leave` : `Leave Vc of Current/Specified Chat..`

  - `/skip` : `Skip the Song Playing in Chat.`
  - `/pause` : `Pause the Voice Call Songs.`
  - `/resume` : `resume the Paused Song.`

  - `/queue` : `Get List of Songs Added in Queue.`
  - `/listvc` : `Get List of Chats, where Vc is Active.`
  - `/clearqueue` : `Clear All the Songs, added to Queue.`

 `Note` :  `You can Also Use the same Commands from VC Account with Handler` `{HNDLR}`

"""


@asst.on_message(
    filters.command(["vchelp", f"vchelp@{vcusername}"])
    & filters.user(VC_AUTHS())
    & ~filters.edited
    & filters.group
)
async def pass_it(_, message):
    await eor(message, HELP_TEXT)


@Client.on_message(
    filters.command("vchelp", HNDLR)
    & filters.outgoing
    & ~(filters.edited | filters.forwarded)
)
async def always(_, message):
    await eor(message, HELP_TEXT)
