# Ultroid - UserBot
# Copyright (C) 2021-2026 TeamUltroid
#
# This file is a part of < https://github.com/TeamUltroid/Ultroid/ >
# Please read the GNU Affero General Public License in
# <https://www.github.com/TeamUltroid/Ultroid/blob/main/LICENSE/>.

import asyncio
from datetime import datetime

try:
    from pytz import timezone as tz
except ImportError:
    tz = None

from telethon import Button, events
from telethon.errors.rpcerrorlist import FloodWaitError, MessageDeleteForbiddenError
from telethon.utils import get_display_name

from pyUltroid._misc import SUDO_M, owner_and_sudos
from pyUltroid.dB.base import KeyManager
from pyUltroid.fns.helper import inline_mention
from strings import get_string

from . import *

Owner_info_msg = udB.get_key("BOT_INFO_START")
custom_info = bool(Owner_info_msg)

if not Owner_info_msg:
    Owner_info_msg = f"""
👑 **Oᴡɴᴇʀ:** {OWNER_NAME}
🆔 **Oᴡɴᴇʀ ID:** `{OWNER_ID}`

💬 **Mᴇssᴀɢᴇ Fᴏʀᴡᴀʀᴅs:** {udB.get_key("PMBOT")}

⚡ **Uʟᴛʀᴏɪᴅ** [`v{ultroid_version}`](https://github.com/TeamUltroid/Ultroid) | **Pᴏᴡᴇʀᴇᴅ ʙʏ @TeamUltroid**
"""

_settings = [
    [
        Button.inline("🔑 Aᴘɪ Kᴇʏs", data="cbs_apiset"),
        Button.inline("🤖 PM Bᴏᴛ", data="cbs_chatbot"),
    ],
    [
        Button.inline("✨ Aʟɪᴠᴇ", data="cbs_alvcstm"),
        Button.inline("🛡️ PM Pᴇʀᴍɪᴛ", data="cbs_ppmset"),
    ],
    [
        Button.inline("⚙️ Fᴇᴀᴛᴜʀᴇs", data="cbs_otvars"),
        Button.inline("🎵 VC Sᴏɴɢ Bᴏᴛ", data="cbs_vcb"),
    ],
    [Button.inline("« Bᴀᴄᴋ Mᴇɴᴜ", data="mainmenu")],
]

_start = [
    [
        Button.inline("🌐 Lᴀɴɢᴜᴀɢᴇ", data="lang"),
        Button.inline("⚙️ Sᴇᴛᴛɪɴɢs", data="setter"),
    ],
    [
        Button.inline("📊 Sᴛᴀᴛs", data="stat"),
        Button.inline("📻 Bʀᴏᴀᴅᴄᴀsᴛ", data="bcast"),
    ],
    [Button.inline("🌎 TɪᴍᴇZᴏɴᴇ", data="tz")],
]

@callback("ownerinfo")
async def own(event):
    try:
        msg = Owner_info_msg.format(
            mention=event.sender.mention,
            me=inline_mention(ultroid_bot.me),
        )
    except (KeyError, IndexError, ValueError):
        msg = Owner_info_msg

    if custom_info:
        msg += "\n\n• **Pᴏᴡᴇʀᴇᴅ ʙʏ @TeamUltroid**"

    await event.edit(
        msg,
        buttons=[Button.inline("❌ Cʟᴏsᴇ", data="closeit")],
        link_preview=False,
    )


@callback("closeit")
async def closet(lol):
    try:
        await lol.delete()
    except MessageDeleteForbiddenError:
        await lol.answer("⚠️ Mᴇssᴀɢᴇ ɪs ᴛᴏᴏ ᴏʟᴅ ᴛᴏ ᴅᴇʟᴇᴛᴇ!", alert=True)


