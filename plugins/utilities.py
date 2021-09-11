# Ultroid - UserBot
# Copyright (C) 2021 TeamUltroid
#
# This file is a part of < https://github.com/TeamUltroid/Ultroid/ >
# PLease read the GNU Affero General Public License in
# <https://www.github.com/TeamUltroid/Ultroid/blob/main/LICENSE/>.
"""
✘ Commands Available -

• `{i}kickme`
    Leaves the group in which it is used.

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

• `{i}suggest <reply to message> or <poll title>`
    Create a Yes/No poll for the replied suggestion.

• `{i}ipinfo <ip address>`
    Get info about that IP address.

• `{i}cpy <reply to message>`
   Copy the replied message, with formatting. Expires in 24hrs.

• `{i}pst`
   Paste the copied message, with formatting.

• `{i}thumb <reply to file>`
   Download the thumbnail of the replied file.
"""
import calendar
import html
import io
import os
import time
from datetime import datetime as dt

import requests
from pyUltroid.functions.gban_mute_db import *
from telegraph import Telegraph
from telegraph import upload_file as uf
from telethon.events import NewMessage
from telethon.tl.custom import Dialog
from telethon.tl.functions.channels import (
    GetAdminedPublicChannelsRequest,
    InviteToChannelRequest,
    LeaveChannelRequest,
)
from telethon.tl.functions.contacts import GetBlockedRequest
from telethon.tl.functions.messages import AddChatUserRequest, GetAllStickersRequest
from telethon.tl.functions.photos import GetUserPhotosRequest
from telethon.tl.types import Channel, Chat, InputMediaPoll, Poll, PollAnswer, User
from telethon.utils import get_input_location

from . import *

# =================================================================#

TMP_DOWNLOAD_DIRECTORY = "resources/downloads/"

# Telegraph Things
telegraph = Telegraph()
try:
    telegraph.create_account(short_name=OWNER_NAME)

except BaseException:
    telegraph.create_account(short_name="Ultroid")

_copied_msg = {}


@ultroid_cmd(pattern="kickme$", fullsudo=True)
async def leave(ult):
    me = asst.me if ult.client._bot else ultroid_bot.me
    await eor(ult, f"`{me.first_name} has left this group, bye!!.`")
    await ult.client(LeaveChannelRequest(ult.chat_id))


@ultroid_cmd(
    pattern="date$",
)
async def date(event):
    m = dt.now().month
    y = dt.now().year
    d = dt.now().strftime("Date - %B %d, %Y\nTime- %H:%M:%S")
    k = calendar.month(y, m)
    ultroid = await eor(event, f"`{k}\n\n{d}`")


@ultroid_cmd(
    pattern="chatinfo(?: |$)(.*)",
)
async def info(event):
    ok = await eor(event, get_string("com_1"))
    try:
        chat = await get_chatinfo(event)
        caption = await fetch_info(chat, event)
        await ok.edit(caption, parse_mode="html")
    except Exception as e:
        LOGS.info(e)
        await eor(ok, f"`An unexpected error has occurred. {e}`", time=5)
    return


@ultroid_cmd(
    pattern="listreserved$",
)
async def _(event):
    result = await event.client(GetAdminedPublicChannelsRequest())
    r = result.chats
    output_str = "".join(
        f"- {channel_obj.title} @{channel_obj.username} \n" for channel_obj in r
    )
    if not r:
        return await eor(event, "`No username Reserved`")
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
    async for dialog in event.client.iter_dialogs():
        entity = dialog.entity
        if isinstance(entity, Channel) and entity.broadcast:
            broadcast_channels += 1
            if entity.creator or entity.admin_rights:
                admin_in_broadcast_channels += 1
            if entity.creator:
                creator_in_channels += 1

        elif (
            isinstance(entity, Channel)
            and entity.megagroup
            or not isinstance(entity, Channel)
            and not isinstance(entity, User)
            and isinstance(entity, Chat)
        ):
            groups += 1
            if entity.creator or entity.admin_rights:
                admin_in_groups += 1
            if entity.creator:
                creator_in_groups += 1

        elif not isinstance(entity, Channel) and isinstance(entity, User):
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
        sp = await ultroid_bot(GetAllStickersRequest(0))
        sp_count = len(sp.sets)
    except BaseException:
        sp_count = 0
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
    response += f"**Unread Mentions:** {unread_mentions} \n"
    response += f"**Blocked Users:** {ct}\n"
    response += f"**Total Stickers Pack Installed :** `{sp_count}`\n\n"
    response += f"**__It Took:__** {stop_time:.02f}s \n"
    await ok.edit(response)


