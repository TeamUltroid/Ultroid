from . import *


@asst.on_message(filters.command("stopvc") & filters.user(AUTH) & ~filters.edited)
async def stopvc(_, message):
    ms = message.text.split(" ", maxsplit=1)
    try:
        chat = ms[1]
    except IndexError:
        chat = message.chat.id
    CallsClient.pause_stream(chat)
    await eor(message, "Stopped VC")


@Client.on_message(
    filters.command("stopvc", HNDLR) & filters.user(AUTH) & ~filters.edited
)
async def ustop(_, message):
    await stopvc(_, message)


@asst.on_message(filters.command("resumevc") & filters.user(AUTH) & ~filters.edited)
async def stopvc(_, message):
    ms = message.text.split(" ", maxsplit=1)
    try:
        chat = ms[1]
    except IndexError:
        chat = message.chat.id
    CallsClient.resume_stream(chat)
    await eor(message, "Resumed VC")


@Client.on_message(
    filters.command("resumevc", HNDLR) & filters.user(AUTH) & ~filters.edited
)
async def ustop(_, message):
    await stopvc(_, message)
