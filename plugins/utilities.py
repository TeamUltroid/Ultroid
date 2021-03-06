# Ultroid - UserBot
# Copyright (C) 2020 TeamUltroid
#
# This file is a part of < https://github.com/TeamUltroid/Ultroid/ >
# PLease read the GNU Affero General Public License in
# <https://www.github.com/TeamUltroid/Ultroid/blob/main/LICENSE/>.
from telethon.tl.types import ChannelParticipantCreator as lbcn
from telethon.utils import get_display_name

"""
✘ Commands Available -

• `{i}kickme`
    Leaves the group in which it is used.

• `{i}calc <equation>`
    A simple calculator.

• `{i}date`
    Show Calender.

• `{i}chatinfo`
    Get full info about the group/chat.

• `{i}listreserved`
    List all usernames (channels/groups) you own.

• `{i}stats`
    See your profile stats.

• `{i}paste`
    Include long text / Reply to text file.

• `{i}hastebin`
    Include long text / Reply to text file.

• `{i}info <username/userid>`
    Reply to someone's msg.

• `{i}invite <username/userid>`
    Add user to the chat.

• `{i}rmbg <reply to pic>`
    Remove background from that picture.

• `{i}telegraph <reply to media/text>`
    Upload media/text to telegraph.

• `{i}json <reply to msg>`
    Get the json encoding of the message.

• `{i}suggest <reply to message>`
    Create a Yes/No poll for the replied suggestion.
"""
import asyncio
import calendar
import html
import io
import os
import sys
import time
import traceback
from datetime import datetime as dt

import pytz
import requests
from telegraph import Telegraph
from telegraph import upload_file as uf
from telethon import functions
from telethon.errors.rpcerrorlist import BotInlineDisabledError
from telethon.errors.rpcerrorlist import BotMethodInvalidError as bmi
from telethon.errors.rpcerrorlist import (BotResponseTimeoutError,
                                          ChatSendInlineForbiddenError)
from telethon.events import NewMessage
from telethon.tl.custom import Dialog
from telethon.tl.functions.channels import LeaveChannelRequest
from telethon.tl.functions.photos import GetUserPhotosRequest
from telethon.tl.types import (Channel, Chat, InputMediaPoll, Poll, PollAnswer,
                               User)
from telethon.utils import get_input_location

# =================================================================#
from . import *

TMP_DOWNLOAD_DIRECTORY = "resources/downloads/"

# Telegraph Things
telegraph = Telegraph()
telegraph.create_account(short_name="Ultroid")
# ================================================================#

