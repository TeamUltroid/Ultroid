# Ultroid - UserBot
# Copyright (C) 2021 TeamUltroid
#
# This file is a part of < https://github.com/TeamUltroid/Ultroid/ >
# PLease read the GNU Affero General Public License in
# <https://www.github.com/TeamUltroid/Ultroid/blob/main/LICENSE/>.

"""
✘ Commands Available -

• `{i}addauth` `add Complete Chat for Voice chat. `
  `{i}addauth admins` - `allow only Chat Admin to Use Vc`

• `{i}remauth`
   Remove chat from Vc Auth.

• `{i}listauth`
   Get All Vc Authorised Chat..
"""

from pyUltroid.functions.vc_group import *

from . import *


@vc_asst("addauth", from_users=[udB["OWNER_ID"], *sudoers()], vc_auth=False)
async def auth_group(event):
    try:
        key = event.text.split(" ", maxsplit=1)[1]
        admins = bool("admins" in key)
    except IndexError:
        admins = True
    chat = event.chat_id
    cha, adm = check_vcauth(chat)
    if cha and adm == admins:
        return await event.reply("Already Authed This Chat!")
    add_vcauth(chat, admins=admins)
    kem = "Admins" if admins else "All"
    await eor(event, f"• Added to AUTH Groups Successfully For `{kem}`.")


@vc_asst("remauth", from_users=[udB["OWNER_ID"], *sudoers()], vc_auth=False)
async def auth_group(event):
    chat = event.chat_id
    gc, ad = check_vcauth(chat)
    if not gc:
        return await eor(event, "Chat is Not in Vc Auth list...")
    rem_vcauth(chat)
    await eor(event, "Removed Chat from Vc AUTH Groups!")

@vc_asst("listauth", from_users=[udB["OWNER_ID"], *sudoers()], vc_auth=False)
async def listVc(e):
    chats = get_chats()
    if not chats:
        return await eor(e, "• Vc Auth List is Empty..")
    text = "• Vc Auth Chats\n\n"
    for on in chats.keys():
        st = "Admins" if chats[on]["admins"] else "All"
        title = (await e.client.get_entity(on)).title
        text += f"∆ **{title}** [`{on}`] - {st}"
    await eor(e, text)
