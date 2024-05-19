# Ultroid - UserBot
# Copyright (C) 2020-2023 TeamUltroid
#
# This file is a part of < https://github.com/TeamUltroid/Ultroid/ >
# PLease read the GNU Affero General Public License in
# <https://www.github.com/TeamUltroid/Ultroid/blob/main/LICENSE/>.

import shutil
from random import choice

from telethon import Button, events
from telethon.tl import functions, types  # pylint:ignore

from localization import get_string
from core import *
from core.decorators._decorators import ultroid_cmd
from utilities.misc import check_filename
from utilities.helper import *
from core.decorators import eor, eod
from core.decorators._assistant import in_pattern, asst_cmd, callback

LOG_CHANNEL = udB.get_config("LOG_CHANNEL")


def inline_pic(get=False):
    INLINE_PIC = udB.get_key("INLINE_PIC")
    if (INLINE_PIC is None) or get:
        # get default if required
        return "https://graph.org/file/8cd1817eb8a9be2436b3b.jpg"
    elif INLINE_PIC:
        return INLINE_PIC
    # is False, return None

udB.on("LOAD_ALL", "delete", lambda: shutil.rmtree("modules/addons"))

List = []
Dict = {}
# Credentials variable for saving login credentials(Like Gdrive,OneDrive,etc. login credentials) in local
creds = {}

# Chats, which needs to be ignore for some cases
# Considerably, there can be many
# Feel Free to Add Any other...

NOSPAM_CHAT = [
    -1001361294038,  # UltroidSupportChat
    -1001387666944,  # PyrogramChat
    -1001109500936,  # TelethonChat
    -1001050982793,  # Python
    -1001256902287,  # DurovsChat
]