async def miraculous(chat, event):
    # chat.chats is a list so we use get_entity() to avoid IndexError
    chat_obj_info = await event.client.get_entity(chat.full_chat.id)
    broadcast = chat_obj_info.broadcast if hasattr(chat_obj_info, "broadcast") else False
    chat_type = "Channel" if broadcast else "Group"
    chat_title = chat_obj_info.title
    warn_emoji = emojize(":warning:")
    try:
        msg_info = await event.client(GetHistoryRequest(peer=chat_obj_info.id, offset_id=0, offset_date=datetime(2010, 1, 1), 
                                                        add_offset=-1, limit=1, max_id=0, min_id=0, hash=0))
    except Exception as e:
        msg_info = None
        print("Exception:", e)
    # No chance for IndexError as it checks for msg_info.messages first
    first_msg_valid = True if msg_info and msg_info.messages and msg_info.messages[0].id == 1 else False
    # Same for msg_info.users
    creator_valid = True if first_msg_valid and msg_info.users else False
    #Sh1vam
    async for shivam in event.client.iter_participants(await event.get_input_chat()):
                             lb=shivam.status
                             cn=shivam.participant
                             if isinstance(cn, lbcn):
                                 sh=shivam.id
                                 iv=shivam.username
                                 am=shivam.first_name##solbed by Sh1vam
    creator_id = int(sh)
    creator_firstname = am
    creator_username = iv
    created = msg_info.messages[0].date if first_msg_valid else None
    former_title = msg_info.messages[0].action.title if first_msg_valid and type(msg_info.messages[0].action) is MessageActionChannelMigrateFrom and msg_info.messages[0].action.title != chat_title else None
    try:
        dc_id, location = get_input_location(chat.full_chat.chat_photo)
    except Exception as e:
        dc_id = "Unknown"
        location = str(e)
    
    #this is some spaghetti I need to change
    description = chat.full_chat.about
    members = chat.full_chat.participants_count if hasattr(chat.full_chat, "participants_count") else chat_obj_info.participants_count
    admins = chat.full_chat.admins_count if hasattr(chat.full_chat, "admins_count") else None
    banned_users = chat.full_chat.kicked_count if hasattr(chat.full_chat, "kicked_count") else None
    restrcited_users = chat.full_chat.banned_count if hasattr(chat.full_chat, "banned_count") else None
    members_online = chat.full_chat.online_count if hasattr(chat.full_chat, "online_count") else 0
    group_stickers = chat.full_chat.stickerset.title if hasattr(chat.full_chat, "stickerset") and chat.full_chat.stickerset else None
    messages_viewable = msg_info.count if msg_info else None
    messages_sent = chat.full_chat.read_inbox_max_id if hasattr(chat.full_chat, "read_inbox_max_id") else None
    messages_sent_alt = chat.full_chat.read_outbox_max_id if hasattr(chat.full_chat, "read_outbox_max_id") else None
    exp_count = chat.full_chat.pts if hasattr(chat.full_chat, "pts") else None
    username = chat_obj_info.username if hasattr(chat_obj_info, "username") else None
    bots_list = chat.full_chat.bot_info  # this is a list
    bots = 0
    supergroup = "<b>Yes</b>" if hasattr(chat_obj_info, "megagroup") and chat_obj_info.megagroup else "No"
    slowmode = "<b>Yes</b>" if hasattr(chat_obj_info, "slowmode_enabled") and chat_obj_info.slowmode_enabled else "No"
    slowmode_time = chat.full_chat.slowmode_seconds if hasattr(chat_obj_info, "slowmode_enabled") and chat_obj_info.slowmode_enabled else None
    restricted = "<b>Yes</b>" if hasattr(chat_obj_info, "restricted") and chat_obj_info.restricted else "No"
    verified = "<b>Yes</b>" if hasattr(chat_obj_info, "verified") and chat_obj_info.verified else "No"
    username = "@{}".format(username) if username else None
    creator_username = "@{}".format(creator_username) if creator_username else None
    #end of spaghetti block
    
    if admins is None:
        # use this alternative way if chat.full_chat.admins_count is None, works even without being an admin
        try:
            participants_admins = await event.client(GetParticipantsRequest(channel=chat.full_chat.id, filter=ChannelParticipantsAdmins(),
                                                                            offset=0, limit=0, hash=0))
            admins = participants_admins.count if participants_admins else None
        except Exception as e:
            print("Exception:", e)
    if bots_list:
        for bot in bots_list:
            bots += 1

    caption = "<b>CHAT INFO:</b>\n"
    caption += f"ID: <code>{chat_obj_info.id}</code>\n"
    if chat_title is not None:
        caption += f"{chat_type} name: {chat_title}\n"
    if former_title is not None:  # Meant is the very first title
        caption += f"Former name: {former_title}\n"
    if username is not None:
        caption += f"{chat_type} type: Public\n"
        caption += f"Link: {username}\n"
    else:
        caption += f"{chat_type} type: Private\n"
    if creator_username is not None:
        caption += f"Creator: {creator_username}\n"
    elif creator_valid:
        caption += f"Creator: <a href=\"tg://user?id={creator_id}\">{creator_firstname}</a>\n"
    if created is not None:
        caption += f"Created: <code>{created.date().strftime('%b %d, %Y')} - {created.time()}</code>\n"
    else:
        caption += f"Created: <code>{chat_obj_info.date.date().strftime('%b %d, %Y')} - {chat_obj_info.date.time()}</code> {warn_emoji}\n"
    caption += f"Data Centre ID: {dc_id}\n"
    if exp_count is not None:
        chat_level = int((1+sqrt(1+7*exp_count/14))/2)
        caption += f"{chat_type} level: <code>{chat_level}</code>\n"
    if messages_viewable is not None:
        caption += f"Viewable messages: <code>{messages_viewable}</code>\n"
    if messages_sent:
        caption += f"Messages sent: <code>{messages_sent}</code>\n"
    elif messages_sent_alt:
        caption += f"Messages sent: <code>{messages_sent_alt}</code> {warn_emoji}\n"
    if members is not None:
        caption += f"Members: <code>{members}</code>\n"
    if admins is not None:
        caption += f"Administrators: <code>{admins}</code>\n"
    if bots_list:
        caption += f"Bots: <code>{bots}</code>\n"
    if members_online:
        caption += f"Currently online: <code>{members_online}</code>\n"
    if restrcited_users is not None:
        caption += f"Restricted users: <code>{restrcited_users}</code>\n"
    if banned_users is not None:
        caption += f"Banned users: <code>{banned_users}</code>\n"
    if group_stickers is not None:
        caption += f"{chat_type} stickers: <a href=\"t.me/addstickers/{chat.full_chat.stickerset.short_name}\">{group_stickers}</a>\n"
    caption += "\n"
    if not broadcast:
        caption += f"Slow mode: {slowmode}"
        if hasattr(chat_obj_info, "slowmode_enabled") and chat_obj_info.slowmode_enabled:
            caption += f", <code>{slowmode_time}s</code>\n\n"
        else:
            caption += "\n\n"
    if not broadcast:
        caption += f"Supergroup: {supergroup}\n\n"
    if hasattr(chat_obj_info, "restricted"):
        caption += f"Restricted: {restricted}\n"
        if chat_obj_info.restricted:
            caption += f"> Platform: {chat_obj_info.restriction_reason[0].platform}\n"
            caption += f"> Reason: {chat_obj_info.restriction_reason[0].reason}\n"
            caption += f"> Text: {chat_obj_info.restriction_reason[0].text}\n\n"
        else:
            caption += "\n"
    if hasattr(chat_obj_info, "scam") and chat_obj_info.scam:
    	caption += "Scam: <b>Yes</b>\n\n"
    if hasattr(chat_obj_info, "verified"):
        caption += f"Verified by Telegram: {verified}\n\n"
    if description:
        caption += f"Description: \n<code>{description}</code>\n"
    return caption

