import asyncio
import os
import re
from datetime import datetime as dt

import ffmpeg
from pyrogram import Client, filters
from pyrogram.raw import functions
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from pytgcalls import StreamType
from pyUltroid import CallsClient, udB
from pyUltroid import vcasst as asst
from pyUltroid import vcClient as Client
from pyUltroid.functions.all import bash
from pyUltroid.misc import sudoers

LOG_CHANNEL = int(udB.get("LOG_CHANNEL"))


SESSION = udB.get("VC_SESSION")
"""
asst = Client(
    "VC-ASST", api_id=Var.API_ID, api_hash=Var.API_HASH, bot_token=udB.get("BOT_TOKEN")
)
Client = Client(SESSION, api_id=Var.API_ID, api_hash=Var.API_HASH)
CallsClient = PyTgCalls(Client, log_mode=PyLogs.ultra_verbose)
"""
HNDLR = udB.get("HNDLR")
QUEUE = {}
_vc_sudos = udB.get("VC_SUDOS").split() if udB.get("VC_SUDOS") else ""
A_AUTH = [udB["OWNER_ID"], *sudoers(), *_vc_sudos]
AUTH = [int(x) for x in A_AUTH]


def add_to_queue(chat_id, song):
    try:
        play_at = len(QUEUE[int(chat_id)]) + 1
    except BaseException:
        play_at = 1
    QUEUE[int(chat_id)] = {play_at: song}
    return QUEUE[int(chat_id)]


def get_from_queue(chat_id):
    try:
        play_this = list(QUEUE[int(chat_id)].keys())[0]
    except KeyError:
        raise KeyError
    song = QUEUE[int(chat_id)][play_this]
    return song


async def eor(message, text, *args, **kwargs):
    if message.outgoing:
        return await message.edit_text(text, *args, **kwargs)
    return await message.reply_text(text, *args, **kwargs)


async def download(query, chat, ts):
    song = f"VCSONG_{chat}_{ts}.raw"
    if ("youtube.com" or "youtu.be") in query:
        await bash(
            f"""youtube-dl -x --audio-format best --audio-quality 1 --postprocessor-args "-f s16le -ac 1 -acodec pcm_s16le -ar 48000 '{song}' -y" {query}"""
        )
    else:
        await bash(
            f"""youtube-dl -x --audio-format best --audio-quality 1 --postprocessor-args "-f s16le -ac 1 -acodec pcm_s16le -ar 48000 '{song}' -y" ytsearch:'{query}'"""
        )
    return song


@asst.on_message(
    filters.command(["play", "cplay"])
    & filters.user(AUTH)
    & ~filters.edited
    & filters.group
)
async def startup(_, message):
    msg = await eor(message, "`Processing..`")
    song = message.text.split(" ", maxsplit=1)
    ChatPlay = None
    if message.text[1] != "c":
        chat = message.chat.id
    else:
        ChatPlay = True
        try:
            song = song[1].split(" ", maxsplit=1)
        except IndexError:
            if not reply:
                return await msg.edit_text(
                    "Please Give a Channel Username/Id to Play There or use /play to play in current Chat."
                )
        chat = song[0]
    if ChatPlay:
        Chat = await Client.get_chat(chat)
        chat = Chat.id
    TS = dt.now().strftime("%H:%M:%S")
    reply = message.reply_to_message
    if not reply and len(song) > 1:
        song = await download(song[1], message.chat.id, TS)
    elif not reply and len(song) == 1:
        return await msg.edit_text("Pls Give me Something to Play...")
    elif not (reply.audio or reply.voice):
        return await msg.edit_text("Pls Reply to Audio File or Give Search Query...")
    else:
        dl = await reply.download()
        song = f"VCSONG_{chat}_{TS}.raw"
        await bash(
            f'ffmpeg -i "{dl}" -f s16le -ac 1 -acodec pcm_s16le -ar 48000 {song} -y'
        )
        if reply.audio and reply.audio.thumbs:
            dll = reply.audio.thumbs[0].file_id
            th = await asst.download_media(dll)
            try:
                CallsClient.active_calls[chat]
            except KeyError:
                await msg.delete()
                msg = await message.reply_photo(th, caption="`Playing...`")
            os.remove(th)
    if chat in CallsClient.active_calls.keys():
        add_to_queue(chat, song)
        return await message.reply_text(
            f"Added to queue at #{list(QUEUE[chat].keys())[-1]}"
        )
    chattitle = message.chat.title
    if ChatPlay:
        chattitle = Chat.title
    await asst.send_message(LOG_CHANNEL, f"Joined Voice Call in {chattitle} [`{chat}`]")
    CallsClient.join_group_call(chat, song)
    reply_markup = InlineKeyboardMarkup(
        [[InlineKeyboardButton("Pause", callback_data=f"vcp_{chat}")]]
    )
    await msg.edit_reply_markup(reply_markup)