@asst_cmd(pattern="start( (.*)|$)", forwards=False, func=lambda x: not x.is_group)
async def ultroid(event):
    args = event.pattern_match.group(1).strip()
    keym = KeyManager("BOT_USERS", cast=list)

    if not keym.contains(event.sender_id) and event.sender_id not in owner_and_sudos():
        keym.add(event.sender_id)
        if not udB.get_key("OFF_START_LOG"):
            log_msg = (
                f"👤 {inline_mention(event.sender)} `[{event.sender_id}]` "
                f"sᴛᴀʀᴛᴇᴅ ʏᴏᴜʀ [Assɪsᴛᴀɴᴛ Bᴏᴛ](@{asst.me.username})."
            )
            buttons = [[Button.inline("ℹ️ Iɴғᴏ", "itkkstyo")]]
            if event.sender.username:
                try:
                    input_ent = await event.client.get_input_entity(event.sender_id)
                    buttons[0].append(Button.mention("👤 Usᴇʀ", input_ent))
                except Exception:
                    pass

            log_channel = udB.get_key("LOG_CHANNEL")
            if log_channel:
                await event.client.send_message(
                    log_channel, log_msg, buttons=buttons
                )

    if event.sender_id not in SUDO_M.fullsudos:
        me = inline_mention(ultroid_bot.me)
        mention = inline_mention(event.sender)

        if args and args != "set":
            await get_stored_file(event, args)

        custom_start_msg = udB.get_key("STARTMSG")
        info_btn = [Button.inline("ℹ️ Oᴡɴᴇʀ Iɴғᴏ", data="ownerinfo")] if Owner_info_msg else None

        if not custom_start_msg:
            pm_text = (
                "\n\n💬 **Yᴏᴜ ᴄᴀɴ sᴇɴᴅ ʏᴏᴜʀ ᴍᴇssᴀɢᴇ ʜᴇʀᴇ ᴛᴏ ᴄᴏɴᴛᴀᴄᴛ ᴍʏ ᴍᴀsᴛᴇʀ.**"
                if udB.get_key("PMBOT")
                else ""
            )
            start_text = (
                f"👋 **Hᴇʏ** {mention},\n\n"
                f"I ᴀᴍ ᴛʜᴇ **Assɪsᴛᴀɴᴛ Bᴏᴛ** ᴏғ {me}.{pm_text}"
            )
        else:
            try:
                start_text = custom_start_msg.format(me=me, mention=mention)
            except (KeyError, IndexError, ValueError):
                start_text = custom_start_msg

        await event.reply(
            start_text,
            file=udB.get_key("STARTMEDIA"),
            buttons=[info_btn] if info_btn else None,
        )

    else:
        name = get_display_name(event.sender)
        if args == "set":
            await event.reply(
                "⚙️ **Cʜᴏᴏsᴇ ᴀɴ ᴏᴘᴛɪᴏɴ ᴛᴏ ᴄᴏɴғɪɢᴜʀᴇ:**",
                buttons=_settings,
            )
        elif args:
            await get_stored_file(event, args)
        else:
            menu_text = get_string("ast_3").format(name)
            await event.reply(
                f"✨ {menu_text}",
                buttons=_start,
            )


@callback("itkkstyo", owner=True)
async def ekekdhdb(e):
    text = (
        "ℹ️ **Nᴇᴡ Vɪsɪᴛᴏʀ Lᴏɢ**\n\n"
        "Wʜᴇɴ a ɴᴇᴡ ᴜsᴇʀ sᴛᴀʀᴛs ʏᴏᴜʀ Bᴏᴛ, ʏᴏᴜ ᴡɪʟʟ ʀᴇᴄᴇɪᴠᴇ ᴀ ʟᴏɢ.\n\n"
        f"🚫 **Tᴏ Dɪsᴀʙʟᴇ:** `{HNDLR}setdb OFF_START_LOG True`"
    )
    await e.answer(text, alert=True)


@callback("mainmenu", owner=True, func=lambda x: not x.is_group)
async def ultroid(event):
    await event.edit(
        get_string("ast_3").format(OWNER_NAME),
        buttons=_start,
    )


@callback("stat", owner=True)
async def botstat(event):
    total_users = len(udB.get_key("BOT_USERS") or [])
    msg = (
        "📊 **Uʟᴛʀᴏɪᴅ Assɪsᴛᴀɴᴛ - Sᴛᴀᴛs**\n"
        "━━━━━━━━━━━━━━━━━━━\n"
        f"👥 **Tᴏᴛᴀʟ Usᴇʀs:** `{total_users}`"
    )
    await event.answer(msg, cache_time=0, alert=True)