@ultroid_cmd(
    pattern="kickme$",
    groups_only=True,
)
async def leave(ult):
    x = ultroid_bot.me
    name = x.first_name
    await eor(ult, f"`{name} has left this group, bye!!.`")
    await ultroid_bot(LeaveChannelRequest(ult.chat_id))


@ultroid_cmd(
    pattern="date$",
)
async def date(event):
    k = pytz.timezone("Asia/Kolkata")
    m = dt.now(k).month
    y = dt.now(k).year
    d = dt.now(k).strftime("Date - %B %d, %Y\nTime- %H:%M:%S")
    k = calendar.month(y, m)
    ultroid = await eor(event, f"`{k}\n\n{d}`")


@ultroid_cmd(
    pattern="calc",
)
async def _(event):
    x = await eor(event, "...")
    cmd = event.text.split(" ", maxsplit=1)[1]
    event.message.id
    if event.reply_to_msg_id:
        event.reply_to_msg_id
    wtf = f"print({cmd})"
    old_stderr = sys.stderr
    old_stdout = sys.stdout
    redirected_output = sys.stdout = io.StringIO()
    redirected_error = sys.stderr = io.StringIO()
    stdout, stderr, exc = None, None, None
    try:
        await aexec(wtf, event)
    except Exception:
        exc = traceback.format_exc()
    stdout = redirected_output.getvalue()
    stderr = redirected_error.getvalue()
    sys.stdout = old_stdout
    sys.stderr = old_stderr
    evaluation = ""
    if exc:
        evaluation = exc
    elif stderr:
        evaluation = stderr
    elif stdout:
        evaluation = stdout
    else:
        evaluation = "`Something went wrong`"

    final_output = """
**EQUATION**:
`{}`
**SOLUTION**:
`{}`
""".format(
        cmd, evaluation
    )
    await x.edit(final_output)


