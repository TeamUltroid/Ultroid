import html
import math

from telethon.tl import functions, types
from telethon.tl.functions.users import GetFullUserRequest
from telethon.tl.types import User
from telethon.utils import get_peer_id

from .. import LOGS, get_string, ultroid_cmd


@ultroid_cmd(
    pattern="info( (.*)|$)",
    manager=True,
)
async def _(event):
    user = event.pattern_match.group(1).strip()
    if not user:
        if event.is_reply:
            rpl = await event.get_reply_message()
            user = rpl.sender_id
        else:
            user = event.chat_id
    xx = await event.eor(get_string("com_1"))
    try:
        _ = await event.client.get_entity(user)
    except Exception as er:
        return await xx.edit(f"**ERROR :** {er}")
    if not isinstance(_, User):
        try:
            get_peer_id(_)
            photo, capt = await get_chat_info(_, event)
            if not photo:
                return await xx.eor(capt, parse_mode="html")
            await event.client.send_message(
                event.chat_id, capt[:1024], file=photo, parse_mode="html"
            )
            await xx.delete()
        except Exception as er:
            await event.eor("**ERROR ON CHATINFO**\n" + str(er))
        return
    try:
        full_user = (await event.client(GetFullUserRequest(user))).full_user
    except Exception as er:
        return await xx.edit(f"ERROR : {er}")
    user = _
    user_photos = (
        await event.client.get_profile_photos(user.id, limit=0)
    ).total or "NaN"
    user_id = user.id
    first_name = html.escape(user.first_name)
    if first_name is not None:
        first_name = first_name.replace("\u2060", "")
    last_name = user.last_name
    last_name = (
        last_name.replace("\u2060", "") if last_name else ("Last Name not found")
    )
    user_bio = html.escape(full_user.about or "")
    common_chats = full_user.common_chats_count
    if user.photo:
        dc_id = user.photo.dc_id
    else:
        dc_id = "Need a Profile Picture to check this"
    caption = f"""<b>Exᴛʀᴀᴄᴛᴇᴅ Dᴀᴛᴀ Fʀᴏᴍ Tᴇʟᴇɢʀᴀᴍ's Dᴀᴛᴀʙᴀsᴇ<b>
<b>••Tᴇʟᴇɢʀᴀᴍ ID</b>: <code>{user_id}</code>
<b>••Pᴇʀᴍᴀɴᴇɴᴛ Lɪɴᴋ</b>: <a href='tg://user?id={user_id}'>Click Here</a>
<b>••Fɪʀsᴛ Nᴀᴍᴇ</b>: <code>{first_name}</code>"""
    if not user.bot:
        caption += f"\n<b>••Sᴇᴄᴏɴᴅ Nᴀᴍᴇ</b>: <code>{last_name}</code>"
    caption += f"""\n<b>••Bɪᴏ</b>: <code>{user_bio}</code>
<b>••Dᴄ ID</b>: <code>{dc_id}</code>"""
    if user_photos:
        caption += f"\n<b>••Nᴏ. Oғ PғPs</b> : <code>{user_photos}</code>"
    if not user.bot:
        caption += f"\n<b>••Is Rᴇsᴛʀɪᴄᴛᴇᴅ</b>: <code>{user.restricted}</code>"
        caption += f"\n<b>••Is Pʀᴇᴍɪᴜᴍ</b>: <code>{user.premium}</code>"
    caption += f"""\n<b>••Vᴇʀɪғɪᴇᴅ</b>: <code>{user.verified}</code>
<b>••Is A Bᴏᴛ</b>: <code>{user.bot}</code>
<b>••Gʀᴏᴜᴘs Iɴ Cᴏᴍᴍᴏɴ</b>: <code>{common_chats}</code>
"""
    #     if chk := is_gbanned(user_id):
    #         caption += f"""<b>••Gʟᴏʙᴀʟʟʏ Bᴀɴɴᴇᴅ</b>: <code>True</code>
    # <b>••Rᴇᴀsᴏɴ</b>: <code>{chk}</code>"""
    await event.client.send_message(
        event.chat_id,
        caption,
        reply_to=event.reply_to_msg_id,
        parse_mode="HTML",
        file=full_user.profile_photo,
        force_document=False,
        silent=True,
    )
    await xx.delete()