@ultroid_cmd(pattern="paste( (.*)|$)", type=["official", "manager"])
async def _(event):
    xx = await eor(event, "` 《 Pasting... 》 `")
    input_str = "".join(event.text.split(maxsplit=1)[1:])
    if not (input_str or event.is_reply):
        return await xx.edit("`Reply to a Message/Document or Give me Some Text !`")
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
            message = previous_message.message
    done, key = await get_paste(message)
    if not done:
        return await eor(xx, key)
    link = "https://spaceb.in/" + key
    raw = f"https://spaceb.in/api/v1/documents/{key}/raw"
    reply_text = (
        f"• **Pasted to SpaceBin :** [Space]({link})\n• **Raw Url :** : [Raw]({raw})"
    )
    try:
        if event.client._bot:
            return await eor(xx, reply_text)
        ok = await event.client.inline_query(asst.me.username, "pasta-" + key)
        await ok[0].click(event.chat_id, reply_to=event.reply_to_msg_id, hide_via=True)
        await xx.delete()
    except BaseException as e:
        LOGS.info(e)
        await xx.edit(reply_text)


@ultroid_cmd(
    pattern="info ?(.*)",
    type=["official", "manager"],
)
async def _(event):
    xx = await eor(event, "`Processing...`")
    replied_user, error_i_a = await get_full_user(event)
    if replied_user is None:
        await xx.edit("Please reply to a user.\nError - " + str(error_i_a))
        return False
    replied_user_profile_photos = await event.client(
        GetUserPhotosRequest(
            user_id=replied_user.user.id,
            offset=42,
            max_id=0,
            limit=80,
        ),
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
    chk = is_gbanned(user_id)
    if chk:
        r = get_gban_reason(user_id)
        caption += "<b>••Gʟᴏʙᴀʟʟʏ Bᴀɴɴᴇᴅ</b>: <code>True</code>"
        if r:
            caption += f"<b>Rᴇᴀsᴏɴ</b>: <code>{r}</code>"
    else:
        caption += "<b>••Gʟᴏʙᴀʟʟʏ Bᴀɴɴᴇᴅ</b>: <code>False</code>"
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
    xx = await eor(ult, get_string("com_1"))
    to_add_users = ult.pattern_match.group(1)
    if not ult.is_channel and ult.is_group:
        for user_id in to_add_users.split(" "):
            try:
                await ult.client(
                    AddChatUserRequest(
                        chat_id=ult.chat_id,
                        user_id=user_id,
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
                        users=[user_id],
                    ),
                )
                await xx.edit(f"Successfully invited `{user_id}` to `{ult.chat_id}`")
            except Exception as e:
                await xx.edit(str(e))


@ultroid_cmd(
    pattern=r"rmbg$",
)
async def rmbg(event):
    RMBG_API = udB.get("RMBG_API")
    if not RMBG_API:
        return await eor(
            event,
            "Get your API key from [here](https://www.remove.bg/) for this plugin to work.",
        )
    if event.reply_to_msg_id:
        reply = await event.get_reply_message()
        dl = await event.client.download_media(reply.media)
        if not dl.endswith(("webp", "jpg", "png", "jpeg")):
            os.remove(dl)
            return await eor(event, "`Unsupported Media`")
        xx = await eor(event, "`Sending to remove.bg`")
        out = ReTrieveFile(dl)
        os.remove(dl)
    else:
        return await eod(
            event, f"Use `{HNDLR}rmbg` as reply to a pic to remove its background."
        )
    contentType = out.headers.get("content-type")
    rmbgp = "ult.png"
    if "image" in contentType:
        with open(rmbgp, "wb") as rmbg:
            rmbg.write(out.content)
    else:
        error = out.json()
        await xx.edit(
            f"**Error ~** `{error['errors'][0]['title']}`,\n`{error['errors'][0]['detail']}`",
        )
    zz = Image.open(rmbgp)
    if zz.mode != "RGB":
        zz.convert("RGB")
    zz.save("ult.webp", "webp")
    await event.client.send_file(
        event.chat_id,
        rmbgp,
        force_document=True,
        reply_to=reply,
    )
    await event.client.send_file(event.chat_id, "ult.webp", reply_to=reply)
    os.remove(rmbgp)
    os.remove("ult.webp")
    await xx.delete()


@ultroid_cmd(
    pattern="telegraph ?(.*)",
)
async def telegraphcmd(event):
    match = event.pattern_match.group(1) or "Ultroid"
    reply = await event.get_reply_message()
    if not reply:
        return await eor(event, "`Reply to Message.`")
    if not reply.media and reply.message:
        content = reply.message
    else:
        getit = await reply.download_media()
        dar = mediainfo(reply.media)
        if dar == "sticker":
            os.rename(getit, getit + ".jpg")
            getit = getit + ".jpg"
        if "document" not in dar:
            try:
                nn = "https://telegra.ph" + uf(getit)[0]
                amsg = f"Uploaded to [Telegraph]({nn}) !"
            except Exception as e:
                amsg = f"Error : {e}"
            os.remove(getit)
            return await eor(event, amsg)
        with open(getit) as ab:
            content = ab.read()
        os.remove(getit)
    makeit = telegraph.create_page(title=match, content=[content])
    war = makeit["url"]
    await eor(event, f"Pasted to Telegraph : [Telegraph]({war})")


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
            await event.client.send_file(
                event.chat_id,
                out_file,
                force_document=True,
                allow_cache=False,
                reply_to=reply_to_id,
            )
            await event.delete()
    else:
        await eor(event, f"```{the_real_message}```")


@ultroid_cmd(pattern="suggest", type=["official", "manager"])
async def sugg(event):
    sll = event.text.split(" ", maxsplit=1)
    try:
        text = sll[1]
    except IndexError:
        text = None
    if event.is_reply:
        text = "Do you Agree to Replied Suggestion ?"
        cevent = await event.get_reply_message()
    elif text:
        cevent = event
    else:
        return await eod(
            event,
            "`Please reply to a message to make a suggestion poll!`",
        )
    try:
        await cevent.reply(
            file=InputMediaPoll(
                poll=Poll(
                    id=12345,
                    question=text,
                    answers=[PollAnswer("Yes", b"1"), PollAnswer("No", b"2")],
                ),
            ),
        )
    except Exception as e:
        return await eod(
            event,
            f"`Oops, you can't send polls here!\n\n{str(e)}`",
        )
    await event.delete()


@ultroid_cmd(pattern="ipinfo ?(.*)")
async def ipinfo(event):
    ip = event.text.split(" ")
    ipaddr = ""
    try:
        ipaddr = "/" + ip[1]
    except IndexError:
        ipaddr = ""
    url = f"https://ipinfo.io{ipaddr}/geo"
    det = requests.get(url).json()
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
        await eor(event, f"ERROR:\n{err}\n{msg}", time=5)


@ultroid_cmd(
    pattern="cpy$",
)
async def copp(event):
    msg = await event.get_reply_message()
    if not msg:
        return await eor(event, f"Use `{hndlr}cpy` as reply to a message!", time=5)
    _copied_msg["CLIPBOARD"] = msg
    await eor(event, f"Copied. Use `{hndlr}pst` to paste!", time=10)


@asst_cmd("pst")
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
        try:
            await event.delete()
        except BaseException:
            pass
    except KeyError:
        return await eod(
            event,
            f"Nothing was copied! Use `{hndlr}cpy` as reply to a message first!",
        )
    except Exception as ex:
        return await eor(event, str(ex), time=5)


@ultroid_cmd(pattern="thumb$")
async def thumb_dl(event):
    if not event.reply_to_msg_id:
        return await eod(
            event, "`Please reply to a file to download its thumbnail!`", time=5
        )
    xx = await eor(event, get_string("com_1"))
    x = await event.get_reply_message()
    m = await event.client.download_media(x, thumb=-1)
    await event.reply(file=m)
    await eor(xx, "`Thumbnail sent, if available.`", time=5)