async def aexec(code, event):
    exec(f"async def __aexec(event): " + "".join(f"\n {l}" for l in code.split("\n")))
    return await locals()["__aexec"](event)


@ultroid_cmd(
    pattern="chatinfo(?: |$)(.*)",
)
async def info(event):
    ok = await eor(event, "`...`")
    chat = await get_chatinfo(event)
    caption = await miraculous(chat, event)
    try:
        await ok.edit(caption, parse_mode="html")
    except Exception as e:
        print("Exception:", e)
        await ok.edit(f"`An unexpected error has occurred. {e}`")
        await asyncio.sleep(5)
        await ok.delete()
    return


@ultroid_cmd(
    pattern="listreserved$",
)
async def _(event):
    result = await ultroid_bot(functions.channels.GetAdminedPublicChannelsRequest())
    output_str = ""
    r = result.chats
    for channel_obj in r:
        output_str += f"- {channel_obj.title} @{channel_obj.username} \n"
    if not r:
        await eor(event, "`Not username Reserved`")
    else:
        await eor(event, output_str)


@ultroid_cmd(
    pattern="stats$",
)
async def stats(
    event: NewMessage.Event,
) -> None:
    ok = await eor(event, "`Collecting stats...`")
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
    async for dialog in ultroid_bot.iter_dialogs():
        entity = dialog.entity
        if isinstance(entity, Channel):
            if entity.broadcast:
                broadcast_channels += 1
                if entity.creator or entity.admin_rights:
                    admin_in_broadcast_channels += 1
                if entity.creator:
                    creator_in_channels += 1

            elif entity.megagroup:
                groups += 1
                if entity.creator or entity.admin_rights:
                    admin_in_groups += 1
                if entity.creator:
                    creator_in_groups += 1

        elif isinstance(entity, User):
            private_chats += 1
            if entity.bot:
                bots += 1

        elif isinstance(entity, Chat):
            groups += 1
            if entity.creator or entity.admin_rights:
                admin_in_groups += 1
            if entity.creator:
                creator_in_groups += 1

        unread_mentions += dialog.unread_mentions_count
        unread += dialog.unread_count
    stop_time = time.time() - start_time

    full_name = inline_mention(await ultroid_bot.get_me())
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
    response += f"**Unread Mentions:** {unread_mentions} \n\n"
    response += f"**__It Took:__** {stop_time:.02f}s \n"
    await ok.edit(response)


