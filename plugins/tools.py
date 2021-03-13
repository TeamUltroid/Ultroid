# Ultroid - UserBot
# Copyright (C) 2020 TeamUltroid
#
# This file is a part of < https://github.com/TeamUltroid/Ultroid/ >
# PLease read the GNU Affero General Public License in
# <https://www.github.com/TeamUltroid/Ultroid/blob/main/LICENSE/>.

"""
✘ Commands Available -

• `{i}bash <cmds>`
    Run linux commands on telegram.

• `{i}eval <cmds>`
    Evaluate python commands on telegram.

• `{i}circle`
    Reply to a audio song or gif to get video note.

• `{i}bots`
    Shows the number of bots in the current chat with their perma-link.

• `{i}hl <a link>`
    Embeds the link with a whitespace as message.

• `{i}id`
    Reply a Sticker to Get Its Id
    Reply a User to Get His Id
    Without Replying You Will Get the Chat's Id

• `{i}sg <reply to a user>`
    Get His Name History of the replied user.

• `{i}tr <dest lang code> <(reply to) a message>`
    Get translated message.
"""

import asyncio
import io
import sys
import time
import traceback
from asyncio.exceptions import TimeoutError

import cv2
import emoji
from googletrans import Translator
from telethon.errors.rpcerrorlist import YouBlockedUserError
from telethon.tl.types import ChannelParticipantAdmin, ChannelParticipantsBots
from telethon.utils import pack_bot_file_id

from . import *


@ultroid_cmd(
    pattern="tr",
)
async def _(event):
    input = event.text[4:6]
    txt = event.text[7:]
    xx = await eor(event, "`Translating...`")
    if event.reply_to_msg_id:
        previous_message = await event.get_reply_message()
        text = previous_message.message
        lan = input or "en"
    elif input:
        text = txt
        lan = input or "en"
    else:
        return await eod(xx, f"`{hndlr}tr LanguageCode` as reply to a message", time=5)
    text = emoji.demojize(text.strip())
    lan = lan.strip()
    translator = Translator()
    try:
        tt = translator.translate(text, dest=lan)
        output_str = f"**TRANSLATED** from {tt.src} to {lan}\n{tt.text}"
        await eod(xx, output_str)
    except Exception as exc:
        await eod(xx, str(exc), time=10)


@ultroid_cmd(
    pattern="id$",
)
async def _(event):
    if event.reply_to_msg_id:
        await event.get_input_chat()
        r_msg = await event.get_reply_message()
        if r_msg.media:
            bot_api_file_id = pack_bot_file_id(r_msg.media)
            await eor(
                event,
                "**Current Chat ID:**  `{}`\n**From User ID:**  `{}`\n**Bot API File ID:**  `{}`".format(
                    str(event.chat_id), str(r_msg.sender.id), bot_api_file_id
                ),
            )
        else:
            await eor(
                event,
                "**Chat ID:**  `{}`\n**User ID:**  `{}`".format(
                    str(event.chat_id), str(r_msg.sender.id)
                ),
            )
    else:
        await eor(event, "**Current Chat ID:**  `{}`".format(str(event.chat_id)))


@ultroid_cmd(pattern="bots ?(.*)")
async def _(ult):
    await ult.edit("`...`")
    if ult.is_private:
        user = await ult.get_chat()
        if not user.bot:
            return await ult.edit("`Seariously ?`")

    mentions = "**Bots in this Chat**: \n"
    input_str = ult.pattern_match.group(1)
    to_write_chat = await ult.get_input_chat()
    chat = None
    if not input_str:
        chat = to_write_chat
    else:
        mentions = "**Bots in **{}: \n".format(input_str)
        try:
            chat = await ultroid_bot.get_entity(input_str)
        except Exception as e:
            await eor(ult, str(e))
            return None
    try:
        async for x in ultroid_bot.iter_participants(
            chat, filter=ChannelParticipantsBots
        ):
            if isinstance(x.participant, ChannelParticipantAdmin):
                mentions += "\n ⚜️ [{}](tg://user?id={}) `{}`".format(
                    x.first_name, x.id, x.id
                )
            else:
                mentions += "\n [{}](tg://user?id={}) `{}`".format(
                    x.first_name, x.id, x.id
                )
    except Exception as e:
        mentions += " " + str(e) + "\n"
    await eod(ult, mentions)


