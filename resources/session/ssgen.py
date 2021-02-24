#!/bin/bash
# Ultroid - UserBot
# Copyright (C) 2020 TeamUltroid
#
# This file is a part of < https://github.com/TeamUltroid/Ultroid/ >
# PLease read the GNU Affero General Public License in
# <https://www.github.com/TeamUltroid/Ultroid/blob/main/LICENSE/>.

from telethon.sessions import StringSession
from telethon.sync import TelegramClient

print("Please ensure that you have your API ID and API HASH.")
print("")

API_ID = int(input("Enter API ID: "))
API_HASH = input("Enter API HASH: ")

with TelegramClient(StringSession(), API_ID, API_HASH) as client:
    ult = client.send_message("me",f"`{client.session.save()}`")
    ult.reply("The above is the `SESSION` for your current session.\nVisit @TheUltroid")
    print("")
    print("String Session for the current login has been generated.")
    print("Check your Telegram Saved messages for your SESSION.")
