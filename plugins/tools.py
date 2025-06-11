# Ultroid - UserBot
# Copyright (C) 2021-2025 TeamUltroid
#
# This file is a part of < https://github.com/TeamUltroid/Ultroid/ >
# PLease read the GNU Affero General Public License in
# <https://www.github.com/TeamUltroid/Ultroid/blob/main/LICENSE/>.
"""
✘ Commands Available -

• `{i}circle`
    Reply to a audio song or gif to get video note.

• `{i}ls`
    Get all the Files inside a Directory.

• `{i}bots`
    Shows the number of bots in the current chat with their perma-link.

• `{i}hl <a link> <text-optional>`
    Embeds the link with a whitespace as message.

• `{i}id`
    Reply a Sticker to Get Its Id
    Reply a User to Get His Id
    Without Replying You Will Get the Chat's Id

• `{i}sg <reply to a user><username/id>`
    Get His Name History of the replied user.

• `{i}tr <dest lang code> <(reply to) a message>`
    Get translated message.

• `{i}webshot <url>`
    Get a screenshot of the webpage.
"""
import glob
import io
import os
import secrets, time, re, asyncio
from telethon.tl import types, functions
from datetime import datetime as dt, timedelta
from asyncio.exceptions import TimeoutError as AsyncTimeout
from telethon.utils import get_display_name
from telethon.tl.functions.contacts import UnblockRequest

try:
    import cv2
except ImportError:
    cv2 = None

try:
    from playwright.async_api import async_playwright
except ImportError:
    async_playwright = None
try:
    from htmlwebshot import WebShot
except ImportError:
    WebShot = None

from telethon.errors.rpcerrorlist import MessageTooLongError, YouBlockedUserError
from telethon.tl.types import (
    ChannelParticipantAdmin,
    ChannelParticipantsBots,
    DocumentAttributeVideo,
)

from pyUltroid.fns.tools import metadata, translate

from aiohttp.client_exceptions import InvalidURL
from telethon.errors.rpcerrorlist import MessageNotModifiedError

from pyUltroid.fns.helper import time_formatter
from pyUltroid.fns.tools import get_chat_and_msgid, set_attributes

from . import (
    LOGS,
    ULTConfig,
    downloader,
    eor,
    fast_download,
    get_all_files,
    get_string,
    progress,
    time_formatter,
    ultroid_cmd,
)

from . import (
    HNDLR,
    LOGS,
    ULTConfig,
    async_searcher,
    bash,
    check_filename,
    con,
    download_file,
    eor,
    get_string,
)
from . import humanbytes as hb
from . import inline_mention, is_url_ok, json_parser, mediainfo, ultroid_cmd


@ultroid_cmd(pattern="tr( (.*)|$)", manager=True)
async def _(event):
    input = event.pattern_match.group(1).strip().split(maxsplit=1)
    txt = input[1] if len(input) > 1 else None
    if input:
        input = input[0]
    if txt:
        text = txt
    elif event.is_reply:
        previous_message = await event.get_reply_message()
        text = previous_message.message
    else:
        return await eor(
            event, f"`{HNDLR}tr LanguageCode` as reply to a message", time=5
        )
    lan = input or "en"
    try:
        tt = translate(text, lang_tgt=lan)
        output_str = f"**TRANSLATED** to {lan}\n{tt}"
        await event.eor(output_str)
    except Exception as exc:
        LOGS.exception(exc)
        await event.eor(str(exc), time=5)


@ultroid_cmd(
    pattern="id( (.*)|$)",
    manager=True,
)
async def _(event):
    ult = event
    match = event.pattern_match.group(1).strip()
    if match:
        try:
            ids = await event.client.parse_id(match)
        except Exception as er:
            return await event.eor(str(er))
        return await event.eor(
            f"**Chat ID:**  `{event.chat_id}`\n**User ID:**  `{ids}`"
        )
    data = f"**Current Chat ID:**  `{event.chat_id}`"
    if event.reply_to_msg_id:
        event = await event.get_reply_message()
        data += f"\n**From User ID:**  `{event.sender_id}`"
    if event.media:
        bot_api_file_id = event.file.id
        data += f"\n**Bot API File ID:**  `{bot_api_file_id}`"
    data += f"\n**Msg ID:**  `{event.id}`"
    await ult.eor(data)