@ultroid_cmd(pattern="hl")
async def _(ult):
    try:
        input = ult.text.split(" ", maxsplit=1)[1]
    except IndexError:
        return await eod(ult, "`Input some link`", time=5)
    await eod(ult, "[ㅤㅤㅤㅤㅤㅤㅤ](" + input + ")", link_preview=False)


@ultroid_cmd(
    pattern="circle$",
)
async def _(e):
    a = await e.get_reply_message()
    if a is None:
        return await eor(e, "Reply to a gif or audio")
    if a.document and a.document.mime_type == "audio/mpeg":
        z = await eor(e, "**Cʀᴇᴀᴛɪɴɢ Vɪᴅᴇᴏ Nᴏᴛᴇ**")
        toime = time.time()
        try:
            bbbb = await a.download_media(thumb=-1)
            im = cv2.imread(bbbb)
            dsize = (320, 320)
            output = cv2.resize(im, dsize, interpolation=cv2.INTER_AREA)
            cv2.imwrite("img.png", output)
            thumb = "img.png"
        except TypeError:
            thumb = "./resources/extras/thumb.jpg"
        c = await a.download_media(
            "resources/downloads/",
            progress_callback=lambda d, t: asyncio.get_event_loop().create_task(
                progress(d, t, z, toime, "Dᴏᴡɴʟᴏᴀᴅɪɴɢ...")
            ),
        )
        await z.edit("**Dᴏᴡɴʟᴏᴀᴅᴇᴅ...\nNᴏᴡ Cᴏɴᴠᴇʀᴛɪɴɢ...**")
        cmd = [
            "ffmpeg",
            "-i",
            c,
            "-acodec",
            "libmp3lame",
            "-ac",
            "2",
            "-ab",
            "144k",
            "-ar",
            "44100",
            "comp.mp3",
        ]
        proess = await asyncio.create_subprocess_exec(
            *cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
        )
        stdout, stderr = await proess.communicate()
        stderr.decode().strip()
        stdout.decode().strip()
        mcd = [
            "ffmpeg",
            "-y",
            "-i",
            thumb,
            "-i",
            "comp.mp3",
            "-c:a",
            "copy",
            "circle.mp4",
        ]
        process = await asyncio.create_subprocess_exec(
            *mcd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
        )
        stdout, stderr = await process.communicate()
        stderr.decode().strip()
        stdout.decode().strip()
        taime = time.time()
        await e.client.send_file(
            e.chat_id,
            "circle.mp4",
            thumb=thumb,
            video_note=True,
            reply_to=a,
            progress_callback=lambda d, t: asyncio.get_event_loop().create_task(
                progress(d, t, z, taime, "Uᴘʟᴏᴀᴅɪɴɢ...")
            ),
        )
        await z.delete()
        os.system("rm resources/downloads/*")
        os.system("rm circle.mp4 comp.mp3 img.png")
        os.remove(bbbb)
    elif a.document and a.document.mime_type == "video/mp4":
        z = await eor(e, "**Cʀᴇᴀᴛɪɴɢ Vɪᴅᴇᴏ Nᴏᴛᴇ**")
        c = await a.download_media("resources/downloads/")
        await e.client.send_file(e.chat_id, c, video_note=True, reply_to=a)
        await z.delete()
        os.remove(c)
    else:
        return await eor(e, "**Reply to a gif or audio file only**")


@ultroid_cmd(
    pattern="bash",
)
async def _(event):
    if Redis("I_DEV") != "True":
        await eor(
            event,
            f"Developer Restricted!\nIf you know what this does, and want to proceed\n\n `{HNDLR}setredis I_DEV True`\n\nThis Might Be Dangerous.",
        )
        return
    xx = await eor(event, "`Processing...`")
    try:
        cmd = event.text.split(" ", maxsplit=1)[1]
    except IndexError:
        return await eod(xx, "`No cmd given`", time=10)
    reply_to_id = event.message.id
    if event.reply_to_msg_id:
        reply_to_id = event.reply_to_msg_id
    time.time() + 100
    process = await asyncio.create_subprocess_shell(
        cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
    )
    stdout, stderr = await process.communicate()
    OUT = f"<b>☞ BASH\n\n• COMMAND:</b>\n<code>{cmd}</code> \n\n"
    e = stderr.decode()
    if e:
        OUT += f"<b>• ERROR:</b> \n<code>{e}</code>\n"
    o = stdout.decode()
    if not o and not e:
        o = "Success"
        OUT += f"<b>• OUTPUT:</b>\n<code>{o}</b>"
    else:
        _o = o.split("\n")
        o = "\n".join(_o)
        OUT += f"<b>• OUTPUT:</b>\n<code>{o}</code>"
    if len(OUT) > 4096:
        ultd = (
            OUT.replace("<code>", "")
            .replace("</code>", "")
            .replace("<b>", "")
            .replace("</b>", "")
            .replace("<i>", "")
            .replace("</i>", "")
        )
        with io.BytesIO(str.encode(ultd)) as out_file:
            out_file.name = "bash.txt"
            await event.client.send_file(
                event.chat_id,
                out_file,
                force_document=True,
                allow_cache=False,
                caption=f"`{cmd}`",
                reply_to=reply_to_id,
            )
            await xx.delete()
    else:
        await eod(xx, OUT, parse_mode="html")


