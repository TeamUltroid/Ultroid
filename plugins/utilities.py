# Ultroid - UserBot
# Copyright (C) 2021-2025 TeamUltroid
#
# This file is a part of < https://github.com/TeamUltroid/Ultroid/ >
# PLease read the GNU Affero General Public License in
# <https://www.github.com/TeamUltroid/Ultroid/blob/main/LICENSE/>.
"""
✘ Commands Available -

• `{i}kickme` : Leaves the group.

• `{i}date` : Show Calender.

• `{i}listreserved`
    List all usernames (channels/groups) you own.

• `{i}stats` : See your profile stats.

• `{i}paste` - `Include long text / Reply to text file.`

• `{i}info <username/userid/chatid>`
    Reply to someone's msg.

• `{i}invite <username/userid>`
    Add user to the chat.

• `{i}rmbg <reply to pic>`
    Remove background from that picture.

• `{i}telegraph <reply to media/text>`
    Upload media/text to telegraph.

• `{i}json <reply to msg>`
    Get the json encoding of the message.

• `{i}suggest <reply to message> or <poll title>`
    Create a Yes/No poll for the replied suggestion.

• `{i}ipinfo <ipAddress>` : Get info about that IP address.

• `{i}cpy <reply to message>`
   Copy the replied message, with formatting. Expires in 24hrs.
• `{i}pst`
   Paste the copied message, with formatting.

• `{i}thumb <reply file>` : Download the thumbnail of the replied file.

• `{i}getmsg <message link>`
  Get messages from chats with forward/copy restrictions.
"""

import asyncio
import calendar
import html
import io
import os
import pathlib
import time, math
from datetime import datetime as dt

try:
    from PIL import Image
except ImportError:
    Image = None

from pyUltroid._misc._assistant import asst_cmd
from pyUltroid.dB.gban_mute_db import is_gbanned
from pyUltroid.fns.tools import get_chat_and_msgid

from . import upload_file as uf

from telethon.errors.rpcerrorlist import ChatForwardsRestrictedError, UserBotError
from telethon.errors import MessageTooLongError
from telethon.events import NewMessage
from telethon.tl import types, functions
from telethon.tl.custom import Dialog
from telethon.tl.functions.channels import (
    GetAdminedPublicChannelsRequest,
    InviteToChannelRequest,
    LeaveChannelRequest,
)
from telethon.tl.functions.contacts import GetBlockedRequest
from telethon.tl.functions.messages import AddChatUserRequest, GetAllStickersRequest
from telethon.tl.functions.users import GetFullUserRequest
from telethon.tl.types import (
    Channel,
    Chat,
    InputMediaPoll,
    Poll,
    PollAnswer,
    TLObject,
    User,
    UserStatusOffline,
    UserStatusOnline,
    MessageMediaPhoto,
    MessageMediaDocument,
    DocumentAttributeVideo,
    
)
from telethon.utils import get_peer_id

from pyUltroid.fns.info import get_chat_info

from . import (
    HNDLR,
    LOGS,
    Image,
    ReTrieveFile,
    Telegraph,
    asst,
    async_searcher,
    bash,
    check_filename,
    eod,
    eor,
    get_paste,
    get_string,
    inline_mention,
    json_parser,
    mediainfo,
    udB,
    ultroid_cmd,
)

# =================================================================#

TMP_DOWNLOAD_DIRECTORY = "resources/downloads/"

CAPTION_LIMIT = 1024  # Telegram's caption character limit for non-premium

_copied_msg = {}


@ultroid_cmd(pattern="kickme$", fullsudo=True)
async def leave(ult):
    await ult.eor(f"`{ult.client.me.first_name} has left this group, bye!!.`")
    await ult.client(LeaveChannelRequest(ult.chat_id))


@ultroid_cmd(
    pattern="date$",
)
async def date(event):
    m = dt.now().month
    y = dt.now().year
    d = dt.now().strftime("Date - %B %d, %Y\nTime- %H:%M:%S")
    k = calendar.month(y, m)
    await event.eor(f"`{k}\n\n{d}`")


@ultroid_cmd(
    pattern="listreserved$",
)
async def _(event):
    result = await event.client(GetAdminedPublicChannelsRequest())
    if not result.chats:
        return await event.eor("`No username Reserved`")
    output_str = "".join(
        f"- {channel_obj.title} @{channel_obj.username} \n"
        for channel_obj in result.chats
    )
    await event.eor(output_str)


