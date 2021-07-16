# Ultroid - UserBot
# Copyright (C) 2021 TeamUltroid
#
# This file is a part of < https://github.com/TeamUltroid/Ultroid/ >
# PLease read the GNU Affero General Public License in
# <https://www.github.com/TeamUltroid/Ultroid/blob/main/LICENSE/>.

from . import *


@asst.on_message(filters.command("skipvc") & filters.user(VC_AUTHS()) & ~filters.edited)
async def skiplife(_, message):
    mst = message.text.split(" ", maxsplit=1)
    try:
        chat = (await Client.get_chat(mst[1])).id
    except BaseException:
        chat = message.chat.id
    try:
        song, title, from_user, pos, dur = get_from_queue(chat)
        CallsClient.change_stream(chat, song)
        ok = await asst.send_message(
            chat, f"**Playing :** {title}\n**Requested by**: {from_user}"
        )
        QUEUE[chat].pop(pos)
        if not QUEUE[chat]:
            QUEUE.pop(chat)
        await asyncio.sleep(dur)
        await ok.delete()
    except IndexError:
        CallsClient.leave_group_call(chat)
    except Exception as Ex:
        await asst.send_message(LOG_CHANNEL, "Vc Error\n\n" + str(Ex))