@ultroid_cmd(pattern="bots( (.*)|$)", groups_only=True, manager=True)
async def _(ult):
    mentions = "• **Bots in this Chat**: \n"
    if input_str := ult.pattern_match.group(1).strip():
        mentions = f"• **Bots in **{input_str}: \n"
        try:
            chat = await ult.client.parse_id(input_str)
        except Exception as e:
            return await ult.eor(str(e))
    else:
        chat = ult.chat_id
    try:
        async for x in ult.client.iter_participants(
            chat,
            filter=ChannelParticipantsBots,
        ):
            if isinstance(x.participant, ChannelParticipantAdmin):
                mentions += f"\n⚜️ {inline_mention(x)} `{x.id}`"
            else:
                mentions += f"\n• {inline_mention(x)} `{x.id}`"
    except Exception as e:
        mentions += f" {str(e)}" + "\n"
    await ult.eor(mentions)


@ultroid_cmd(
    pattern="hl( (.*)|$)",
)
async def _(ult):
    input_ = ult.pattern_match.group(1).strip()
    if not input_:
        return await ult.eor("`Input some link`", time=5)
    text = None
    if len(input_.split()) > 1:
        spli_ = input_.split()
        input_ = spli_[0]
        text = spli_[1]
    if not text:
        text = "ㅤㅤㅤㅤㅤㅤㅤ"
    await ult.eor(f"[{text}]({input_})", link_preview=False)


@ultroid_cmd(
    pattern="circle$",
)
async def _(e):
    reply = await e.get_reply_message()
    if not (reply and reply.media):
        return await e.eor("`Reply to a gif or audio file only.`")
    if "audio" in mediainfo(reply.media):
        msg = await e.eor("`Downloading...`")
        try:
            bbbb = await reply.download_media(thumb=-1)
        except TypeError:
            bbbb = ULTConfig.thumb
        im = cv2.imread(bbbb)
        dsize = (512, 512)
        output = cv2.resize(im, dsize, interpolation=cv2.INTER_AREA)
        cv2.imwrite("img.jpg", output)
        thumb = "img.jpg"
        audio, _ = await e.client.fast_downloader(reply.document)
        await msg.edit("`Creating video note...`")
        await bash(
            f'ffmpeg -i "{thumb}" -i "{audio.name}" -preset ultrafast -c:a libmp3lame -ab 64 circle.mp4 -y'
        )
        await msg.edit("`Uploading...`")
        data = await metadata("circle.mp4")
        file, _ = await e.client.fast_uploader("circle.mp4", to_delete=True)
        await e.client.send_file(
            e.chat_id,
            file,
            thumb=thumb,
            reply_to=reply,
            attributes=[
                DocumentAttributeVideo(
                    duration=min(data["duration"], 60),
                    w=512,
                    h=512,
                    round_message=True,
                )
            ],
        )

        await msg.delete()
        [os.remove(k) for k in [audio.name, thumb]]
    elif mediainfo(reply.media) == "gif" or mediainfo(reply.media).startswith("video"):
        msg = await e.eor("**Creating video note**")
        file = await reply.download_media("resources/downloads/")
        if file.endswith(".webm"):
            nfile = await con.ffmpeg_convert(file, "file.mp4")
            os.remove(file)
            file = nfile
        if file:
            await e.client.send_file(
                e.chat_id,
                file,
                video_note=True,
                thumb=ULTConfig.thumb,
                reply_to=reply,
            )
            os.remove(file)
        await msg.delete()

    else:
        await e.eor("`Reply to a gif or audio file only.`")


FilesEMOJI = {
    "py": "🐍",
    "json": "🔮",
    ("sh", "bat"): "⌨️",
    (".mkv", ".mp4", ".avi", ".gif", "webm"): "🎥",
    (".mp3", ".ogg", ".m4a", ".opus"): "🔊",
    (".jpg", ".jpeg", ".png", ".webp", ".ico"): "🖼",
    (".txt", ".text", ".log"): "📄",
    (".apk", ".xapk"): "📲",
    (".pdf", ".epub"): "📗",
    (".zip", ".rar"): "🗜",
    (".exe", ".iso"): "⚙",
}


