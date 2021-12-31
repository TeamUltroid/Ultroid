# Ultroid - UserBot
# Copyright (C) 2021-2022 TeamUltroid
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

• `{i}hl <a link>`
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

• `{i}shorturl <url> <id-optional>`
    shorten any url...
"""
import glob
import io
import os
from asyncio.exceptions import TimeoutError as AsyncTimeout

import cv2
from google_trans_new import google_translator
from htmlwebshot import WebShot
from pyUltroid.functions.tools import metadata
from telethon.errors.rpcerrorlist import MessageTooLongError, YouBlockedUserError
from telethon.tl.types import (
    ChannelParticipantAdmin,
    ChannelParticipantsBots,
    DocumentAttributeVideo,
)
from telethon.utils import pack_bot_file_id

from . import HNDLR, async_searcher, bash, eor, get_string
from . import humanbytes as hb
from . import inline_mention, is_url_ok, mediainfo, ultroid_cmd


@ultroid_cmd(pattern="tr", manager=True)
async def _(event):
    if len(event.text) > 3 and event.text[3] != " ":
        return
    input = event.text[4:].split(maxsplit=1)
    txt = input[1] if len(input) > 1 else None
    if input:
        input = input[0]
    if txt:
        text = txt
        lan = input or "en"
    elif event.is_reply:
        previous_message = await event.get_reply_message()
        text = previous_message.message
        lan = input or "en"
    else:
        return await eor(
            event, f"`{HNDLR}tr LanguageCode` as reply to a message", time=5
        )
    translator = google_translator()
    try:
        tt = translator.translate(text, lang_tgt=lan)
        fr = translator.detect(text)
        output_str = f"**TRANSLATED** from {fr} to {lan}\n{tt}"
        await event.eor(output_str)
    except Exception as exc:
        await event.eor(str(exc), time=5)


@ultroid_cmd(
    pattern="id ?(.*)",
    manager=True,
)
async def _(event):
    match = event.pattern_match.group(1)
    if event.reply_to_msg_id:
        await event.get_input_chat()
        r_msg = await event.get_reply_message()
        if r_msg.media:
            bot_api_file_id = pack_bot_file_id(r_msg.media)
            await event.eor(
                "**Current Chat ID:**  `{}`\n**From User ID:**  `{}`\n**Bot API File ID:**  `{}`\n**Msg ID:**  `{}`".format(
                    str(event.chat_id),
                    str(r_msg.sender_id),
                    bot_api_file_id,
                    str(r_msg.id),
                ),
            )
        else:
            await event.eor(
                "**Chat ID:**  `{}`\n**User ID:**  `{}`\n**Msg ID:**  `{}`".format(
                    str(event.chat_id), str(r_msg.sender_id), str(r_msg.id)
                ),
            )
    elif match:
        try:
            ids = await event.client.parse_id(match)
        except Exception as er:
            return await event.eor(str(er))
        await event.eor(
            "**Chat ID:**  `{}`\n**User ID:**  `{}`".format(
                str(event.chat_id),
                str(ids),
            ),
        )
    else:
        await event.eor(
            "**Current Chat ID:**  `{}`\n**Msg ID:**  `{}`".format(
                str(event.chat_id), str(event.id)
            ),
        )


@ultroid_cmd(pattern="bots ?(.*)", groups_only=True, manager=True)
async def _(ult):
    mentions = "• **Bots in this Chat**: \n"
    input_str = ult.pattern_match.group(1)
    if not input_str:
        chat = ult.chat_id
    else:
        mentions = f"• **Bots in **{input_str}: \n"
        try:
            chat = await ult.client.parse_id(input_str)
        except Exception as e:
            return await ult.eor(str(e))
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
        mentions += " " + str(e) + "\n"
    await ult.eor(mentions)


@ultroid_cmd(
    pattern="hl",
)
async def _(ult):
    try:
        input = ult.text.split(" ", maxsplit=1)[1]
    except IndexError:
        return await ult.eor("`Input some link`", time=5)
    await ult.eor("[ㅤㅤㅤㅤㅤㅤㅤ](" + input + ")", link_preview=False)


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
            bbbb = "resources/extras/ultroid.jpg"
        im = cv2.imread(bbbb)
        dsize = (512, 512)
        output = cv2.resize(im, dsize, interpolation=cv2.INTER_AREA)
        cv2.imwrite("img.jpg", output)
        thumb = "img.jpg"
        audio, _ = await e.client.fast_downloader(reply.document, reply.file.name)
        await msg.edit("`Creating video note...`")
        await bash(
            f'ffmpeg -i "{thumb}" -i "{audio.name}" -preset ultrafast -c:a libmp3lame -ab 64 circle.mp4 -y'
        )
        await msg.edit("`Uploading...`")
        file, _ = await e.client.fast_uploader("circle.mp4", to_delete=True)
        data = await metadata("circle.mp4")
        await e.client.send_file(
            e.chat_id,
            file,
            thumb=thumb,
            reply_to=reply,
            attributes=[
                DocumentAttributeVideo(
                    duration=data["duration"] if data["duration"] < 60 else 60,
                    w=512,
                    h=512,
                    round_message=True,
                )
            ],
        )
        await msg.delete()
        [os.remove(k) for k in [audio.name, thumb]]
    elif mediainfo(reply.media) == "gif" or mediainfo(reply.media).startswith("video"):
        msg = await e.eor("**Cʀᴇᴀᴛɪɴɢ Vɪᴅᴇᴏ Nᴏᴛᴇ**")
        file = await reply.download_media("resources/downloads/")
        await e.client.send_file(
            e.chat_id,
            file,
            video_note=True,
            thumb="resources/extras/ultroid.jpg",
            reply_to=reply,
        )
        await msg.delete()
        os.remove(file)
    else:
        await e.eor("`Reply to a gif or audio file only.`")


@ultroid_cmd(
    pattern="ls ?(.*)",
)
async def _(e):
    files = e.pattern_match.group(1)
    if not files:
        files = "*"
    elif files.endswith("/"):
        files = files + "*"
    elif "*" not in files:
        files = files + "/*"
    files = glob.glob(files)
    if not files:
        return await e.eor("`Directory Empty or Incorrect.`", time=5)
    pyfiles = []
    jsons = []
    vdos = []
    audios = []
    pics = []
    others = []
    otherfiles = []
    folders = []
    text = []
    apk = []
    exe = []
    zip_ = []
    book = []
    for file in sorted(files):
        if os.path.isdir(file):
            folders.append("📂 " + str(file))
        elif str(file).endswith(".py"):
            pyfiles.append("🐍 " + str(file))
        elif str(file).endswith(".json"):
            jsons.append("🔮 " + str(file))
        elif str(file).endswith((".mkv", ".mp4", ".avi", ".gif", "webm")):
            vdos.append("🎥 " + str(file))
        elif str(file).endswith((".mp3", ".ogg", ".m4a", ".opus")):
            audios.append("🔊 " + str(file))
        elif str(file).endswith((".jpg", ".jpeg", ".png", ".webp", ".ico")):
            pics.append("🖼 " + str(file))
        elif str(file).endswith((".txt", ".text", ".log")):
            text.append("📄 " + str(file))
        elif str(file).endswith((".apk", ".xapk")):
            apk.append("📲 " + str(file))
        elif str(file).endswith((".exe", ".iso")):
            exe.append("⚙ " + str(file))
        elif str(file).endswith((".zip", ".rar")):
            zip_.append("🗜 " + str(file))
        elif str(file).endswith((".pdf", ".epub")):
            book.append("📗 " + str(file))
        elif "." in str(file)[1:]:
            others.append("🏷 " + str(file))
        else:
            otherfiles.append("📒 " + str(file))
    omk = [
        *sorted(folders),
        *sorted(pyfiles),
        *sorted(jsons),
        *sorted(zip_),
        *sorted(vdos),
        *sorted(pics),
        *sorted(audios),
        *sorted(apk),
        *sorted(exe),
        *sorted(book),
        *sorted(text),
        *sorted(others),
        *sorted(otherfiles),
    ]
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
                    text += emoji + f" `{nam}`" + "  `" + hb(size) + "`\n"
                    fos += size
                else:
                    text += emoji + f" `{nam}`" + "\n"
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
                    text += emoji + f" `{nam}`" + "\n"
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
        await e.eor(text)
    except MessageTooLongError:
        with io.BytesIO(str.encode(text)) as out_file:
            out_file.name = "output.txt"
            await e.reply(
                f"`{e.text}`", file=out_file, thumb="resources/extras/ultroid.jpg"
            )
        await e.delete()


@ultroid_cmd(
    pattern="sg ?(.*)",
)
async def lastname(steal):
    mat = steal.pattern_match.group(1)
    if not steal.is_reply and not mat:
        return await steal.eor("`Use this command with reply or give Username/id...`")
    if mat:
        try:
            user_id = await steal.client.parse_id(mat)
        except ValueError:
            user_id = mat
    message = await steal.get_reply_message()
    if message:
        user_id = message.sender.id
    chat = "@SangMataInfo_bot"
    id = f"/search_id {user_id}"
    lol = await steal.eor(get_string("com_1"))
    try:
        async with steal.client.conversation(chat) as conv:
            try:
                msg = await conv.send_message(id)
                response = await conv.get_response()
                respond = await conv.get_response()
                responds = await conv.get_response()
            except YouBlockedUserError:
                return await lol.edit("Please unblock @sangmatainfo_bot and try again")
            if (
                (response and response.text == "No records found")
                or (respond and respond.text == "No records found")
                or (responds and responds.text == "No records found")
            ):
                await lol.edit("No records found for this user")
                await steal.client.delete_messages(conv.chat_id, [msg.id, response.id])
            elif response.text.startswith("🔗"):
                await lol.edit(respond.message)
                await lol.reply(responds.message)
            elif respond.text.startswith("🔗"):
                await lol.edit(response.message)
                await lol.reply(responds.message)
            else:
                await lol.edit(respond.message)
                await lol.reply(response.message)
            await steal.client.delete_messages(
                conv.chat_id,
                [msg.id, responds.id, respond.id, response.id],
            )
    except AsyncTimeout:
        await lol.edit("Error: @SangMataInfo_bot is not responding!.")


@ultroid_cmd(pattern="webshot ?(.*)")
async def webss(event):
    xx = await event.eor(get_string("com_1"))
    xurl = event.pattern_match.group(1)
    if not xurl:
        return await xx.eor(get_string("wbs_1"), time=5)
    if not is_url_ok(xurl):
        return await xx.eor(get_string("wbs_2"), time=5)
    shot = WebShot(quality=88, flags=["--enable-javascript", "--no-stop-slow-scripts"])
    pic = await shot.create_pic_async(url=xurl)
    await xx.reply(
        get_string("wbs_3").format(xurl),
        file=pic,
        link_preview=False,
        force_document=True,
    )
    os.remove(pic)
    await xx.delete()


@ultroid_cmd(pattern="shorturl")
async def magic(event):
    try:
        match = event.text.split(maxsplit=1)[1].strip()
    except IndexError:
        return await event.eor("`Provide url to turn into tiny...`")
    match, id_ = match.split(), None
    data = {}
    if len(match) > 1:
        data.update({"id": match[1]})
    url = match[0]
    data.update({"link": url})
    data = await async_searcher(
        "https://tiny.ultroid.tech/api/new",
        data=data,
        post=True,
        re_json=True,
    )
    response = data.get("response", {})
    if not response.get("status"):
        return await event.eor("**ERRROR :** `{}`".format(response["message"]))
    await event.eor(
        f"• **Ultroid Tiny**\n• Given Url : {url}\n• Shorten Url : {data['response']['tinyUrl']}"
    )