@ultroid_cmd(
    pattern="eval",
)
async def _(event):
    if Redis("I_DEV") != "True":
        await eor(
            event,
            f"Developer Restricted!\nIf you know what this does, and want to proceed\n\n {HNDLR}setredis I_DEV True\n\nThis Might Be Dangerous.",
        )
        return
    xx = await eor(event, "`Processing ...`")
    try:
        cmd = event.text.split(" ", maxsplit=1)[1]
    except IndexError:
        return await eod(xx, "`Give some python cmd`", time=5)
    if event.reply_to_msg_id:
        reply_to_id = event.reply_to_msg_id
    old_stderr = sys.stderr
    old_stdout = sys.stdout
    redirected_output = sys.stdout = io.StringIO()
    redirected_error = sys.stderr = io.StringIO()
    stdout, stderr, exc = None, None, None
    reply_to_id = event.message.id
    try:
        await aexec(cmd, event)
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
        evaluation = "Success"
    final_output = "<i>►</i> <b>EVAL</b>\n<code>{}</code>\n\n<i>►</i><b>OUTPUT</b>: \n<code>{}</code>".format(
        cmd, evaluation
    )
    if len(final_output) > 4096:
        ultd = (
            final_output.replace("<code>", "")
            .replace("</code>", "")
            .replace("<b>", "")
            .replace("</b>", "")
            .replace("<i>", "")
            .replace("</i>", "")
        )
        with io.BytesIO(str.encode(ultd)) as out_file:
            out_file.name = "eval.txt"
            await ultroid_bot.send_file(
                event.chat_id,
                out_file,
                force_document=True,
                allow_cache=False,
                caption=f"```{cmd}```",
                reply_to=reply_to_id,
            )
            await xx.delete()
    else:
        await eod(xx, final_output, parse_mode="html")


async def aexec(code, event):
    e = message = event
    client = event.client
    exec(
        f"async def __aexec(e, client): "
        + "\n message = event = e"
        + "".join(f"\n {l}" for l in code.split("\n"))
    )

    return await locals()["__aexec"](e, e.client)


@ultroid_cmd(
    pattern="sg(?: |$)(.*)",
)
async def lastname(steal):
    if steal.fwd_from:
        return
    if not steal.reply_to_msg_id:
        await steal.edit("Reply to any user message.")
        return
    message = await steal.get_reply_message()
    chat = "@SangMataInfo_bot"
    user_id = message.sender.id
    id = f"/search_id {user_id}"
    if message.sender.bot:
        await steal.edit("Reply to actual users message.")
        return
    lol = await eor(steal, "Processingg !!!!!")
    try:
        async with ultroid_bot.conversation(chat) as conv:
            try:
                msg = await conv.send_message(id)
                response = await conv.get_response()
                respond = await conv.get_response()
                responds = await conv.get_response()
            except YouBlockedUserError:
                await lol.edit("Please unblock @sangmatainfo_bot and try again")
                return
            if response.text.startswith("No records found"):
                await lol.edit("No records found for this user")
                await steal.client.delete_messages(conv.chat_id, [msg.id, response.id])
                return
            else:
                if response.text.startswith("🔗"):
                    await lol.edit(respond.message)
                    await lol.reply(responds.message)
                elif respond.text.startswith("🔗"):
                    await lol.edit(response.message)
                    await lol.reply(responds.message)
                else:
                    await lol.edit(respond.message)
                    await lol.reply(response.message)
            await steal.client.delete_messages(
                conv.chat_id, [msg.id, responds.id, respond.id, response.id]
            )
    except TimeoutError:
        return await lol.edit("Error: @SangMataInfo_bot is not responding!.")


HELP.update({f"{__name__.split('.')[1]}": f"{__doc__.format(i=HNDLR)}"})
