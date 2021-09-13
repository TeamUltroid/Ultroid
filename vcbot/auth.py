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

• `{i}vcaccess <id/username/reply to msg>`
    Give access of Voice Chat Bot.

• `{i}rmvcaccess <id/username/reply to msg>`
    Remove access of Voice Chat Bot.

• `{i}listvcaccess`
    Get The List of People having vc access.
"""

from pyUltroid.functions.vc_group import *
from pyUltroid.functions.vc_sudos import add_vcsudo, del_vcsudo, get_vcsudos, is_vcsudo

from . import *


@vc_asst("addauth", from_users=owner_and_sudos(), vc_auth=False)
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
    await eor(
        event,
        f"• Added to AUTH Groups Successfully For <code>{kem}</code>.",
        parse_mode="html",
    )


@vc_asst("remauth", from_users=owner_and_sudos(), vc_auth=False)
async def auth_group(event):
    chat = event.chat_id
    gc, ad = check_vcauth(chat)
    if not gc:
        return await eor(event, "Chat is Not in Vc Auth list...")
    rem_vcauth(chat)
    await eor(event, "Removed Chat from Vc AUTH Groups!")


@vc_asst("listauth", from_users=owner_and_sudos(), vc_auth=False)
async def listVc(e):
    chats = get_chats()
    if not chats:
        return await eor(e, "• Vc Auth List is Empty..")
    text = "• <strong>Vc Auth Chats •</strong>\n\n"
    for on in chats.keys():
        st = "Admins" if chats[on]["admins"] else "All"
        title = (await e.client.get_entity(on)).title
        text += f"∆ <strong>{title}</strong> [ <code>{on}</code> ] : <code>{st}</code>"
    await eor(e, text, parse_mode="html")


@vc_asst("listvcaccess$", from_users=owner_and_sudos(), vc_auth=False)
async def _(e):
    xx = await eor(e, "`Getting Voice Chat Bot Users List...`")
    mm = get_vcsudos()
    pp = f"<strong>{len(mm)} Voice Chat Bot Approved Users</strong>\n"
    if len(mm) > 0:
        for m in mm:
            try:
                name = (await e.client.get_entity(int(m))).first_name
                pp += f"• <a href=tg://user?id={int(m)}>{name}</a>\n"
            except ValueError:
                pp += f"• <code>{int(m)} » No Info</code>\n"
    await xx.edit(pp, parse_mode="html")


@vc_asst("rmvcaccess ?(.*)", from_users=owner_and_sudos(), vc_auth=False)
async def _(e):
    xx = await eor(e, "`Disapproving to access Voice Chat features...`")
    input = e.pattern_match.group(1)
    if e.reply_to_msg_id:
        userid = (await e.get_reply_message()).sender_id
        name = (await e.client.get_entity(userid)).first_name
    elif input:
        try:
            userid = await get_user_id(input)
            name = (await e.client.get_entity(userid)).first_name
        except ValueError as ex:
            return await eor(xx, f"`{str(ex)}`", time=5)
    else:
        return await eor(xx, "`Reply to user's msg or add it's id/username...`", time=3)
    if not is_vcsudo(userid):
        return await eod(
            xx,
            f"[{name}](tg://user?id={userid})` is not approved to use my Voice Chat Bot.`",
            time=5,
        )
    try:
        del_vcsudo(userid)
        await eod(
            xx,
            f"[{name}](tg://user?id={userid})` is removed from Voice Chat Bot Users.`",
            time=5,
        )
    except Exception as ex:
        return await eor(xx, f"`{ex}`", time=5)


@vc_asst("vcaccess ?(.*)", from_users=owner_and_sudos(), vc_auth=False)
async def _(e):
    xx = await eor(e, "`Approving to access Voice Chat features...`")
    input = e.pattern_match.group(1)
    if e.reply_to_msg_id:
        userid = (await e.get_reply_message()).sender_id
        name = (await e.client.get_entity(userid)).first_name
    elif input:
        try:
            userid = await get_user_id(input)
            name = (await e.client.get_entity(userid)).first_name
        except ValueError as ex:
            return await eor(xx, f"`{str(ex)}`", time=5)
    else:
        return await eor(xx, "`Reply to user's msg or add it's id/username...`", time=3)
    if is_vcsudo(userid):
        return await eod(
            xx,
            f"[{name}](tg://user?id={userid})` is already approved to use my Voice Chat Bot.`",
            time=5,
        )
    try:
        add_vcsudo(userid)
        await eod(
            xx,
            f"[{name}](tg://user?id={userid})` is added to Voice Chat Bot Users.`",
            time=5,
        )
    except Exception as ex:
        return await eor(xx, f"`{ex}`", time=5)
