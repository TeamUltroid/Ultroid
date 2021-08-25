# Ultroid - UserBot
# Copyright (C) 2021 TeamUltroid
#
# This file is a part of < https://github.com/TeamUltroid/Ultroid/ >
# PLease read the GNU Affero General Public License in
# <https://www.github.com/TeamUltroid/Ultroid/blob/main/LICENSE/>.

from pyUltroid.dB.core import VC_HELP

from . import *


@vc_asst("vchelp")
async def helper(event):
    await eor(
        event, "**VCBot Help Menu**\n\n" + "".join(VC_HELP[i] + "\n" for i in VC_HELP)
    )
