# Ultroid - UserBot
# Copyright (C) 2021 TeamUltroid
#
# This file is a part of < https://github.com/TeamUltroid/Ultroid/ >
# PLease read the GNU Affero General Public License in
# <https://www.github.com/TeamUltroid/Ultroid/blob/main/LICENSE/>.


from . import *


@ultroid_cmd(pattern="kickme", type=["manager"], allow_all=True)
async def doit(e):
    try:
        await e.client.kick_participant(e.chat_id, e.sender_id)
    except Exception as e:
        return await eod(e, str(e))
    await eod(e, "Yes, You are right, get out.")