@ultroid_cmd(
    pattern="stats$",
)
async def stats(
    event: NewMessage.Event,
):
    ok = await event.eor("`Collecting stats...`")
    start_time = time.time()
    private_chats = 0
    bots = 0
    groups = 0
    broadcast_channels = 0
    admin_in_groups = 0
    creator_in_groups = 0
    admin_in_broadcast_channels = 0
    creator_in_channels = 0
    unread_mentions = 0
    unread = 0
    dialog: Dialog
    async for dialog in event.client.iter_dialogs():
        entity = dialog.entity
        if isinstance(entity, Channel) and entity.broadcast:
            broadcast_channels += 1
            if entity.creator or entity.admin_rights:
                admin_in_broadcast_channels += 1
            if entity.creator:
                creator_in_channels += 1

        elif (isinstance(entity, Channel) and entity.megagroup) or isinstance(
            entity, Chat
        ):
            groups += 1
            if entity.creator or entity.admin_rights:
                admin_in_groups += 1
            if entity.creator:
                creator_in_groups += 1

        elif isinstance(entity, User):
            private_chats += 1
            if entity.bot:
                bots += 1

        unread_mentions += dialog.unread_mentions_count
        unread += dialog.unread_count
    stop_time = time.time() - start_time
    try:
        ct = (await event.client(GetBlockedRequest(1, 0))).count
    except AttributeError:
        ct = 0
    try:
        sp = await event.client(GetAllStickersRequest(0))
        sp_count = len(sp.sets)
    except BaseException:
        sp_count = 0
    full_name = inline_mention(event.client.me)
    response = f"🔸 **Stats for {full_name}** \n\n"
    response += f"**Private Chats:** {private_chats} \n"
    response += f"**  •• **`Users: {private_chats - bots}` \n"
    response += f"**  •• **`Bots: {bots}` \n"
    response += f"**Groups:** {groups} \n"
    response += f"**Channels:** {broadcast_channels} \n"
    response += f"**Admin in Groups:** {admin_in_groups} \n"
    response += f"**  •• **`Creator: {creator_in_groups}` \n"
    response += f"**  •• **`Admin Rights: {admin_in_groups - creator_in_groups}` \n"
    response += f"**Admin in Channels:** {admin_in_broadcast_channels} \n"
    response += f"**  •• **`Creator: {creator_in_channels}` \n"
    response += f"**  •• **`Admin Rights: {admin_in_broadcast_channels - creator_in_channels}` \n"
    response += f"**Unread:** {unread} \n"
    response += f"**Unread Mentions:** {unread_mentions} \n"
    response += f"**Blocked Users:** {ct}\n"
    response += f"**Total Stickers Pack Installed :** `{sp_count}`\n\n"
    response += f"**__It Took:__** {stop_time:.02f}s \n"
    await ok.edit(response)


@ultroid_cmd(pattern="paste( (.*)|$)", manager=True, allow_all=True)
async def _(event):
    try:
        input_str = event.text.split(maxsplit=1)[1]
    except IndexError:
        input_str = None
    xx = await event.eor("` 《 Pasting... 》 `")
    downloaded_file_name = None
    if input_str:
        message = input_str
    elif event.reply_to_msg_id:
        previous_message = await event.get_reply_message()
        if previous_message.media:
            downloaded_file_name = await event.client.download_media(
                previous_message,
                "./resources/downloads",
            )
            with open(downloaded_file_name, "r") as fd:
                message = fd.read()
            os.remove(downloaded_file_name)
        else:
            message = previous_message.message
    else:
        message = None
    if not message:
        return await xx.eor(
            "`Reply to a Message/Document or Give me Some Text !`", time=5
        )
    done, data = await get_paste(message)
    if not done and data.get("error"):
        return await xx.eor(data["error"])
    reply_text = (
        f"• **Pasted to SpaceBin :** [Space]({data['link']})\n• **Raw Url :** : [Raw]({data['raw']})"
    )
    try:
        if event.client._bot:
            return await xx.eor(reply_text)
        ok = await event.client.inline_query(asst.me.username, f"pasta-{data['link']}")
        await ok[0].click(event.chat_id, reply_to=event.reply_to_msg_id, hide_via=True)
        await xx.delete()
    except BaseException as e:
        LOGS.exception(e)
        await xx.edit(reply_text)