@callback("bcast", owner=True)
async def bdcast(event):
    keym = KeyManager("BOT_USERS", cast=list)
    users_list = keym.get() or []
    total = len(users_list)

    await event.edit(f"📻 **Bʀᴏᴀᴅᴄᴀsᴛ Mᴏᴅᴇ**\n\n👥 **Tᴀʀɢᴇᴛ Aᴜᴅɪᴇɴᴄᴇ:** `{total}` users.")

    async with event.client.conversation(OWNER_ID, timeout=120) as conv:
        try:
            await conv.send_message(
                "📝 **Eɴᴛᴇʀ ʏᴏᴜʀ ʙʀᴏᴀᴅᴄᴀsᴛ ᴍᴇssᴀɢᴇ.**\n"
                "💡 *Send /cancel to abort the operation.*"
            )
            response = await conv.get_response()

            if response.message.strip() == "/cancel":
                return await conv.send_message("❌ **Bʀᴏᴀᴅᴄᴀsᴛ ᴄᴀɴᴄᴇʟʟᴇᴅ!**")

            await conv.send_message(f"🚀 **Sᴛᴀʀᴛɪɴɢ ʙʀᴏᴀᴅᴄᴀsᴛ ᴛᴏ {total} ᴜsᴇʀs...**")

            success, fail = 0, 0
            start = datetime.now()

            for user_id in users_list:
                try:
                    await asst.send_message(int(user_id), response)
                    success += 1
                    await asyncio.sleep(0.05) 
                except FloodWaitError as fw:
                    await asyncio.sleep(fw.seconds + 2) 
                    try:
                        await asst.send_message(int(user_id), response)
                        success += 1
                    except Exception:
                        fail += 1
                except Exception:
                    fail += 1

            time_taken = (datetime.now() - start).seconds

            summary = (
                "✅ **Bʀᴏᴀᴅᴄᴀsᴛ Cᴏᴍᴘʟᴇᴛᴇᴅ!**\n"
                "━━━━━━━━━━━━━━━━━━━\n"
                f"⏱️ **Tɪᴍᴇ Tᴀᴋᴇɴ:** `{time_taken}s`\n"
                f"👥 **Tᴏᴛᴀʟ Usᴇʀs:** `{total}`\n"
                f"🎯 **Sᴜᴄᴄᴇss:** `{success}`\n"
                f"❌ **Fᴀɪʟᴇᴅ:** `{fail}`"
            )
            await conv.send_message(summary)

        except asyncio.TimeoutError:
            await conv.send_message("⌛ **Oᴘᴇʀᴀᴛɪᴏɴ ᴛɪᴍᴇᴅ ᴏᴜᴛ! Bʀᴏᴀᴅᴄᴀsᴛ ᴄᴀɴᴄᴇʟʟᴇᴅ.**")


@callback("setter", owner=True)
async def setting(event):
    await event.edit(
        "⚙️ **Cʜᴏᴏsᴇ ғʀᴏᴍ ᴛʜᴇ ᴏᴘᴛɪᴏɴs ʙᴇʟᴏᴡ:**",
        buttons=_settings,
    )


@callback("tz", owner=True)
async def timezone_(event):
    await event.delete()
    if tz is None:
        return await event.client.send_message(
            event.sender_id,
            "⚠️ **`pytz` is not installed! TimeZone feature is unavailable.**\n\n"
            f"💡 *Install it via:* `{HNDLR}update` or `{HNDLR}bash pip install pytz`",
        )

    pru = event.sender_id
    var = "TIMEZONE"
    name = "Timezone"

    async with event.client.conversation(pru, timeout=60) as conv:
        try:
            await conv.send_message(
                "🌎 **Sᴇɴᴅ ʏᴏᴜʀ TɪᴍᴇZᴏɴᴇ ғʀᴏᴍ ᴛʜɪs ʟɪsᴛ:**\n"
                "[🔗 Cʟɪᴄᴋ Hᴇʀᴇ Mᴀᴘ Lɪsᴛ](http://www.timezoneconverter.com/cgi-bin/findzone.tzc)\n\n"
                "💡 *Send /cancel to abort.*"
            )
            response = await conv.get_response()
            themssg = response.message.strip()

            if themssg == "/cancel":
                return await conv.send_message(
                    "❌ **OᴘᴇRᴀᴛɪᴏɴ Cᴀɴᴄᴇʟʟᴇᴅ!**",
                    buttons=get_back_button("mainmenu"),
                )

            try:
                tz(themssg)
                await setit(event, var, themssg)
                await conv.send_message(
                    f"✅ **{name} sᴜᴄᴄᴇssғᴜʟʟʏ ᴄʜᴀɴɢᴇᴅ ᴛᴏ:** `{themssg}`\n",
                    buttons=get_back_button("mainmenu"),
                )
            except Exception:
                await conv.send_message(
                    "❌ **Iɴᴠᴀʟɪᴅ TɪᴍᴇZᴏɴᴇ format! Pʟᴇᴀsᴇ ᴛʀʏ ᴀɢᴀɪɴ.**",
                    buttons=get_back_button("mainmenu"),
                )

        except asyncio.TimeoutError:
            await conv.send_message(
                "⌛ **Oᴘᴇʀᴀᴛɪᴏɴ ᴛɪᴍᴇᴅ ᴏᴜᴛ!**",
                buttons=get_back_button("mainmenu"),
            )
