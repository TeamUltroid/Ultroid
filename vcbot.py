import logging
from multiprocessing import Process

from pyrogram import Client, filters, idle
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
A_AUTH = [udB.get("OWNER_ID"),*sudoers()]
AUTH = list(int(a) for a in A_AUTH)

async def download(query, chat):
    song = f"VCSONG_{chat}.raw"
    s = await bash(
        f"""youtube-dl -x --audio-format best --audio-quality 1 --postprocessor-args "-f s16le -ac 1 -acodec pcm_s16le -ar 48000 '{song}' -y" ytsearch:'{query}'"""
    )
    return song


@asst.on_message(filters.command("play") & filters.users(AUTH))
async def startup(_, message):
    chat = message.chat.id
    msg = await message.reply_text("`Processing...`")
    song = message.text.split(" ", maxsplit=1)
    if not message.reply_to_message and len(song) > 1:
        song = song[1]
        song = await download(song, message.chat.id)
        await msg.edit_text("Starting Play..")
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


@asst.on_message(filters.command("listvc") & filters.users(AUTH))
async def handler(_, message):
    await message.reply_text(f"{CallsClient.active_calls}")


@asst.on_message(filters.command("volume") & filters.users(AUTH))
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


asst.start()
Process(target=idle).start()
CallsClient.run()