@ultroid_cmd(
    pattern="info( (.*)|$)",
    manager=True,
)
async def getInfo(event):
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
    if not isinstance(_, types.User):
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
        full_user: types.UserFull = (await event.client(GetFullUserRequest(user))).full_user
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
        last_name.replace("\u2060", "") if last_name else (
            "Last Name not found")
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
    if (b_date:= full_user.birthday):
        date = f"{b_date.day}-{b_date.month}"
        if b_date.year:
            date += f"-{b_date.year}"
        caption += f"\n<b>••Birthday</b> : <code>{date}</code>"  
    if full_user.stories:
        caption += f"\n<b>••Stories Count</b> : <code>{len(full_user.stories.stories)}</code>"  
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
    creator_username = "@{}".format(
        creator_username) if creator_username else None

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


@ultroid_cmd(
    pattern="invite( (.*)|$)",
    groups_only=True,
)
async def _(ult):
    xx = await ult.eor(get_string("com_1"))
    to_add_users = ult.pattern_match.group(1).strip()
    if not ult.is_channel and ult.is_group:
        for user_id in to_add_users.split(" "):
            try:
                await ult.client(
                    AddChatUserRequest(
                        chat_id=ult.chat_id,
                        user_id=await ult.client.parse_id(user_id),
                        fwd_limit=1000000,
                    ),
                )
                await xx.edit(f"Successfully invited `{user_id}` to `{ult.chat_id}`")
            except Exception as e:
                await xx.edit(str(e))
    else:
        for user_id in to_add_users.split(" "):
            try:
                await ult.client(
                    InviteToChannelRequest(
                        channel=ult.chat_id,
                        users=[await ult.client.parse_id(user_id)],
                    ),
                )
                await xx.edit(f"Successfully invited `{user_id}` to `{ult.chat_id}`")
            except UserBotError:
                await xx.edit(
                    f"Bots can only be added as Admins in Channel.\nBetter Use `{HNDLR}promote {user_id}`"
                )
            except Exception as e:
                await xx.edit(str(e))


@ultroid_cmd(
    pattern="rmbg($| (.*))",
)
async def abs_rmbg(event):
    RMBG_API = udB.get_key("RMBG_API")
    if not RMBG_API:
        return await event.eor(
            "Get your API key from [here](https://www.remove.bg/) for this plugin to work.",
        )
    match = event.pattern_match.group(1).strip()
    reply = await event.get_reply_message()
    if match and os.path.exists(match):
        dl = match
    elif reply and reply.media:
        if reply.document and reply.document.thumbs:
            dl = await reply.download_media(thumb=-1)
        else:
            dl = await reply.download_media()
    else:
        return await eod(
            event, f"Use `{HNDLR}rmbg` as reply to a pic to remove its background."
        )
    if not (dl and dl.endswith(("webp", "jpg", "png", "jpeg"))):
        os.remove(dl)
        return await event.eor(get_string("com_4"))
    if dl.endswith("webp"):
        file = f"{dl}.png"
        Image.open(dl).save(file)
        os.remove(dl)
        dl = file
    xx = await event.eor("`Sending to remove.bg`")
    dn, out = await ReTrieveFile(dl)
    os.remove(dl)
    if not dn:
        dr = out["errors"][0]
        de = dr.get("detail", "")
        return await xx.edit(
            f"**ERROR ~** `{dr['title']}`,\n`{de}`",
        )
    zz = Image.open(out)
    if zz.mode != "RGB":
        zz.convert("RGB")
    wbn = check_filename("ult-rmbg.webp")
    zz.save(wbn, "webp")
    await event.client.send_file(
        event.chat_id,
        out,
        force_document=True,
        reply_to=reply,
    )
    await event.client.send_file(event.chat_id, wbn, reply_to=reply)
    os.remove(out)
    os.remove(wbn)
    await xx.delete()


@ultroid_cmd(
    pattern="telegraph( (.*)|$)",
)
async def telegraphcmd(event):
    xx = await event.eor(get_string("com_1"))
    match = event.pattern_match.group(1).strip() or "Ultroid"
    reply = await event.get_reply_message()
    if not reply:
        return await xx.eor("`Reply to Message.`")
    if not reply.media and reply.message:
        content = reply.message
    else:
        getit = await reply.download_media()
        dar = mediainfo(reply.media)
        if dar == "sticker":
            file = f"{getit}.png"
            Image.open(getit).save(file)
            os.remove(getit)
            getit = file
        elif dar.endswith("animated"):
            file = f"{getit}.gif"
            await bash(f"lottie_convert.py '{getit}' {file}")
            os.remove(getit)
            getit = file
        if "document" not in dar:
            try:
                nn = uf(getit)
                amsg = f"Uploaded to [Telegraph]({nn}) !"
            except Exception as e:
                amsg = f"Error : {e}"
            os.remove(getit)
            return await xx.eor(amsg)
        content = pathlib.Path(getit).read_text()
        os.remove(getit)
    makeit = Telegraph.create_page(title=match, content=[content])
    await xx.eor(
        f"Pasted to Telegraph : [Telegraph]({makeit['url']})", link_preview=False
    )


