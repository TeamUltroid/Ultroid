# Ultroid - UserBot
# Copyright (C) 2020 TeamUltroid
#
# This file is a part of < https://github.com/TeamUltroid/Ultroid/ >
# PLease read the GNU Affero General Public License in
# <https://www.github.com/TeamUltroid/Ultroid/blob/main/LICENSE/>.

from datetime import datetime

from pyUltroid.functions.asst_fns import *
from telethon import Button, custom, events

from plugins import *

from . import *


@asst_cmd("start")
async def assistant(event):
    if event.is_group and event.sender_id in sed:
        return await eor(event, "`I dont work in groups`")
    else:
        if not is_added(event.sender_id) and event.sender_id not in sed:
            add_user(event.sender_id)
            await asst.send_message(
                OWNER_ID,
                f"Bot started by [{event.sender_id}](tg://user?id={event.sender_id})",
            )
        ok = ""
        if udB.get("MSG_FRWD") == True:
            ok = "You can contact me using this bot!!"
        if event.is_private and event.sender_id in sed:
            return
        await event.reply(
            f"Hey there, this is Ultroid Assistant of {OWNER_NAME}!\n\n{ok}",
            buttons=[Button.url("Know More", url="https://t.me/TeamUltroid")],
        )


@asst_cmd("start")
@owner
async def ultroid(event):
    if event.is_group:
        return
    await asst.send_message(
        event.chat_id,
        get_string("ast_3").format(OWNER_NAME),
        buttons=[
            [Button.inline("Language 🌐", data="lang"),
            Button.inline("Sᴇᴛᴛɪɴɢs ⚙️", data="setter")],
            [Button.inline("Sᴛᴀᴛs ✨", data="stat"),
            Button.inline("Bʀᴏᴀᴅᴄᴀsᴛ 📻", data="bcast")],
        ],
    )


# aah, repeat the codes..
@callback("mainmenu")
@owner
async def ultroid(event):
    if event.is_group:
        return
    await event.edit(
        get_string("ast_3").format(OWNER_NAME),
        buttons=[
            [Button.inline("Language 🌐", data="lang"),
            Button.inline("Sᴇᴛᴛɪɴɢs ⚙️", data="setter")],
            [Button.inline("Sᴛᴀᴛs ✨", data="stat"),
            Button.inline("Bʀᴏᴀᴅᴄᴀsᴛ 📻", data="bcast")],
        ],
    )


@callback("stat")
@owner
async def botstat(event):
    ok = len(get_all_users())
    msg = """Ultroid Assistant - Stats
Total Users - {}""".format(
        ok
    )
    await event.answer(msg, cache_time=0, alert=True)


@callback("bcast")
@owner
async def bdcast(event):
    ok = get_all_users()
    await event.edit(f"Broadcast to {len(ok)} users.")
    async with event.client.conversation(OWNER_ID) as conv:
        await conv.send_message(
            "Enter your broadcast message.\nUse /cancel to stop the broadcast."
        )
        response = conv.wait_event(events.NewMessage(chats=OWNER_ID))
        response = await response
        themssg = response.message.message
        if themssg == "/cancel":
            return await conv.send_message("Cancelled!!")
        else:
            success = 0
            fail = 0
            await conv.send_message(f"Starting a broadcast to {len(ok)} users...")
            start = datetime.now()
            for i in ok:
                try:
                    await asst.send_message(int(i), f"{themssg}")
                    success += 1
                except BaseException:
                    fail += 1
            end = datetime.now()
            time_taken = (end - start).seconds
            await conv.send_message(
                f"""
Broadcast completed in {time_taken} seconds.
Total Users in Bot - {len(ok)}
Sent to {success} users.
Failed for {fail} user(s)."""
            )


@callback("setter")
@owner
async def setting(event):
    await event.edit(
        "Choose from the below options -",
        buttons=[
            [Button.inline("API Kᴇʏs", data="apiset")],
            [
                Button.inline("Aʟɪᴠᴇ", data="alvcstm"),
                Button.inline("PᴍPᴇʀᴍɪᴛ", data="pmset"),
            ],
            [Button.inline("Fᴇᴀᴛᴜʀᴇs", data="otvars")],
            [Button.inline("« Bᴀᴄᴋ", data="mainmenu")],
        ],
    )


#@callback("lang")
#@owner
#async def lang(e):
    
