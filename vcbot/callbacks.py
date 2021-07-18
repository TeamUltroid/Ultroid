# Ultroid - UserBot
# Copyright (C) 2021 TeamUltroid
#
# This file is a part of < https://github.com/TeamUltroid/Ultroid/ >
# PLease read the GNU Affero General Public License in
# <https://www.github.com/TeamUltroid/Ultroid/blob/main/LICENSE/>.

from . import *
from .play import queue_func


def AUTH_FILTER(client, query):
    if query.from_user.id not in VC_AUTHS():
        query.answer("You are Not Authorised to Use Me!", show_alert=True)
        return False
    return True


@asst.on_callback_query(filters.regex("^vc(.*)") & AUTH_FILTER)
async def stopvc(_, query):
    match = query.matches[0].group(1).split("_")
    chat = int(match[1])
    if match[0] == "r":
        CallsClient.resume_stream(chat)
        BT = "Pause"
    else:
        CallsClient.pause_stream(chat)
        BT = "Resume"
    await query.answer("Done", show_alert=True)
    dt = BT[0].lower()
    await query.edit_message_reply_markup(
        InlineKeyboardMarkup(
            [[InlineKeyboardButton(BT, callback_data=f"vc{dt}_{chat}")]]
        )
    )


@asst.on_callback_query(filters.regex("^skip_(.*)") & AUTH_FILTER)
async def skipstream(client, query):
    match = query.matches[0].group(1)
    await query.answer("Skipped !", show_alert=True)
    await query.message.delete()
    await queue_func(int(match))


@asst.on_callback_query(filters.regex("^ex_(.*)") & AUTH_FILTER)
async def exit_vc(_, query):
    match = query.matches[0].group(1)
    msg = query.message
    if int(match) not in CallsClient.active_calls.keys():
        return await msg.delete()
    QUEUE.pop(int(match))
    CallsClient.leave_group_call(int(match))
    await query.answer("Exited !")
    await asyncio.sleep(1)
    await msg.delete()
