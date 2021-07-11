# Ultroid - UserBot
# Copyright (C) 2021 TeamUltroid
#
# This file is a part of < https://github.com/TeamUltroid/Ultroid/ >
# PLease read the GNU Affero General Public License in
# <https://www.github.com/TeamUltroid/Ultroid/blob/main/LICENSE/>.

from . import *


@asst.on_callback_query(filters.regex("^vc(.*)"))
async def stopvc(_, query):
    if query.from_user.id not in VC_AUTHS():
        return await query.answer("You are Not Authorised to Use Me!", show_alert=True)
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
