import logging

from pyrogram import Client, filters
from pytgcalls import PyLogs, PyTgCalls
from pyUltroid import udB
from pyUltroid.dB.database import Var

LOG_CHANNEL = int(udB.get("LOG_CHANNEL"))

logging.basicConfig(level=logging.INFO)

SESSION = udB.get("VC_SESSION")

Client = Client(SESSION, api_id=Var.API_ID, api_hash=Var.API_HASH)

CallsClient = PyTgCalls(Client, log_mode=PyLogs.ultra_verbose)


@Client.on_message(filters.me & filters.group & filters.command(["play"], prefixes="."))
async def startup(_, message):
    msg = await message.edit_text("`Processing...`")
    song = message.text.split(" ")
    if not message.reply_to_message and len(song) > 1:
        song = song[1]
    elif not message.reply_to_message.audio:
        return await msg.edit_text("Pls Reply to Audio File or Give Search Query...")
    else:
        dl = await message.reply_to_message.download()
        song = f"{message.chat.id}_VCSONG.raw"
        await bash(f"ffmpeg -i {dl} -f s16le -ac 1 -acodec pcm_s16le -ar 4800 {song}")
    CallsClient.join_group_call(message.chat.id, song)
    await msg.delete()


@CallsClient.on_stream_end()
async def handler(chat_id: int):
    CallsClient.leave_group_call(chat_id)


@Client.on_message(filters.me & filters.group & filters.regex("^.lvc"))
async def handler(_, message):
    await message.edit_text("`Left...`")
    await CallsClient.leave_group_call(message.chat.id)


CallsClient.run()
