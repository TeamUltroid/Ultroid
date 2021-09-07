
import os
import re

from pyUltroid.functions.filter_db import *
from telegraph import upload_file as uf
from telethon.tl.types import User
from telethon.utils import pack_bot_file_id

from . import *


@ultroid_cmd(pattern="gmail ?(.*)")
async def af(e):
    wrd = (e.pattern_match.group(1)).lower()
    username = await e.get_reply_message()
    chat = e.chat_id
    if not (username and wrd):
        return await eor(e, "`Use this command word to set as filter and reply...`")
   if username.text:
        def dot_trick(username):
    emails = list()
    username_length = len(username)
    combinations = pow(2, username_length - 1)
    padding = "{0:0" + str(username_length - 1) + "b}"
    for i in range(0, combinations):
        bin = padding.format(i)
        full_email = ""

        for j in range(0, username_length - 1):
            full_email += (username[j]);
            if bin[j] == "1":
                full_email += "."
        full_email += (username[j + 1])
        emails.append(full_email + "@gmail.com")
    return emails



username = username
await eor(*dot_trick(username) , sep="\n")
        