@ultroid_cmd(
    pattern="paste( (.*)|$)",
)
async def _(event):
    xx = await eor(event, "` 《 Pasting to nekobin... 》 `")
    input_str = "".join(event.text.split(maxsplit=1)[1:])
    if input_str:
        message = input_str
        downloaded_file_name = None
    elif event.reply_to_msg_id:
        previous_message = await event.get_reply_message()
        if previous_message.media:
            downloaded_file_name = await event.client.download_media(
                previous_message,
                "./resources/downloads",
            )
            m_list = None
            with open(downloaded_file_name, "rb") as fd:
                m_list = fd.readlines()
            message = ""
            try:
                for m in m_list:
                    message += m.decode("UTF-8")
            except BaseException:
                message = "`Include long text / Reply to text file`"
            os.remove(downloaded_file_name)
        else:
            downloaded_file_name = None
            message = previous_message.message
    else:
        downloaded_file_name = None
        message = "`Include long text / Reply to text file`"
    if downloaded_file_name and downloaded_file_name.endswith(".py"):
        data = message
        key = (
            requests.post("https://nekobin.com/api/documents", json={"content": data})
            .json()
            .get("result")
            .get("key")
        )
    else:
        data = message
        key = (
            requests.post("https://nekobin.com/api/documents", json={"content": data})
            .json()
            .get("result")
            .get("key")
        )
    q = f"paste-{key}"
    reply_text = f"• **Pasted to Nekobin :** [Neko](https://nekobin.com/{key})\n• **Raw Url :** : [Raw](https://nekobin.com/raw/{key})"
    try:
        ok = await ultroid_bot.inline_query(Var.BOT_USERNAME, q)
        await ok[0].click(event.chat_id, reply_to=event.reply_to_msg_id, hide_via=True)
        await xx.delete()
    except BotInlineDisabledError or BotResponseTimeoutError or ChatSendInlineForbiddenError:  # handling possible exceptions
        await xx.edit(reply_text)
    except bmi:
        await xx.edit(
            f"**Inline Not Available as You Are in Bot Mode\nPasted to Nekobin :**\n{reply_text}"
        )


@ultroid_cmd(
    pattern="hastebin ?(.*)",
)
async def _(event):
    input_str = event.pattern_match.group(1)
    xx = await eor(event, "`Pasting...`")
    message = "SYNTAX: `.paste <long text to include>`"
    if input_str:
        message = input_str
    elif event.reply_to_msg_id:
        previous_message = await event.get_reply_message()
        if previous_message.media:
            downloaded_file_name = await event.client.download_media(
                previous_message,
                "./resources/downloads",
            )
            m_list = None
            with open(downloaded_file_name, "rb") as fd:
                m_list = fd.readlines()
            message = ""
            for m in m_list:
                message += m.decode("UTF-8") + "\r\n"
            os.remove(downloaded_file_name)
        else:
            message = previous_message.message
    else:
        message = "SYNTAX: `.hastebin <long text to include>`"
    url = "https://hastebin.com/documents"
    r = requests.post(url, data=message).json()
    url = f"https://hastebin.com/{r['key']}"
    await xx.edit("**Pasted to Hastebin** : [Link]({})".format(url))


