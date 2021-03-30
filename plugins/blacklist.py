# Ultroid - UserBot
# Copyright (C) 2020 TeamUltroid
#
# This file is a part of < https://github.com/TeamUltroid/Ultroid/ >
# PLease read the GNU Affero General Public License in
# <https://www.github.com/TeamUltroid/Ultroid/blob/main/LICENSE/>.

"""
✘ Commands Available -

"""

from pyUltroid.functions.blacklist_db import *
from . import *
import re


@ultroid_cmd(pattern="blacklist ?(.*)")
async def af(e):
    wrd = e.pattern_match.group(1)
    chat = e.chat_id
    if not (wrd):
       return await eor(e, "fuk off bici")
    wrd = e.text[10:]
    add_blacklist(int(chat), wrd)
    await eor(e, "done")
    
@ultroid_cmd(pattern="remblacklist ?(.*)")
async def rf(e):
    wrd = e.pattern_match.group(1)
    chat = e.chat_id
    if not wrd:
        return  await eor(e, "fuk off bici")
    rem_blacklist(int(chat), wrd)
    await eor(e, "done")


@ultroid_cmd(pattern="listblacklist")
async def lsnote(e):
    x = list_blacklist(e.chat_id)
    if x:
        sd = "Blacklist Found In This Chats Are\n\n"
        await eor(e, sd+x)
    else:
        await eor(e, "No Blacklist word Found Here")
        
        
@ultroid_bot.on(events.NewMessage(incoming=True))
async def bl(e):
    xx = e.text
    chat = e.chat_id
    x = get_blacklist(int(chat))
    if x and xx:
      if " " in xx:
          xx = xx.split(" ")
          for c in xx:
              try:
                  kk = re.search(str(c), str(x), flags=re.IGNORECASE)
              except:
                  pass
          try:     
              if kk:
                  await e.delete()
          except:
              pass
      else:
          k = re.search(xx, x, flags=re.IGNORECASE)
          if k:
              try:
                  await e.delete()
              except:
                  pass
                
HELP.update({f"{__name__.split('.')[1]}": f"{__doc__.format(i=Var.HNDLR)}"})
                