@ultroid_cmd(pattern="json( (.*)|$)")
async def _(event):
    reply_to_id = None
    match = event.pattern_match.group(1).strip()
    if event.reply_to_msg_id:
        msg = await event.get_reply_message()
        reply_to_id = event.reply_to_msg_id
    else:
        msg = event
        reply_to_id = event.message.id
    if match and hasattr(msg, match.split()[0]):
        msg = getattr(msg, match.split()[0])
        try:
            if hasattr(msg, "to_json"):
                msg = msg.to_json(ensure_ascii=False, indent=1)
            elif hasattr(msg, "to_dict"):
                msg = json_parser(msg.to_dict(), indent=1)
            else:
                msg = TLObject.stringify(msg)
        except Exception:
            pass
        msg = str(msg)
    else:
        msg = json_parser(msg.to_json(), indent=1)
    if "-t" in match:
        try:
            data = json_parser(msg)
            msg = json_parser(
                {key: data[key] for key in data.keys() if data[key]}, indent=1
            )
        except Exception:
            pass
    if len(msg) > 4096:
        with io.BytesIO(str.encode(msg)) as out_file:
            out_file.name = "json-ult.txt"
            await event.client.send_file(
                event.chat_id,
                out_file,
                force_document=True,
                allow_cache=False,
                reply_to=reply_to_id,
            )
            await event.delete()
    else:
        await event.eor(f"```{msg or None}```")


@ultroid_cmd(pattern="suggest( (.*)|$)", manager=True)
async def sugg(event):
    sll = event.text.split(maxsplit=1)
    try:
        text = sll[1]
    except IndexError:
        text = None
    if not (event.is_reply or text):
        return await eod(
            event,
            "`Please reply to a message to make a suggestion poll!`",
        )
    if event.is_reply and not text:
        reply = await event.get_reply_message()
        if reply.text and len(reply.text) < 35:
            text = reply.text
        else:
            text = "Do you Agree to Replied Suggestion ?"
    reply_to = event.reply_to_msg_id if event.is_reply else event.id
    try:
        await event.client.send_file(
            event.chat_id,
            file=InputMediaPoll(
                poll=Poll(
                    id=12345,
                    question=text,
                    answers=[PollAnswer("Yes", b"1"), PollAnswer("No", b"2")],
                ),
            ),
            reply_to=reply_to,
        )
    except Exception as e:
        return await eod(event, f"`Oops, you can't send polls here!\n\n{e}`")
    await event.delete()


@ultroid_cmd(pattern="ipinfo( (.*)|$)")
async def ipinfo(event):
    ip = event.text.split()
    ipaddr = ""
    try:
        ipaddr = f"/{ip[1]}"
    except IndexError:
        ipaddr = ""
    det = await async_searcher(f"https://ipinfo.io{ipaddr}/geo", re_json=True)
    try:
        ip = det["ip"]
        city = det["city"]
        region = det["region"]
        country = det["country"]
        cord = det["loc"]
        try:
            zipc = det["postal"]
        except KeyError:
            zipc = "None"
        tz = det["timezone"]
        await eor(
            event,
            """
**IP Details Fetched.**

**IP:** `{}`
**City:** `{}`
**Region:** `{}`
**Country:** `{}`
**Co-ordinates:** `{}`
**Postal Code:** `{}`
**Time Zone:** `{}`
""".format(
                ip,
                city,
                region,
                country,
                cord,
                zipc,
                tz,
            ),
        )
    except BaseException:
        err = det["error"]["title"]
        msg = det["error"]["message"]
        await event.eor(f"ERROR:\n{err}\n{msg}", time=5)


@ultroid_cmd(
    pattern="cpy$",
)
async def copp(event):
    msg = await event.get_reply_message()
    if not msg:
        return await event.eor(f"Use `{HNDLR}cpy` as reply to a message!", time=5)
    _copied_msg["CLIPBOARD"] = msg
    await event.eor(f"Copied. Use `{HNDLR}pst` to paste!", time=10)


@asst_cmd(pattern="pst$")
async def pepsodent(event):
    await toothpaste(event)


@ultroid_cmd(
    pattern="pst$",
)
async def colgate(event):
    await toothpaste(event)