@ultroid_cmd(
    pattern="info ?(.*)",
)
async def _(event):
    xx = await eor(event, "`Processing...`")
    replied_user, error_i_a = await get_full_user(event)
    if replied_user is None:
        await xx.edit("Please reply to a user.\nError - " + str(error_i_a))
        return False
    replied_user_profile_photos = await event.client(
        GetUserPhotosRequest(
            user_id=replied_user.user.id, offset=42, max_id=0, limit=80
        )
    )
    replied_user_profile_photos_count = "NaN"
    try:
        replied_user_profile_photos_count = replied_user_profile_photos.count
    except AttributeError:
        pass
    user_id = replied_user.user.id
    first_name = html.escape(replied_user.user.first_name)
    if first_name is not None:
        first_name = first_name.replace("\u2060", "")
    last_name = replied_user.user.last_name
    last_name = (
        last_name.replace("\u2060", "") if last_name else ("Last Name not found")
    )
    user_bio = replied_user.about
    if user_bio is not None:
        user_bio = html.escape(replied_user.about)
    common_chats = replied_user.common_chats_count
    try:
        dc_id, location = get_input_location(replied_user.profile_photo)
    except Exception as e:
        dc_id = "Need a Profile Picture to check this"
        str(e)
    caption = """<b>Exᴛʀᴀᴄᴛᴇᴅ Dᴀᴛᴀʙᴀsᴇ Fʀᴏᴍ Tᴇʟᴇɢʀᴀᴍ's Dᴀᴛᴀʙᴀsᴇ<b>
    <b>••Tᴇʟᴇɢʀᴀᴍ ID</b>: <code>{}</code>
    <b>••Pᴇʀᴍᴀɴᴇɴᴛ Lɪɴᴋ</b>: <a href='tg://user?id={}'>Click Here</a>
    <b>••Fɪʀsᴛ Nᴀᴍᴇ</b>: <code>{}</code>
    <b>••Sᴇᴄᴏɴᴅ Nᴀᴍᴇ</b>: <code>{}</code>
    <b>••Bɪᴏ</b>: <code>{}</code>
    <b>••Dᴄ ID</b>: <code>{}</code>
    <b>••Nᴏ. Oғ PғPs</b> : <code>{}</code>
    <b>••Is Rᴇsᴛʀɪᴄᴛᴇᴅ</b>: <code>{}</code>
    <b>••Vᴇʀɪғɪᴇᴅ</b>: <code>{}</code>
    <b>••Is A Bᴏᴛ</b>: <code>{}</code>
    <b>••Gʀᴏᴜᴘs Iɴ Cᴏᴍᴍᴏɴ</b>: <code>{}</code>
    """.format(
        user_id,
        user_id,
        first_name,
        last_name,
        user_bio,
        dc_id,
        replied_user_profile_photos_count,
        replied_user.user.restricted,
        replied_user.user.verified,
        replied_user.user.bot,
        common_chats,
    )
    message_id_to_reply = event.message.reply_to_msg_id
    if not message_id_to_reply:
        message_id_to_reply = event.message.id
    await event.client.send_message(
        event.chat_id,
        caption,
        reply_to=message_id_to_reply,
        parse_mode="HTML",
        file=replied_user.profile_photo,
        force_document=False,
        silent=True,
    )
    await xx.delete()


@ultroid_cmd(
    pattern="invite ?(.*)",
    groups_only=True,
)
async def _(ult):
    xx = await eor(ult, "`Processing...`")
    to_add_users = ult.pattern_match.group(1)
    if not ult.is_channel and ult.is_group:
        for user_id in to_add_users.split(" "):
            try:
                await ultroid_bot(
                    functions.messages.AddChatUserRequest(
                        chat_id=ult.chat_id, user_id=user_id, fwd_limit=1000000
                    )
                )
                await xx.edit(f"Successfully invited `{user_id}` to `{ult.chat_id}`")
            except Exception as e:
                await xx.edit(str(e))
    else:
        for user_id in to_add_users.split(" "):
            try:
                await ultroid_bot(
                    functions.channels.InviteToChannelRequest(
                        channel=ult.chat_id, users=[user_id]
                    )
                )
                await xx.edit(f"Successfully invited `{user_id}` to `{ult.chat_id}`")
            except Exception as e:
                await xx.edit(str(e))


@ultroid_cmd(
    pattern=r"rmbg$",
)
async def rmbg(event):
    RMBG_API = udB.get("RMBG_API")
    xx = await eor(event, "`Processing...`")
    if not RMBG_API:
        return await xx.edit(
            "Get your API key from [here](https://www.remove.bg/) for this plugin to work.",
        )
    if event.reply_to_msg_id:
        reply = await event.get_reply_message()
        dl = await ultroid_bot.download_media(reply)
        if not dl.endswith(("webp", "jpg", "png", "jpeg")):
            os.remove(dl)
            return await xx.edit("`Unsupported Media`")
        await xx.edit("`Sending to remove.bg`")
        out = ReTrieveFile("ult.png")
        os.remove("ult.png")
        os.remove(dl)
    else:
        await xx.edit(f"Use `{HNDLR}rmbg` as reply to a pic to remove its background.")
        await asyncio.sleep(5)
        await xx.delete()
        return
    contentType = out.headers.get("content-type")
    rmbgp = "ult.png"
    if "image" in contentType:
        with open(rmbgp, "wb") as rmbg:
            rmbg.write(out.content)
    else:
        error = out.json()
        await xx.edit(
            f"**Error ~** `{error['errors'][0]['title']}`,\n`{error['errors'][0]['detail']}`"
        )
    zz = Image.open(rmbgp)
    if zz.mode != "RGB":
        zz.convert("RGB")
    zz.save("ult.webp", "webp")
    await ultroid_bot.send_file(
        event.chat_id, rmbgp, force_document=True, reply_to=reply
    )
    await ultroid_bot.send_file(event.chat_id, "ult.webp", reply_to=reply)
    os.remove(rmbgp)
    os.remove("ult.webp")
    await xx.delete()


