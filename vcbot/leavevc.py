from . import *


@asst.on_message(filters.command("leavevc") & filters.user(AUTH) & ~filters.edited)
async def leavehandler(_, message):
    spli = message.text.split(" ", maxpslit=1)
    try:
        chat = spli[1]
    except IndexError:
        chat = message.chat.id
    await eor(message, "`Left Vc...`")
    CallsClient.leave_group_call(chat)


@Client.on_message(filters.me & filters.command("leavevc", HNDLR) & ~filters.edited)
async def lhandler(_, message):
    await leavehandler(_, message)