async def toothpaste(event):
    try:
        await event.respond(_copied_msg["CLIPBOARD"])
    except KeyError:
        return await eod(
            event,
            f"Nothing was copied! Use `{HNDLR}cpy` as reply to a message first!",
        )
    except Exception as ex:
        return await event.eor(str(ex), time=5)
    await event.delete()


@ultroid_cmd(pattern="thumb$")
async def thumb_dl(event):
    reply = await event.get_reply_message()
    if not (reply and reply.file):
        return await eod(event, get_string("th_1"), time=5)
    if not reply.file.media.thumbs:
        return await eod(event, get_string("th_2"))
    await event.eor(get_string("com_1"))
    x = await event.get_reply_message()
    m = await x.download_media(thumb=-1)
    await event.reply(file=m)
    os.remove(m)


async def get_video_duration(file_path):
    cmd = [
        "ffprobe",
        "-v",
        "error",
        "-show_entries",
        "format=duration",
        "-of",
        "default=noprint_wrappers=1:nokey=1",
        file_path,
    ]
    try:
        result = await asyncio.create_subprocess_exec(
            *cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
        )
        stdout, stderr = await result.communicate()
        duration = float(stdout.decode().strip())
        return duration
    except Exception as e:
        print("Error running ffprobe:", e)
        return None

async def get_thumbnail(file_path, thumbnail_path):
    try:
        await asyncio.create_subprocess_exec(
            "ffmpeg",
            "-i", file_path,
            "-ss", "00:00:04",
            "-vframes", "1",  # Extract a single frame as the thumbnail
            thumbnail_path,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
    except Exception as e:
        print(f"Error extracting thumbnail: {e}")



@ultroid_cmd(pattern="getmsg( ?(.*)|$)")
async def get_restricted_msg(event):
    match = event.pattern_match.group(1).strip()
    if not match:
        await event.eor("`Please provide a link!`", time=5)
        return
    
    xx = await event.eor("`Loading...`")
    chat, msg = get_chat_and_msgid(match)
    if not (chat and msg):
        return await event.eor(
            "Invalid link!\nExamples:\n"
            "`https://t.me/TeamUltroid/3`\n"
            "`https://t.me/c/1313492028/3`\n"
            "`tg://openmessage?user_id=1234567890&message_id=1`"
        )
    
    try:
        input_entity = await event.client.get_input_entity(chat)
        message = await event.client.get_messages(input_entity, ids=msg)
    except BaseException as er:
        return await event.eor(f"**ERROR**\n`{er}`")
    
    if not message:
        return await event.eor("`Message not found or may not exist.`")
    
    try:
        await event.client.send_message(event.chat_id, message)
        await xx.try_delete()
        return
    except ChatForwardsRestrictedError:
        pass
    
    if message.media:
        if isinstance(message.media, (MessageMediaPhoto, MessageMediaDocument)):
            media_path, _ = await event.client.fast_downloader(message.document, show_progress=True, event=xx, message=get_string("com_5"))

            caption = message.text or ""

            attributes = []
            if message.video:
                duration = await get_video_duration(media_path.name)
                
                width, height = 0, 0
                for attribute in message.document.attributes:
                    if isinstance(attribute, DocumentAttributeVideo):
                        width = attribute.w
                        height = attribute.h
                        break
                
                thumb_path = media_path.name + "_thumb.jpg"
                await get_thumbnail(media_path.name, thumb_path)

                attributes.append(
                    DocumentAttributeVideo(
                        duration=int(duration) if duration else 0,
                        w=width,
                        h=height,
                        supports_streaming=True,
                    )
                )
            await xx.edit(get_string("com_6"))
            media_path, _ = await event.client.fast_uploader(media_path.name, event=xx, show_progress=True, to_delete=True)

            try:
                await event.client.send_file(
                    event.chat_id,
                    media_path,
                    caption=caption,
                    force_document=False,
                    supports_streaming=True if message.video else False,
                    thumb=thumb_path if message.video else None,
                    attributes=attributes if message.video else None,
                )
            except MessageTooLongError:
                if len(caption) > CAPTION_LIMIT:
                    caption = caption[:CAPTION_LIMIT] + "..."
                await event.client.send_file(
                    event.chat_id,
                    media_path,
                    caption=caption,
                    force_document=False,  # Set to True if you want to send as a document
                    supports_streaming=True if message.video else False,
                    thumb=thumb_path if message.video else None,
                    attributes=attributes if message.video else None,
                )

            if message.video and os.path.exists(thumb_path):
                os.remove(thumb_path)
            await xx.try_delete()
        else:
            await event.eor("`Cannot process this type of media.`")
    else:
        await event.eor("`No media found in the message.`")
