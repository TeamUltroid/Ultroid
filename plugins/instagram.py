# Ultroid - UserBot
# Copyright (C) 2021 TeamUltroid
#
# This file is a part of < https://github.com/TeamUltroid/Ultroid/ >
# PLease read the GNU Affero General Public License in
# <https://www.github.com/TeamUltroid/Ultroid/blob/main/LICENSE/>.

"""
✘ Commands Available -

• `{i}instadl <Instagram Url>`
  `Download Instagram Media...`

"""

import os
from . import *
from instagrapi import Client

CLIENT = []

def create_client(username, password):
  try:
    return CLIENT[0]
  except IndexError:
    cl = Client()
    cl.login(username, password)
    CLIENT.append(cl)
    return cl
  

@ultroid_cmd(pattern="instadl ?(.*)")
async def insta_dl(e):
  match = e.pattern_match.group(1)
  replied = await e.get_reply_message()
  if match:
    text = match
  elif e.is_reply and "insta" in replied.message:
    text = replied.message
  else:
    return await eor(e, "Provide a Link to Download...")
  un = udB.get("INSTA_USERNAME")
  up = udB.get("INSTA_PASSWORD")
  if un and up:
    try:
        CL = create_client(un, up)
        media = CL.video_download(CL.media_pk_from_url(text))
        await e.reply(f"**Uploaded Successfully\nLink :** {text}", file=media)
        await e.delete()
        os.remove(media)
        return
    except Exception as B:
        return await eor(e, B)
    if isinstance(e.media, types.MessageMediaWebPage) and isinstance(e.media.webpage, types.WebPage):
      photo = e.media.webpage.photo or e.media.webpage.document
      if not photo
        return await eor(e, "Please Fill `INSTA_USERNAME` and `INSTA_PASSWORD` to Use This Comamand!")
      return await e.reply(file=photo, f"**Link:{text}\n\nIf This Wasnt Excepted Result, Please Fill `INSTA_USERNAME` and `INSTA_PASSWORD`...")
    await eor(e, "Please Fill Instagram Credential to Use this Command...")
      
        

