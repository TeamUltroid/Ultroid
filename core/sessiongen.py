from re import compile
from core.version import version
from telethonpatch import TelegramClient
from telethon.events import NewMessage, CallbackQuery
from telethon.tl.custom import Message, Button
from core.config import Var
from core.decorators._assistant import asst_cmd, callback


@asst_cmd("session", owner=True)
async def sessionCommand(event: Message):
    await event.reply(
        "*Select type of session to generate:*",
        buttons=[
            [
                Button.inline("Telethon", "gen_telethon"),
                Button.inline("Pyrogram", "gen_pyrogram"),
            ]
        ],
    )


async def generate_session(ult: NewMessage, type: str):
    client: TelegramClient = ult.client
    if type == "telethon":
        from telethon.sessions import StringSession

        new_client = TelegramClient(
            StringSession(),
            api_id=Var.API_ID,
            api_hash=Var.API_HASH,
            app_version=version,
        )
    else:
        from pyrogram import Client

        new_client = Client(
            ":memory:", api_id=Var.API_ID, api_hash=Var.API_HASH, in_memory=True
        )
    async with client.conversation(ult.chat_id) as conv:
        message = await conv.send_message("Please send your phone number:")
        phoneNumber = await conv.get_response()
        await phoneNumber.delete()
        if type == "telethon":
            sentCode = await new_client.send_code_request(phoneNumber)
        else:
            sentCode = await new_client.send_code(phone_number=phoneNumber)
        await conv.send_message("Please enter the code in this format:\n6 5 8 5 5 5")
        loginCode = await conv.get_response()
        await TelegramClient.sign_in(phone=phoneNumber, code=loginCode.message.replace(' ', ''))
 

@callback(compile("gen_(.*)"), owner=True)
async def onGen(event: CallbackQuery.Event):
    _type = event.pattern_match.split("_")[-1]
    await generate_session(event, _type)