@Client.on_message(filters.me & filters.command("play", HNDLR) & ~filters.edited)
async def cstartup(_, message):
    await startup(_, message)


@CallsClient.on_stream_end()
async def streamhandler(chat_id: int):
    if chat_id in QUEUE.keys():
        CallsClient.change_stream(chat_id, get_from_queue(chat_id))
        try:
            pos = list(QUEUE[int(chat_id)])[0]
            del QUEUE[chat_id][pos]
        except BaseException as ap:
            print(ap)
    else:
        CallsClient.leave_group_call(chat_id)


@asst.on_message(filters.command("leavevc") & filters.user(AUTH) & ~filters.edited)
async def leavehandler(_, message):
    await eor(message, "`Left...`")
    CallsClient.leave_group_call(message.chat.id)


@Client.on_message(filters.me & filters.command("leavevc", HNDLR) & ~filters.edited)
async def lhandler(_, message):
    await handler(_, message)


@asst.on_message(filters.command("listvc") & filters.user(AUTH) & ~filters.edited)
async def list_handler(_, message):
    await message.reply_text(f"{CallsClient.active_calls}")


@Client.on_message(filters.me & filters.command("listvc", HNDLR) & ~filters.edited)
async def llhnf(_, message):
    await message.edit_text(f"{CallsClient.active_calls}")


@asst.on_message(filters.command("radio") & filters.user(AUTH) & ~filters.edited)
async def radio(_, message):
    radio = message.text.split(" ", maxsplit=1)
    if re.search("|", radio[1]):
        ko = radio.split("|", maxsplit=1)
        chat = ko[1]
    else:
        chat = message.chat.id
    file = f"VCRADIO_{message.chat.id}.raw"
    if re.search("youtube", radio[1]) or re.search("youtu", radio[1]):
        is_live_vid = (await bash(f'youtube-dl -j "{radio[1]}" | jq ".is_live"'))[0]
        if is_live_vid == "true":
            the_input = (await bash(f"youtube-dl -x -g {radio[1]}"))[0]
        else:
            return await message.reply_text(
                "Only Live Youtube Urls/m3u8 Urls supported!"
            )
    else:
        the_input = radio[1]
    process = (
        ffmpeg.input(the_input)
        .output(
            file,
            format="s16le",
            acodec="pcm_s16le",
            ac=1,
            ar="48000",
            loglevel="error",
        )
        .overwrite_output()
        .run_async()
    )
    await asyncio.sleep(2)
    CallsClient.join_group_call(
        chat, file, stream_type=StreamType().live_stream
    )
    await message.reply_text("Playing Radio")


@Client.on_message(filters.me & filters.command("radio", HNDLR) & ~filters.edited)
async def rplay(_, message):
    await radio(_, message)


@asst.on_message(filters.command("volume") & filters.user(AUTH) & ~filters.edited)
async def chesendvolume(_, message):
    mk = message.text.split(" ")
    if not len(mk) > 1:
        me = await Client.get_me()
        fchat = await Client.send(
            functions.channels.GetFullChannel(
                channel=await Client.resolve_peer(message.chat.id)
            )
        )
        mk = fchat.full_chat.call
        Vl = await Client.send(
            functions.phone.GetGroupParticipants(
                call=mk,
                ids=[await Client.resolve_peer(me.id)],
                sources=[],
                offset="",
                limit=0,
            )
        )
        try:
            CML = Vl.participants[0].volume
        except IndexError:
            CML = None or 0
        return await eor(message, f"**Current Volume :** {CML}%")
    try:
        if int(mk[1]) not in range(1, 101):
            return await eor(message, "Volume should be in between 1-100")
        CallsClient.change_volume_call(message.chat.id, int(mk[1]))
        msg = f"Volume Changed to {mk[1]}"
    except Exception as msg:
        msg = str(msg)
    await eor(message, msg)


@Client.on_message(filters.me & filters.command("volume", HNDLR) & ~filters.edited)
async def volplay(_, message):
    await chesendvolume(_, message)


@asst.on_callback_query(filters.regex("^vc(.*)"))
async def stopvc(_, query):
    if query.from_user.id not in AUTH:
        return await query.answer("You are Not Authorised to Use Me!", show_alert=True)
    match = query.matches[0].group(1).split("_")
    chat = int(match[1])
    if match[0] == "r":
        CallsClient.resume_stream(chat)
        BT = "Pause"
    else:
        CallsClient.pause_stream(chat)
        BT = "Resume"
    await query.answer("Done", show_alert=True)
    dt = BT[0].lower()
    await query.edit_message_reply_markup(
        InlineKeyboardMarkup(
            [[InlineKeyboardButton(BT, callback_data=f"vc{dt}_{chat}")]]
        )
    )


"""
asst.start()
Process(target=idle).start()
CallsClient.run()
"""
