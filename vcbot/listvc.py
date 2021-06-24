from . import *


@asst.on_message(filters.command("listvc") & filters.user(AUTH) & ~filters.edited)
async def list_handler(_, message):
    await message.reply_text(f"{CallsClient.active_calls}")


@Client.on_message(filters.me & filters.command("listvc", HNDLR) & ~filters.edited)
async def llhnf(_, message):
    await message.edit_text(f"{CallsClient.active_calls}")