@ultroid_cmd(
    pattern="ls( (.*)|$)",
)
async def _(e):
    files = e.pattern_match.group(1).strip()
    if not files:
        files = "*"
    elif files.endswith("/"):
        files += "*"
    elif "*" not in files:
        files += "/*"
    files = glob.glob(files)
    if not files:
        return await e.eor("`Directory Empty or Incorrect.`", time=5)
    folders = []
    allfiles = []
    for file in sorted(files):
        if os.path.isdir(file):
            folders.append(f"📂 {file}")
        else:
            for ext in FilesEMOJI.keys():
                if file.endswith(ext):
                    allfiles.append(f"{FilesEMOJI[ext]} {file}")
                    break
            else:
                if "." in str(file)[1:]:
                    allfiles.append(f"🏷 {file}")
                else:
                    allfiles.append(f"📒 {file}")
    omk = [*sorted(folders), *sorted(allfiles)]
    text = ""
    fls, fos = 0, 0
    flc, foc = 0, 0
    for i in omk:
        try:
            emoji = i.split()[0]
            name = i.split(maxsplit=1)[1]
            nam = name.split("/")[-1]
            if os.path.isdir(name):
                size = 0
                for path, dirs, files in os.walk(name):
                    for f in files:
                        fp = os.path.join(path, f)
                        size += os.path.getsize(fp)
                if hb(size):
                    text += f"{emoji} `{nam}`  `{hb(size)}" + "`\n"
                    fos += size
                else:
                    text += f"{emoji} `{nam}`" + "\n"
                foc += 1
            else:
                if hb(int(os.path.getsize(name))):
                    text += (
                        emoji
                        + f" `{nam}`"
                        + "  `"
                        + hb(int(os.path.getsize(name)))
                        + "`\n"
                    )
                    fls += int(os.path.getsize(name))
                else:
                    text += f"{emoji} `{nam}`" + "\n"
                flc += 1
        except BaseException:
            pass
    tfos, tfls, ttol = hb(fos), hb(fls), hb(fos + fls)
    if not hb(fos):
        tfos = "0 B"
    if not hb(fls):
        tfls = "0 B"
    if not hb(fos + fls):
        ttol = "0 B"
    text += f"\n\n`Folders` :  `{foc}` :   `{tfos}`\n`Files` :       `{flc}` :   `{tfls}`\n`Total` :       `{flc+foc}` :   `{ttol}`"
    try:
        if (flc + foc) > 100:
            text = text.replace("`", "")
        await e.eor(text)
    except MessageTooLongError:
        with io.BytesIO(str.encode(text)) as out_file:
            out_file.name = "output.txt"
            await e.reply(f"`{e.text}`", file=out_file, thumb=ULTConfig.thumb)
        await e.delete()



def sanga_seperator(sanga_list):
    string = "".join(info[info.find("\n") + 1 :] for info in sanga_list)
    string = re.sub(r"^$\n", "", string, flags=re.MULTILINE)
    name, username = string.split("Usernames**")
    name = name.split("Names")[1]
    return name, username


def mentionuser(name, userid):
    return f"[{name}](tg://user?id={userid})"


