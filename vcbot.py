import logging
from multiprocessing import Process

from pyrogram import Client, filters, idle
from pyrogram.raw import functions
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from pytgcalls import PyLogs, PyTgCalls
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

CACHE = {}
_vc_sudos = udB.get("VC_SUDOS").split() if udB.get("VC_SUDOS") else ""
A_AUTH = [udB["OWNER_ID"], *sudoers(), *_vc_sudos]
AUTH = [int(x) for x in A_AUTH]


async def download(query, chat):
    song = f"VCSONG_{chat}.raw"
    s = await bash(
        f"""youtube-dl -x --audio-format best --audio-quality 1 --postprocessor-args "-f s16le -ac 1 -acodec pcm_s16le -ar 48000 '{song}' -y" ytsearch:'{query}'"""
    )
    return song


@asst.on_message(filters.command("play") & filters.user(AUTH))
async def startup(_, message):
    chat = message.chat.id
    msg = await message.reply_text("`Processing...`")
    song = message.text.split(" ", maxsplit=1)
    if not message.reply_to_message and len(song) > 1:
        song = song[1]
        song = await download(song, message.chat.id)
    elif not message.reply_to_message.audio:
        return await msg.edit_text("Pls Reply to Audio File or Give Search Query...")
    elif not message.reply_to_message and len(song) == 1:
        return await msg.edit_text("Pls Give me Something to Play...")
    else:
        dl = await message.reply_to_message.download()
        print(dl)
        song = f"VCSONG_{chat}.raw"
        print(
            await bash(
                f'ffmpeg -i "{dl}" -f s16le -ac 1 -acodec pcm_s16le -ar 48000 {song} -y'
            )
        )
    await asst.send_message(
        LOG_CHANNEL, f"Joined Voice Call in {message.chat.title} [`{chat}`]"
    )
    CallsClient.join_group_call(message.chat.id, song)
    reply_markup = InlineKeyboardMarkup(
        [[InlineKeyboardButton("Pause", callback_data=f"vcp_{chat}")]]
    )
    await msg.edit_text("Started Play...", reply_markup=reply_markup)


@CallsClient.on_stream_end()
async def handler(chat_id: int):
    CallsClient.leave_group_call(chat_id)


@asst.on_message(filters.regex("leavevc") & filters.user(AUTH))
async def handler(_, message):
    await message.reply_text("`Left...`")
    await CallsClient.leave_group_call(message.chat.id)


@asst.on_message(filters.command("listvc") & filters.user(AUTH))
async def handler(_, message):
    await message.reply_text(f"{CallsClient.active_calls}")


@asst.on_message(filters.command("volume") & filters.user(AUTH))
async def chesendvolume(_, message):
    mk = message.text.split(" ")
    if not len(mk) > 1:
        fchat = await Client.send(
            functions.channels.GetFullChannel(channel=message.chat.id)
        )
        mk = fchat.full_chat.call
        Vl = await Client.send(
            functions.phone.GetGroupParticipants(
                call=mk, ids=["me"], sources=[], offset="", limit=0
            )
        )
        try:
            CML = Vl.participants[0].volume
        except IndexError:
            CML = None or 0
        return await message.reply_text(f"**Current Volume :** {CML}%")
    try:
        if int(mk[1]) not in range(1, 101):
            return await message.reply_text("Volume should be in between 1-100")
        CallsClient.change_volume_call(message.chat.id, int(mk[1]))
        msg = f"Volume Changed to {mk[1]}"
    except Exception as msg:
        msg = str(msg)
    await message.reply_text(msg)


@asst.on_callback_query(filters.regex("^vc(.*)"))
async def stopvc(_, query):
    match = query.matches[0].group(1).split("_")
    chat = int(match[1])
    if match[0] == "r":
        CallsClient.resume_stream(chat)
        BT = "Resume"
    else:
        CallsClient.pause_stream(chat)
        BT = "Pause"
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
