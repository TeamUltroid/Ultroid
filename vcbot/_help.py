from pyUltroid.dB.core import VC_HELP

from . import *


@vc_asst("vchelp")
async def helper(event):
    await eor(
        event, "**VCBot Help Menu**\n\n" + "".join(VC_HELP[i] + "\n" for i in VC_HELP)
    )