@ultroid_cmd(
    pattern="sg(|u)(?:\\s|$)([\\s\\S]*)",
    fullsudo=True,
)
async def sangmata(event):
    "To get name/username history."
    cmd = event.pattern_match.group(1)
    user = event.pattern_match.group(2)
    reply = await event.get_reply_message()
    if not user and reply:
        user = str(reply.sender_id)
    if not user:
        await event.edit(
            "`Reply to  user's text message to get name/username history or give userid/username`",
        )
        await asyncio.sleep(10)
        return await event.delete()

    try:
        if user.isdigit():
            userinfo = await event.client.get_entity(int(user))
        else:
            userinfo = await event.client.get_entity(user)
    except ValueError:
        userinfo = None
    if not isinstance(userinfo, types.User):
        await event.edit("`Can't fetch the user...`")
        await asyncio.sleep(10)
        return await event.delete()

    await event.edit("`Processing...`")
    async with event.client.conversation("@SangMata_beta_bot") as conv:
        try:
            await conv.send_message(f"{userinfo.id}")
        except YouBlockedUserError:
            await event.client(UnblockRequest("SangMata_beta_bot"))
            await conv.send_message(f"{userinfo.id}")
        responses = []
        while True:
            try:
                response = await conv.get_response(timeout=2)
            except asyncio.TimeoutError:
                break
            responses.append(response.text)
        await event.client.send_read_acknowledge(conv.chat_id)

    if not responses:
        await event.edit("`Bot can't fetch results`")
        await asyncio.sleep(10)
        await event.delete()
    if "No records found" in responses or "No data available" in responses:
        await event.edit("`The user doesn't have any record`")
        await asyncio.sleep(10)
        await event.delete()

    names, usernames = sanga_seperator(responses)
    check = (usernames, "Username") if cmd == "u" else (names, "Name")
    user_name = (
        f"{userinfo.first_name} {userinfo.last_name}"
        if userinfo.last_name
        else userinfo.first_name
    )
    output = f"**➜ User Info :**  {mentionuser(user_name, userinfo.id)}\n**➜ {check[1]} History :**\n{check[0]}"
    await event.edit(output)


@ultroid_cmd(pattern="webshot( (.*)|$)")
async def webss(event):
    xx = await event.eor(get_string("com_1"))
    xurl = event.pattern_match.group(1).strip()
    if not xurl:
        return await xx.eor(get_string("wbs_1"), time=5)
    if not (await is_url_ok(xurl)):
        return await xx.eor(get_string("wbs_2"), time=5)
    path, pic = check_filename("shot.png"), None
    if async_playwright:
        try:
            async with async_playwright() as playwright:
                chrome = await playwright.chromium.launch()
                page = await chrome.new_page()
                await page.goto(xurl)
                await page.screenshot(path=path, full_page=True)
                pic = path
        except Exception as er:
            LOGS.exception(er)
            await xx.respond(f"Error with playwright:\n`{er}`")
    if WebShot and not pic:
        try:
            shot = WebShot(
                quality=88, flags=["--enable-javascript", "--no-stop-slow-scripts"]
            )
            pic = await shot.create_pic_async(url=xurl)
        except Exception as er:
            LOGS.exception(er)
    if not pic:
        pic, msg = await download_file(
            f"https://shot.screenshotapi.net/screenshot?&url={xurl}&output=image&file_type=png&wait_for_event=load",
            path,
            validate=True,
        )
        if msg:
            await xx.edit(json_parser(msg, indent=1))
            return
    if pic:
        await xx.reply(
            get_string("wbs_3").format(xurl),
            file=pic,
            link_preview=False,
            force_document=True,
        )
        os.remove(pic)
    await xx.delete()




