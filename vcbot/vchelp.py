# Ultroid - UserBot
# Copyright (C) 2021 TeamUltroid
#
# This file is a part of < https://github.com/TeamUltroid/Ultroid/ >
# PLease read the GNU Affero General Public License in
# <https://www.github.com/TeamUltroid/Ultroid/blob/main/LICENSE/>.

from . import *

HELP_TEXT = "**View All Vc Commands Here :**\nhttps://telegra.ph/Vc-Commands-07-17-2"


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
