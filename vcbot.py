import logging

from pyUltroid import udB, vcbot
from pyUltroid.dB.database import Var

from pyrogram import Client, filters
from pytgcalls import PyTgCalls

LOG_CHANNEL = int(udB.get("LOG_CHANNEL"))

logging.basicConfig(level=logging.WARNING)

SESSION = udB.get("VC_SESSION")

Client = Client(SESSION or ":memory:",
                api_id=Var.API_ID,
                api_hash=Var.API_HASH)

CallsClient = PyTgCalls(Client)

@Client.on_message(filters.me & filters.group & filters.regex("^.play (.*)"))
async def startup(_, message):
    song = message.matches[0].group(1)
    await CallsClient.join_group_call(message.chat.id, song)


if vcbot:
  CallsClient.run()
