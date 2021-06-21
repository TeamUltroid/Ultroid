import logging
import os
from datetime import datetime as dt
from multiprocessing import Process

import ffmpeg
from pyrogram import Client, filters, idle
from pyrogram.raw import functions
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from pytgcalls import PyLogs, PyTgCalls, StreamType
from pyUltroid import udB
from pyUltroid.dB.database import Var
from pyUltroid.functions.all import bash
from pyUltroid.misc import sudoers

LOG_CHANNEL = int(udB.get("LOG_CHANNEL"))

logging.basicConfig(level=logging.INFO)

SESSION = udB.get("VC_SESSION")

asst = Client(
    "VC-ASST", api_id=Var.API_ID, api_hash=Var.API_HASH, bot_token=udB.get("BOT_TOKEN")
)
Client = Client(SESSION, api_id=Var.API_ID, api_hash=Var.API_HASH)

CallsClient = PyTgCalls(Client, log_mode=PyLogs.ultra_verbose)

QUEUE = {}
_vc_sudos = udB.get("VC_SUDOS").split() if udB.get("VC_SUDOS") else ""
A_AUTH = [udB["OWNER_ID"], *sudoers(), *_vc_sudos]
AUTH = [int(x) for x in A_AUTH]


def add_to_queue(chat_id, song):
    if int(chat_id) in CallsClient.active_calls.keys():
        try:
            play_at = len(QUEUE[int(chat_id)]) + 1
        except KeyError:
            play_at = 1
        QUEUE[int(chat_id)] = {play_at: song}


def get_from_queue(chat_id):
    if int(chat_id) in CallsClient.active_calls.keys():
        try:
            play_this = list(QUEUE[int(chat_id)].keys())[0]
        except KeyError:
            raise KeyError
        return play_this


async def eor(message, text, *args, **kwargs):
    if message.outgoing:
        return await message.edit_text(text, *args, **kwargs)
    return await message.reply_text(text, *args, **kwargs)


async def download(query, chat, ts):
    song = f"VCSONG_{chat}_{ts}.raw"
    if "youtube.com" in query:
        await bash(
            f"""youtube-dl -x --audio-format best --audio-quality 1 --postprocessor-args "-f s16le -ac 1 -acodec pcm_s16le -ar 48000 '{song}' -y" {query}"""
        )
    else:
        await bash(
            f"""youtube-dl -x --audio-format best --audio-quality 1 --postprocessor-args "-f s16le -ac 1 -acodec pcm_s16le -ar 48000 '{song}' -y" ytsearch:'{query}'"""
        )
    return song


@asst.on_message(filters.command("play") & filters.user(AUTH))
async def startup(_, message):
    msg = await eor(message, "`Processing..`")
    chat = message.chat.id
    song = message.text.split(" ", maxsplit=1)
    TS = dt.now().strftime("%H:%M:%S")
    reply = message.reply_to_message
    if not reply and len(song) > 1:
        song = song[1]
        song = await download(song, message.chat.id, TS)
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
                msg = await asst.send_photo(chat, th, caption="`Playing...`")
            os.remove(th)
    if chat in CallsClient.active_calls.keys():
        add_to_queue(chat, song)
        return await message.reply_text(
            f"Added to queue at #{list(QUEUE[chat].keys())[-1]}"
        )
    await asst.send_message(
        LOG_CHANNEL, f"Joined Voice Call in {message.chat.title} [`{chat}`]"
    )
    CallsClient.join_group_call(message.chat.id, song)
    reply_markup = InlineKeyboardMarkup(
        [[InlineKeyboardButton("Pause", callback_data=f"vcp_{chat}")]]
    )
    await msg.edit_reply_markup(reply_markup)
    # gsn = get_from_queue(chat)
    # while gsn:
    #   CallsClient.change_stream(chat, gsn)


@Client.on_message(filters.me & filters.command("play", "."))
async def cstartup(_, message):
    await startup(_, message)


@CallsClient.on_stream_end()
async def streamhandler(chat_id: int):
    if chat_id in QUEUE.keys():
        CallsClient.join_group_call(chat_id, get_from_queue(chat_id))
        try:
            pos = len(QUEUE[int(chat_id)]) + 1
            del QUEUE[chat_id][pos]
        except BaseException as ap:
            print(ap)
    CallsClient.leave_group_call(chat_id)


@asst.on_message(filters.regex("leavevc") & filters.user(AUTH))
async def leavehandler(_, message):
    await eor(message, "`Left...`")
    await CallsClient.leave_group_call(message.chat.id)


@Client.on_message(filters.me & filters.command("leavevc", "."))
async def lhandler(_, message):
    await handler(_, message)


@asst.on_message(filters.command("listvc") & filters.user(AUTH))
async def list_handler(_, message):
    await message.reply_text(f"{CallsClient.active_calls}")


@Client.on_message(filters.me & filters.command("listvc", "."))
async def llhnf(_, message):
    await message.edit_text(f"{CallsClient.active_calls}")


@asst.on_message(filters.command("radio") & filters.user(AUTH))
async def radio(_, message):
    radio = message.text.split(" ", maxsplit=1)
    TS = dt.now().strftime("%H:%M:%S")
    file = f"VCRADIO_{message.chat.id}_{TS}.raw"
    process = (
        ffmpeg.input(
            "https://meethimirchihdl-lh.akamaihd.net/i/MeethiMirchiHDLive_1_1@320572/master.m3u8"
        )
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
    CallsClient.join_group_call(
        message.chat.id, file, stream_type=StreamType().live_stream
    )
    await message.reply_text("playing Radio")


@Client.on_message(filters.me & filters.command("radio", "."))
async def rplay(_, message):
    await radio(_, message)


@asst.on_message(filters.command("volume") & filters.user(AUTH))
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


@Client.on_message(filters.me & filters.command("volume", "."))
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


asst.start()
Process(target=idle).start()
CallsClient.run()
