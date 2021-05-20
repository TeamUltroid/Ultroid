#Ultroid - UserBot
# Copyright (C) 2020 TeamUltroid
#
# This file is a part of < https://github.com/TeamUltroid/Ultroid/ >
# PLease read the GNU Affero General Public License in
# <https://www.github.com/TeamUltroid/Ultroid/blob/main/LICENSE/>.

"""
✘ Commands Available

•`{i}addecho`

•`{i}remecho`

•`{i}listecho`


"""

from pyUltroid.functions.echo_db import *
from . import *

@ultroid_cmd(pattern="addecho ?(.*)")
async def echo(e):
    r = await e.get_reply_message()
    if r:
        user = r.sender.id
    else:
        try:
            user = e.text.split()[1]
            if user.startswith("@"):
                ok = await ultroid_bot.get_entity(user)
                user = ok.id
            else:
                user = int(user)
        except BaseException:
            return await eor(e, "Reply To user")
    if check_echo(e.chat_id, user):
        return await eor(e, "echo already activated for this user.")
    add_echo(e.chat_id, user)
    await eor(e, "Activated Echo For this user.")
    
@ultroid_cmd(pattern="remecho ?(.*)") 
async def rm(e):
    r = await e.get_reply_message()
    if r:
        user = r.sender.id
    else:
        try:
            user = e.text.split()[1]
            if user.startswith("@"):
                ok = await ultroid_bot.get_entity(user)
                user = ok.id
            else:
                user = int(user)
        except BaseException:
            return await eor(e, "Reply To user")
    if check_echo(e.chat_id, user):
        rem_echo(e.chat_id, user)
        return await eor(e, "Deactivated Echo For user.")
    await eor(e, "echo not activated for this user")


@ultroid_bot.on(events.NewMessage(incoming=True))
async def okk(e):
    if check_echo(e.chat_id, e.sender.id):
        try:
            ok = await bot.get_messages(e.chat_id, ids=e.id)
            return await ultroid_bot.send_message(e.chat_id, ok, reply_to=e.id)
        except Exception as er:
            LOGS.info(er)
  
@ultroid_cmd(pattern="listecho$")
async def lstecho(e):
    k = list_echo(e.chat_id)
    if k:
        user = ""
        for x in k:
            user += "•" + str(x) + "\n"
        await eor(e, user)
    else:
        await eor(e, "Empty List")
      
HELP.update({f"{__name__.split('.')[1]}": f"{__doc__.format(i=HNDLR)}"})      