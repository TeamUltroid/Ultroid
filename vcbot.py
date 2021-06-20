import logging
import os
from multiprocessing import Process

from pyrogram import Client, filters, idle
from pytgcalls import PyLogs, PyTgCalls
from pyUltroid import udB
from pyUltroid.dB.database import Var
from pyUltroid.misc import owners_and_sudoers

LOG_CHANNEL = int(udB.get("LOG_CHANNEL"))

logging.basicConfig(level=logging.INFO)

SESSION = udB.get("VC_SESSION")

asst = Client(
    "VC-ASST", api_id=Var.API_ID, api_hash=Var.API_HASH, bot_token=udB.get("BOT_TOKEN")
)
Client = Client(SESSION, api_id=Var.API_ID, api_hash=Var.API_HASH)

CallsClient = PyTgCalls(Client, log_mode=PyLogs.ultra_verbose)

AUTHS = owners_and_sudoers()


@Client.on_message(filters.command(["play"], prefixes="."))
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
        os.system(f"ffmpeg -i {dl} -f s16le -ac 1 -acodec pcm_s16le -ar 48000 {song}")
        await msg.edit_text("Starting Play..")
    CallsClient.join_group_call(message.chat.id, song)
    await msg.delete()


@CallsClient.on_stream_end()
async def handler(chat_id: int):
    CallsClient.leave_group_call(chat_id)


@Client.on_message(filters.me & filters.group & filters.regex("^.lvc"))
async def handler(_, message):
    await message.edit_text("`Left...`")
    await CallsClient.leave_group_call(message.chat.id)


@asst.on_message(filters.group & filters.command("listvc"))
async def handler(_, message):
    await message.reply_text(f"{CallsClient.active_calls}")


@asst.on_message(filters.command("volume"))
async def chesendvolume(_, message):
    mk = message.text.split(" ")
    if not len(mk) > 1:
        return await message.reply_text("Give Some Input to Change the Volume...")
    try:
        CallsClient.change_volume_call(message.chat.id, int(mk[1]))
        msg = f"Volume Changed to {mk[1]}"
    except Exception as msg:
        msg = str(msg)
    await message.reply_text(msg)


@asst.on_message(filters.command("play"))
async def testing(_, msg):
    await msg.reply_text("Wait a Second..")


asst.start()
Process(target=idle).start()
CallsClient.run()
