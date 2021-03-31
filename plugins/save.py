# Ultroid - UserBot
# Copyright (C) 2020 TeamUltroid
#
# This file is a part of < https://github.com/TeamUltroid/Ultroid/ >
# PLease read the GNU Affero General Public License in
# <https://www.github.com/TeamUltroid/Ultroid/blob/main/LICENSE/>.

"""
✘ Commands Available -

• `{i}save <reply message>`
    Save that replied msg to ur saved messages box.

"""
from . import *

@ultroid_cmd(pattern="save")
async def saf(e):
     x = await e.get_reply_message()
     if not x:
         return await eod(e, "Reply to Any Message to save it to ur saved messages", time=5)
     await e.forward_to("me")
     await eod(e, "Message saved at saved messages", time=5)


HELP.update({f"{__name__.split('.')[1]}": f"{__doc__.format(i=HNDLR)}"})
