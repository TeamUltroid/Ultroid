# Ultroid - UserBot
# Copyright (C) 2021 TeamUltroid
#
# This file is a part of < https://github.com/TeamUltroid/Ultroid/ >
# PLease read the GNU Affero General Public License in
# <https://www.github.com/TeamUltroid/Ultroid/blob/main/LICENSE/>.

from pyUltroid.dB.core import VC_HELP
from telethon import Button
from . import *


@vc_asst("vchelp")
async def helper(event):
    await event.reply(
        "**VCBot Help Menu**\n\n", buttons=Button.inline("Voice Chat Help", data="vc_helper")
    )