@ultroid_cmd(
    pattern="telegraph ?(.*)",
)
async def telegraphcmd(event):
    input_str = event.pattern_match.group(1)
    xx = await eor(event, "`Processing...`")
    if event.reply_to_msg_id:
        getmsg = await event.get_reply_message()
        if getmsg.photo or getmsg.video or getmsg.gif:
            getit = await ultroid_bot.download_media(getmsg)
            try:
                variable = uf(getit)
                os.remove(getit)
                nn = "https://telegra.ph" + variable[0]
                amsg = f"Uploaded to [Telegraph]({nn}) !"
            except Exception as e:
                amsg = f"Error - {e}"
            await xx.edit(amsg)
        elif getmsg.document:
            getit = await ultroid_bot.download_media(getmsg)
            ab = open(getit, "r")
            cd = ab.read()
            ab.close()
            if input_str:
                tcom = input_str
            else:
                tcom = "Ultroid"
            makeit = telegraph.create_page(title=tcom, content=[f"{cd}"])
            war = makeit["url"]
            os.remove(getit)
            await xx.edit(f"Pasted to Telegraph : [Telegraph]({war})")
        elif getmsg.text:
            if input_str:
                tcom = input_str
            else:
                tcom = "Ultroid"
            makeit = telegraph.create_page(title=tcom, content=[f"{getmsg.text}"])
            war = makeit["url"]
            await xx.edit(f"Pasted to Telegraph : [Telegraph]({war})")
        else:
            await xx.edit("Reply to a Media or Text !")
    else:
        await xx.edit("Reply to a Message !")


@ultroid_cmd(pattern="json")
async def _(event):
    the_real_message = None
    reply_to_id = None
    if event.reply_to_msg_id:
        previous_message = await event.get_reply_message()
        the_real_message = previous_message.stringify()
        reply_to_id = event.reply_to_msg_id
    else:
        the_real_message = event.stringify()
        reply_to_id = event.message.id
    if len(the_real_message) > 4096:
        with io.BytesIO(str.encode(the_real_message)) as out_file:
            out_file.name = "json-ult.txt"
            await ultroid_bot.send_file(
                event.chat_id,
                out_file,
                force_document=True,
                allow_cache=False,
                reply_to=reply_to_id,
            )
            await event.delete()
    else:
        await eor(event, f"```{the_real_message}```")


@ultroid_cmd(pattern="suggest")
async def sugg(event):
    if await event.get_reply_message():
        msgid = (await event.get_reply_message()).id
        try:
            await ultroid.send_message(
                event.chat_id,
                file=InputMediaPoll(
                    poll=Poll(
                        id=12345,
                        question="Do you agree to the replied suggestion?",
                        answers=[PollAnswer("Yes", b"1"), PollAnswer("No", b"2")],
                    )
                ),
                reply_to=msgid,
            )
        except Exception as e:
            return await eod(
                event, f"`Oops, you can't send polls here!\n\n{str(e)}`", time=5
            )
        await event.delete()
    else:
        return await eod(
            event, "`Please reply to a message to make a suggestion poll!`", time=5
        )


HELP.update({f"{__name__.split('.')[1]}": f"{__doc__.format(i=HNDLR)}"})
