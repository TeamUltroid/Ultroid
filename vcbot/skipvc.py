from . import *


@asst.on_message(filters.command("skipvc") & filters.user(AUTH) & ~filters.edited)
async def skiplife(_, message):
    mst = message.text.split(" ", maxsplit=1)
    try:
        chat = mst[1]
    except BaseException:
        chat = message.chat.id
    CallsClient.pause_stream(chat)
    await streamhandler(_, message)
