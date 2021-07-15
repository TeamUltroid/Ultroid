# Ultroid - UserBot
# Copyright (C) 2021 TeamUltroid
#
# This file is a part of < https://github.com/TeamUltroid/Ultroid/ >
# PLease read the GNU Affero General Public License in
# <https://www.github.com/TeamUltroid/Ultroid/blob/main/LICENSE/>.

from datetime import datetime

from pytz import timezone as tz
from pyUltroid.functions.asst_fns import *
from pyUltroid.misc import owner_and_sudos
from telethon import events
from telethon.utils import get_display_name

from plugins import *

from . import *

Owner_info_msg = f"""
<strong>Owner</strong> - {OWNER_NAME}
<stong>OwnerID</strong> - <code>{OWNER_ID}</code>

<strong>Message Forwards</strong> - {udB.get("PMBOT")}

<stong>Ultroid <a href=https://github.com/TeamUltroid/Ultroid>[v{ultroid_version}]</a>, powered by @TeamUltroid</strong>
"""

_settings = [
    [
        Button.inline("API Kᴇʏs", data="apiset"),
        Button.inline("Pᴍ Bᴏᴛ", data="chatbot"),
    ],
    [
        Button.inline("Aʟɪᴠᴇ", data="alvcstm"),
        Button.inline("PᴍPᴇʀᴍɪᴛ", data="ppmset"),
    ],
    [Button.inline("Fᴇᴀᴛᴜʀᴇs", data="otvars")],
    [Button.inline("VC Sᴏɴɢ Bᴏᴛ", data="vcb")],
    [Button.inline("« Bᴀᴄᴋ", data="mainmenu")],
]

_start = [
    [
        Button.inline("Lᴀɴɢᴜᴀɢᴇ 🌐", data="lang"),
        Button.inline("Sᴇᴛᴛɪɴɢs ⚙️", data="setter"),
    ],
    [
        Button.inline("Sᴛᴀᴛs ✨", data="stat"),
        Button.inline("Bʀᴏᴀᴅᴄᴀsᴛ 📻", data="bcast"),
    ],
    [Button.inline("TɪᴍᴇZᴏɴᴇ 🌎", data="tz")],
]


@callback("ownerinfo")
async def own(event):
    await event.edit(
        Owner_info_msg,
        buttons=[Button.inline("Close", data=f"closeit")],
        link_preview=False,
        parse_mode="html",
    )


@callback("closeit")
async def closet(lol):
    await lol.delete()


@asst_cmd("start ?(.*)")
async def ultroid(event):
    if event.is_group:
        return
    else:
        if (
            not is_added(event.sender_id)
            and str(event.sender_id) not in owner_and_sudos()
        ):
            add_user(event.sender_id)
        if str(event.sender_id) not in owner_and_sudos():
            ok = ""
            u = await event.client.get_entity(event.chat_id)
            if not udB.get("STARTMSG"):
                if udB.get("PMBOT") == "True":
                    ok = "You can contact my master using this bot!!\n\nSend your Message, I will Deliver it To Master."
                await event.reply(
                    f"Hey there [{get_display_name(u)}](tg://user?id={u.id}), this is Ultroid Assistant of [{ultroid_bot.me.first_name}](tg://user?id={ultroid_bot.uid})!\n\n{ok}",
                    buttons=[Button.inline("Info.", data="ownerinfo")],
                )
            else:
                me = f"[{ultroid_bot.me.first_name}](tg://user?id={ultroid_bot.uid})"
                mention = f"[{get_display_name(u)}](tg://user?id={u.id})"
                await event.reply(
                    Redis("STARTMSG").format(me=me, mention=mention),
                    buttons=[Button.inline("Info.", data="ownerinfo")],
                )
        else:
            name = get_display_name(event.sender_id)
            if event.pattern_match.group(1) == "set":
                await event.reply(
                    "Choose from the below options -",
                    buttons=_settings,
                )
            else:
                await event.reply(
                    get_string("ast_3").format(name),
                    buttons=_start,
                )


@callback("mainmenu")
@owner
async def ultroid(event):
    if event.is_group:
        return
    await event.edit(
        get_string("ast_3").format(OWNER_NAME),
        buttons=_start,
    )


@callback("stat")
@owner
async def botstat(event):
    ok = len(get_all_users())
    msg = """Ultroid Assistant - Stats
Total Users - {}""".format(
        ok,
    )
    await event.answer(msg, cache_time=0, alert=True)


@callback("bcast")
@owner
async def bdcast(event):
    ok = get_all_users()
    await event.edit(f"Broadcast to {len(ok)} users.")
    async with event.client.conversation(OWNER_ID) as conv:
        await conv.send_message(
            "Enter your broadcast message.\nUse /cancel to stop the broadcast.",
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
Failed for {fail} user(s).""",
            )


@callback("setter")
@owner
async def setting(event):
    await event.edit(
        "Choose from the below options -",
        buttons=_settings,
    )


@callback("tz")
@owner
async def timezone_(event):
    await event.delete()
    pru = event.sender_id
    var = "TIMEZONE"
    name = "Timezone"
    async with event.client.conversation(pru) as conv:
        await conv.send_message(
            "Send Your TimeZone From This List [Check From Here](http://www.timezoneconverter.com/cgi-bin/findzone.tzc)"
        )
        response = conv.wait_event(events.NewMessage(chats=pru))
        response = await response
        themssg = response.message.message
        if themssg == "/cancel":
            return await conv.send_message(
                "Cancelled!!",
                buttons=get_back_button("mainmenu"),
            )
        else:
            try:
                tz(themssg)
                await setit(event, var, themssg)
                await conv.send_message(
                    f"{name} changed to {themssg}\n",
                    buttons=get_back_button("mainmenu"),
                )
            except BaseException:
                await conv.send_message(
                    "Wrong TimeZone, Try again",
                    buttons=get_back_button("mainmenu"),
                )
