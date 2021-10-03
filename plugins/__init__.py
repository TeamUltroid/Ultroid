# Ultroid - UserBot
# Copyright (C) 2021 TeamUltroid
#
# This file is a part of < https://github.com/TeamUltroid/Ultroid/ >
# PLease read the GNU Affero General Public License in
# <https://www.github.com/TeamUltroid/Ultroid/blob/main/LICENSE/>.

import asyncio
import os
import time
from random import choice

from pyUltroid import *
from pyUltroid.dB import ULTROID_IMAGES
from pyUltroid.functions.helper import *
from pyUltroid.functions.info import *
from pyUltroid.functions.misc import *
from pyUltroid.functions.tools import *
from pyUltroid.misc._assistant import asst_cmd, callback, in_pattern
from pyUltroid.misc._decorators import ultroid_cmd
from pyUltroid.misc._wrappers import eod, eor
from pyUltroid.version import __version__, ultroid_version
from telegraph import Telegraph
from telethon import Button, events
from telethon.tl import functions, types

from strings import get_string

Redis = udB.get

OWNER_NAME = ultroid_bot.me.first_name
OWNER_ID = ultroid_bot.me.id
LOG_CHANNEL = int(udB.get("LOG_CHANNEL"))
INLINE_PIC = udB.get("INLINE_PIC") or choice(ULTROID_IMAGES)
Ttoken = udB.get("_TELEGRAPH_TOKEN")
Telegraph = Telegraph(Ttoken)

if not Ttoken:
    short_name = OWNER_NAME if len(OWNER_NAME) < 32 else "Ultroid"
    author_name = short_name
    author_url = (
        f"https://t.me/{ultroid_bot.me.username}" if ultroid_bot.me.username else None
    )
    Telegraph.create_account(
        short_name=short_name, author_name=author_name, author_url=author_url
    )
    udB.set("_TELEGRAPH_TOKEN", Telegraph.get_access_token())

List = []
Dict = {}
N = 0

STUFF = {}

# Chats, which needs to be ignore for some cases
# Considerably, there can be many
# Feel Free to Add Any other...

NOSPAM_CHAT = [
    -1001327032795,  # UltroidSupport
    -1001387666944,  # PyrogramChat
    -1001109500936,  # TelethonChat
    -1001050982793,  # Python
    -1001256902287,  # DurovsChat
]

KANGING_STR = [
    "Using Witchery to kang this sticker...",
    "Plagiarising hehe...",
    "Inviting this sticker over to my pack...",
    "Kanging this sticker...",
    "Hey that's a nice sticker!\nMind if I kang?!..",
    "Hehe me stel ur stiker...",
    "Ay look over there (☉｡☉)!→\nWhile I kang this...",
    "Roses are red violets are blue, kanging this sticker so my pack looks cool",
    "Imprisoning this sticker...",
    "Mr.Steal-Your-Sticker is stealing this sticker... ",
]
