from core import asst, udB, ultroid_bot, LOGS
from telethon import Button
from utilities.helper import inline_mention, updater

async def notify(init=False):
    chat_id = udB.get_key("LOG_CHANNEL")
    spam_sent, BTTS = None, None
    if init:  # Detailed Message at Initial Deploy
        MSG = """🎇 **Thanks for Deploying Ultroid Userbot!**
• Here, are the Some Basic stuff from, where you can Know, about its Usage."""
        PHOTO = "https://graph.org/file/54a917cc9dbb94733ea5f.jpg"
        # TODO: udB.set_key("INIT_DEPLOY", True)
    else:
        MSG = f"**Ultroid has been deployed!**\n➖➖➖➖➖➖➖➖➖➖\n**UserMode**: {inline_mention(ultroid_bot.me)}\n**Assistant**: @{asst.me.username}\n➖➖➖➖➖➖➖➖➖➖\n**Support**: @TeamUltroid\n➖➖➖➖➖➖➖➖➖➖"
        BTTS, PHOTO = None, None
        if prev_spam := udB.get_key("LAST_UPDATE_LOG_SPAM"):
            try:
                await asst.delete_messages(chat_id, int(prev_spam))
            except Exception as E:
                LOGS.info(f"Error while Deleting Previous Update Message :{str(E)}")
        if await updater():
            BTTS = Button.inline("Update Available", "updtavail")

    try:
        spam_sent = await asst.send_message(chat_id, MSG, file=PHOTO, buttons=BTTS)
    except Exception as el:
        LOGS.exception(el)
        try:
            spam_sent = await ultroid_bot.send_message(chat_id, MSG)
        except Exception as ef:
            LOGS.exception(ef)
    if spam_sent:
        udB.set_key("LAST_UPDATE_LOG_SPAM", spam_sent.id)