async def get_chat_info(chat, event):
    if isinstance(chat, types.Channel):
        chat_info = await event.client(functions.channels.GetFullChannelRequest(chat))
    elif isinstance(chat, types.Chat):
        chat_info = await event.client(functions.messages.GetFullChatRequest(chat))
    else:
        return await event.eor("`Use this for Group/Channel.`")
    full = chat_info.full_chat
    chat_photo = full.chat_photo
    broadcast = getattr(chat, "broadcast", False)
    chat_type = "Channel" if broadcast else "Group"
    chat_title = chat.title
    try:
        msg_info = await event.client(
            functions.messages.GetHistoryRequest(
                peer=chat.id,
                offset_id=0,
                offset_date=None,
                add_offset=-0,
                limit=0,
                max_id=0,
                min_id=0,
                hash=0,
            )
        )
    except Exception as er:
        msg_info = None
        if not event.client._bot:
            LOGS.exception(er)
    first_msg_valid = bool(
        msg_info and msg_info.messages and msg_info.messages[0].id == 1
    )

    creator_valid = bool(first_msg_valid and msg_info.users)
    creator_id = msg_info.users[0].id if creator_valid else None
    creator_firstname = (
        msg_info.users[0].first_name
        if creator_valid and msg_info.users[0].first_name is not None
        else "Deleted Account"
    )
    creator_username = (
        msg_info.users[0].username
        if creator_valid and msg_info.users[0].username is not None
        else None
    )
    created = msg_info.messages[0].date if first_msg_valid else None
    if not isinstance(chat.photo, types.ChatPhotoEmpty):
        dc_id = chat.photo.dc_id
    else:
        dc_id = "Null"

    restricted_users = getattr(full, "banned_count", None)
    members = getattr(full, "participants_count", chat.participants_count)
    admins = getattr(full, "admins_count", None)
    banned_users = getattr(full, "kicked_count", None)
    members_online = getattr(full, "online_count", 0)
    group_stickers = (
        full.stickerset.title if getattr(full, "stickerset", None) else None
    )
    messages_viewable = msg_info.count if msg_info else None
    messages_sent = getattr(full, "read_inbox_max_id", None)
    messages_sent_alt = getattr(full, "read_outbox_max_id", None)
    exp_count = getattr(full, "pts", None)
    supergroup = "<b>Yes</b>" if getattr(chat, "megagroup", None) else "No"
    creator_username = "@{}".format(creator_username) if creator_username else None

    if admins is None:
        try:
            participants_admins = await event.client(
                functions.channels.GetParticipantsRequest(
                    channel=chat.id,
                    filter=types.ChannelParticipantsAdmins(),
                    offset=0,
                    limit=0,
                    hash=0,
                )
            )
            admins = participants_admins.count if participants_admins else None
        except Exception as e:
            LOGS.info(f"Exception: {e}")
    caption = "ℹ️ <b>[<u>CHAT INFO</u>]</b>\n"
    caption += f"🆔 <b>ID:</b> <code>{chat.id}</code>\n"
    if chat_title is not None:
        caption += f"📛 <b>{chat_type} name:</b> <code>{chat_title}</code>\n"
    if chat.username:
        caption += f"🔗 <b>Link:</b> @{chat.username}\n"
    else:
        caption += f"🗳 <b>{chat_type} type:</b> Private\n"
    if creator_username:
        caption += f"🖌 <b>Creator:</b> {creator_username}\n"
    elif creator_valid:
        caption += f'🖌 <b>Creator:</b> <a href="tg://user?id={creator_id}">{creator_firstname}</a>\n'
    if created:
        caption += f"🖌 <b>Created:</b> <code>{created.date().strftime('%b %d, %Y')} - {created.time()}</code>\n"
    else:
        caption += f"🖌 <b>Created:</b> <code>{chat.date.date().strftime('%b %d, %Y')} - {chat.date.time()}</code> ⚠\n"
    caption += f"🗡 <b>Data Centre ID:</b> {dc_id}\n"
    if exp_count is not None:
        chat_level = int((1 + math.sqrt(1 + 7 * exp_count / 14)) / 2)
        caption += f"⭐️ <b>{chat_type} level:</b> <code>{chat_level}</code>\n"
    if messages_viewable is not None:
        caption += f"💬 <b>Viewable messages:</b> <code>{messages_viewable}</code>\n"
    if messages_sent:
        caption += f"💬 <b>Messages sent:</b> <code>{messages_sent}</code>\n"
    elif messages_sent_alt:
        caption += f"💬 <b>Messages sent:</b> <code>{messages_sent_alt}</code> ⚠\n"
    if members is not None:
        caption += f"👥 <b>Members:</b> <code>{members}</code>\n"
    if admins:
        caption += f"👮 <b>Administrators:</b> <code>{admins}</code>\n"
    if full.bot_info:
        caption += f"🤖 <b>Bots:</b> <code>{len(full.bot_info)}</code>\n"
    if members_online:
        caption += f"👀 <b>Currently online:</b> <code>{members_online}</code>\n"
    if restricted_users is not None:
        caption += f"🔕 <b>Restricted users:</b> <code>{restricted_users}</code>\n"
    if banned_users:
        caption += f"📨 <b>Banned users:</b> <code>{banned_users}</code>\n"
    if group_stickers:
        caption += f'📹 <b>{chat_type} stickers:</b> <a href="t.me/addstickers/{full.stickerset.short_name}">{group_stickers}</a>\n'
    if not broadcast:
        if getattr(chat, "slowmode_enabled", None):
            caption += f"👉 <b>Slow mode:</b> <code>True</code>"
            caption += f", 🕐 <code>{full.slowmode_seconds}s</code>\n"
        else:
            caption += f"🦸‍♂ <b>Supergroup:</b> {supergroup}\n"
    if getattr(chat, "restricted", None):
        caption += f"🎌 <b>Restricted:</b> {chat.restricted}\n"
        rist = chat.restriction_reason[0]
        caption += f"> Platform: {rist.platform}\n"
        caption += f"> Reason: {rist.reason}\n"
        caption += f"> Text: {rist.text}\n\n"
    if getattr(chat, "scam", None):
        caption += "⚠ <b>Scam:</b> <b>Yes</b>\n"
    if getattr(chat, "verified", None):
        caption += f"✅ <b>Verified by Telegram:</b> <code>Yes</code>\n\n"
    if full.about:
        caption += f"🗒 <b>Description:</b> \n<code>{full.about}</code>\n"
    return chat_photo, caption
