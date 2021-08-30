from pyUltroid.functions.vc_group import *

from . import *


@vc_asst("authg", from_users=[udB["OWNER_ID"], *sudoers()], vc_auth=False)
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
    await eor(f"• Added to AUTH Groups Successfully For `{kem}`.")


@vc_asst("remauth", from_users=[udB["OWNER_ID"], *sudoers()], vc_auth=False)
async def auth_group(event):
    chat = event.chat_id
    gc, ad = check_vcauth(chat)
    if not gc:
        return await eor(event, "Chat is Not in Vc Auth list...")
    rem_vcauth(chat)
    await eor(event, "Removed Chat from Vc AUTH Groups!")
