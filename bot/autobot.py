import os
import asyncio, sys
from core import ultroid_bot, asst, udB, LOGS
from utilities.helper import download_file
from random import randint, choice
from telethon.tl.functions.contacts import UnblockRequest


async def send_and_wait(message, time=1):
    await ultroid_bot.send_message("botfather", message)
    await asyncio.sleep(time)


async def autobot():
    await ultroid_bot.start()
    LOGS.info("MAKING A TELEGRAM BOT FOR YOU AT @BotFather, Kindly Wait")
    who = ultroid_bot.me
    name = f"{who.first_name}'s Bot"
    if who.username:
        username = f"{who.username}_bot"
    else:
        username = f"ultroid_{str(who.id)[5:]}_bot"
    bf = "@BotFather"
    await ultroid_bot(UnblockRequest(bf))
    await send_and_wait("/cancel")
    await send_and_wait("/newbot")
    isdone = (await ultroid_bot.get_messages(bf, limit=1))[0].text
    if isdone.startswith("That I cannot do.") or "20 bots" in isdone:
        LOGS.critical(
            "Please make a Bot from @BotFather and add it's token in BOT_TOKEN, as an env var and restart me."
        )

        sys.exit(1)
    await ultroid_bot.send_message(bf, name)
    await asyncio.sleep(1)
    isdone = (await ultroid_bot.get_messages(bf, limit=1))[0].text
    if not isdone.startswith("Good."):
        await ultroid_bot.send_message(bf, "My Assistant Bot")
        await asyncio.sleep(1)
        isdone = (await ultroid_bot.get_messages(bf, limit=1))[0].text
        if not isdone.startswith("Good."):
            LOGS.critical(
                "Please make a Bot from @BotFather and add it's token in BOT_TOKEN, as an env var and restart me."
            )

            sys.exit(1)
    await send_and_wait(username)
    isdone = (await ultroid_bot.get_messages(bf, limit=1))[0].text
    await ultroid_bot.send_read_acknowledge("botfather")
    if isdone.startswith("Sorry,"):
        ran = randint(1, 100)
        username = f"ultroid_{str(who.id)[6:]}{str(ran)}_bot"
        await send_and_wait(username)
        isdone = (await ultroid_bot.get_messages(bf, limit=1))[0].text
    if isdone.startswith("Done!"):
        token = isdone.split("`")[1]
        udB.set_key("BOT_TOKEN", token)
        await enable_inline(ultroid_bot, username)
        LOGS.info(
            f"Done. Successfully created @{username} to be used as your assistant bot!"
        )
    else:
        LOGS.info(
            "Please Delete Some Of your Telegram bots at @Botfather or Set Var BOT_TOKEN with token of a bot"
        )

        sys.exit(1)


# customize assistant


async def customize():
    try:
        chat_id = udB.get_key("LOG_CHANNEL")
        LOGS.info("Customising Ur Assistant Bot in @BOTFATHER")
        UL = f"@{asst.me.username}"
        sir = (
            f"@{ultroid_bot.me.username}"
            if ultroid_bot.me.username
            else ultroid_bot.me.first_name
        )
        file = choice(
            [
                "https://graph.org/file/92cd6dbd34b0d1d73a0da.jpg",
                "https://graph.org/file/a97973ee0425b523cdc28.jpg",
            ]
        )
        file, _ = await download_file(file, "profile.jpg")
        msg = await asst.send_message(
            chat_id, "**Auto Customisation** Started on @Botfather"
        )
        for command in ["/cancel", "/setuserpic"]:
            await send_and_wait(command)
        isdone = (await ultroid_bot.get_messages("botfather", limit=1))[0].text
        if isdone.startswith("Invalid bot"):
            LOGS.info("Error while trying to customise assistant, skipping...")
            return
        for cmd in [
            UL,
            file,
            "/setabouttext",
            UL,
            f"✨ Hello ✨!! I'm Assistant Bot of {sir}",
            "/setdescription",
            UL,
            f"✨ Powerful Ultroid Assistant Bot ✨\n✨ Master ~ {sir} ✨\n\n✨ Powered By ~ @TeamUltroid ✨",
        ]:
            await send_and_wait(cmd)
        await ultroid_bot.send_message(
            "botfather",
        )
        await msg.edit("Completed **Auto Customisation** at @BotFather.")
        os.remove(file)
        LOGS.info("Customisation Done")
    except Exception as e:
        LOGS.exception(e)