@ultroid_cmd(
    pattern="dl( (.*)|$)",
)
async def download(event):
    match = event.pattern_match.group(1).strip()
    xx = await event.eor(get_string("com_1"))
    
    # Handle web links
    if match and ("http://" in match or "https://" in match):
        try:
            splited = match.split(" | ")
            link = splited[0]
            filename = splited[1] if len(splited) > 1 else None
            s_time = time.time()
            try:
                filename, d = await fast_download(
                    link,
                    filename,
                    progress_callback=lambda d, t: asyncio.get_event_loop().create_task(
                        progress(
                            d,
                            t,
                            xx,
                            s_time,
                            f"Downloading from {link}",
                        )
                    ),
                )
            except InvalidURL:
                return await xx.eor("`Invalid URL provided :(`", time=5)
            return await xx.eor(f"`{filename}` `downloaded in {time_formatter(d*1000)}.`")
        except Exception as e:
            LOGS.exception(e)
            return await xx.eor(f"`Error: {str(e)}`", time=5)
    
    # Handle Telegram links
    if match and "t.me/" in match:
        chat, msg = get_chat_and_msgid(match)
        if not (chat and msg):
            return await xx.eor(get_string("gms_1"))
        match = ""
        ok = await event.client.get_messages(chat, ids=msg)
    elif event.reply_to_msg_id:
        ok = await event.get_reply_message()
    else:
        return await xx.eor(get_string("cvt_3"), time=8)

    if not (ok and ok.media):
        return await xx.eor(get_string("udl_1"), time=5)
    
    s = dt.now()
    k = time.time()
    if hasattr(ok.media, "document"):
        file = ok.media.document
        mime_type = file.mime_type
        filename = match or ok.file.name
        if not filename:
            if "audio" in mime_type:
                filename = "audio_" + dt.now().isoformat("_", "seconds") + ".ogg"
            elif "video" in mime_type:
                filename = "video_" + dt.now().isoformat("_", "seconds") + ".mp4"
        try:
            result = await downloader(
                f"resources/downloads/{filename}",
                file,
                xx,
                k,
                f"Downloading {filename}...",
            )
        except MessageNotModifiedError as err:
            return await xx.edit(str(err))
        file_name = result.name
    else:
        d = "resources/downloads/"
        file_name = await event.client.download_media(
            ok,
            d,
            progress_callback=lambda d, t: asyncio.get_event_loop().create_task(
                progress(
                    d,
                    t,
                    xx,
                    k,
                    get_string("com_5"),
                ),
            ),
        )
    e = dt.now()
    t = time_formatter(((e - s).seconds) * 1000)
    await xx.eor(get_string("udl_2").format(file_name, t))


@ultroid_cmd(
    pattern="ul( (.*)|$)",
)
async def _(event):
    msg = await event.eor(get_string("com_1"))
    match = event.pattern_match.group(1)
    if match:
        match = match.strip()
    if not event.out and match == ".env":
        return await event.reply("`You can't do this...`")
    stream, force_doc, delete, thumb = (
        False,
        True,
        False,
        ULTConfig.thumb,
    )
    if "--stream" in match:
        stream = True
        force_doc = False
    if "--delete" in match:
        delete = True
    if "--no-thumb" in match:
        thumb = None
    arguments = ["--stream", "--delete", "--no-thumb"]
    if any(item in match for item in arguments):
        match = (
            match.replace("--stream", "")
            .replace("--delete", "")
            .replace("--no-thumb", "")
            .strip()
        )
    if match.endswith("/"):
        match += "*"
    results = glob.glob(match)
    if not results and os.path.exists(match):
        results = [match]
    if not results:
        try:
            await event.reply(file=match)
            return await event.try_delete()
        except Exception as er:
            LOGS.exception(er)
        return await msg.eor(get_string("ls1"))
    for result in results:
        if os.path.isdir(result):
            c, s = 0, 0
            for files in get_all_files(result):
                attributes = None
                if stream:
                    try:
                        attributes = await set_attributes(files)
                    except KeyError as er:
                        LOGS.exception(er)
                try:
                    file, _ = await event.client.fast_uploader(
                        files, show_progress=True, event=msg, to_delete=delete
                    )
                    await event.client.send_file(
                        event.chat_id,
                        file,
                        supports_streaming=stream,
                        force_document=force_doc,
                        thumb=thumb,
                        attributes=attributes,
                        caption=f"`Uploaded` `{files}` `in {time_formatter(_*1000)}`",
                        reply_to=event.reply_to_msg_id or event,
                    )
                    s += 1
                except (ValueError, IsADirectoryError):
                    c += 1
            break
        attributes = None
        if stream:
            try:
                attributes = await set_attributes(result)
            except KeyError as er:
                LOGS.exception(er)
        file, _ = await event.client.fast_uploader(
            result, show_progress=True, event=msg, to_delete=delete
        )
        await event.client.send_file(
            event.chat_id,
            file,
            supports_streaming=stream,
            force_document=force_doc,
            thumb=thumb,
            attributes=attributes,
            caption=f"`Uploaded` `{result}` `in {time_formatter(_*1000)}`",
        )
    await msg.try_delete()
