# Ultroid - UserBot
# Copyright (C) 2020 TeamUltroid
#
# This file is a part of < https://github.com/TeamUltroid/Ultroid/ >
# PLease read the GNU Affero General Public License in
# <https://www.github.com/TeamUltroid/Ultroid/blob/main/LICENSE/>.

"""
✘ Commands Available -

• `{i}addsudo`
    Add Sudo Users by replying to user or using <space> separated userid(s)

• `{i}delsudo`
    Remove Sudo Users by replying to user or using <space> separated userid(s)

• `{i}listsudo`
    List all sudo users.
"""

import re

from telethon.tl.functions.users import GetFullUserRequest

from . import *


@ultroid_cmd(
    pattern="addsudo ?(.*)",
)
async def _(ult):
    if Var.BOT_MODE == True:
        try:
            if ult.sender_id != Var.OWNER_ID:
                return await eor(
                    ult, "You are sudo user, You cant add other sudo user."
                )
        except BaseException:
            pass
    else:
        if ult.sender_id != ultroid_bot.uid:
            return await eor(ult, "You are sudo user, You cant add other sudo user.")
    ok = await eor(ult, "`Updating SUDO Users List ...`")
    if ult.reply_to_msg_id:
        replied_to = await ult.get_reply_message()
        id = replied_to.sender.id
        user = await ult.client(GetFullUserRequest(int(id)))
        sed.append(id)
        if id == ultroid_bot.me.id:
            return await ok.edit("You cant add yourself as Sudo User...")
        elif is_sudo(id):
            return await ok.edit(
                f"[{user.user.first_name}](tg://user?id={id}) `is already a SUDO User ...`"
            )
        elif add_sudo(id):
            return await ok.edit(
                f"**Added [{user.user.first_name}](tg://user?id={id}) as SUDO User**"
            )
        else:
            return await ok.edit("`SEEMS LIKE THIS FUNCTION CHOOSE TO BROKE ITSELF`")

    args = ult.pattern_match.group(1).strip()

    if re.search(r"[\s]", args) is not None:
        args = args.split(" ")
        msg = ""
        sudos = get_sudos()
        for item in args:
            user = ""
            try:
                user = await ult.client(GetFullUserRequest(int(item)))
            except BaseException:
                pass
            if not hasattr(user, "user"):
                msg += f"• `{item}` __Invalid UserID__\n"
            elif item in sudos:
                msg += f"• [{user.user.first_name}](tg://user?id={item}) __Already a SUDO__\n"
            elif add_sudo(item.strip()):
                msg += (
                    f"• [{user.user.first_name}](tg://user?id={item}) __Added SUDO__\n"
                )
            else:
                msg += f"• `{item}` __Failed to Add SUDO__\n"
        return await ok.edit(f"**Adding Sudo Users :**\n{msg}")

    id = args.strip()
    user = ""

    try:
        user = await ult.client(GetFullUserRequest(int(i)))
    except BaseException:
        pass

    if not id.isdigit():
        return await ok.edit("`Integer(s) Expected`")
    elif not hasattr(user, "user"):
        return await ok.edit("`Invalid UserID`")
    elif is_sudo(id):
        return await ok.edit(
            f"[{user.user.first_name}](tg://user?id={id}) `is already a SUDO User ...`"
        )
    elif add_sudo(id):
        return await ok.edit(
            f"**Added [{user.user.first_name}](tg://user?id={id}) as SUDO User**"
        )
    else:
        return await ok.edit(f"**Failed to add `{id}` as SUDO User ... **")


@ultroid_cmd(
    pattern="delsudo ?(.*)",
)
async def _(ult):
    if Var.BOT_MODE == True:
        try:
            if ult.sender_id != Var.OWNER_ID:
                return await eor(
                    ult, "You are sudo user, You cant add other sudo user."
                )
        except BaseException:
            pass
    else:
        if ult.sender_id != ultroid_bot.uid:
            return await eor(ult, "You are sudo user, You cant add other sudo user.")
    ok = await eor(ult, "`Updating SUDO Users List ...`")
    if ult.reply_to_msg_id:
        replied_to = await ult.get_reply_message()
        id = replied_to.sender.id
        user = await ult.client(GetFullUserRequest(int(id)))
        sed.remove(id)
        if not is_sudo(id):
            return await ok.edit(
                f"[{user.user.first_name}](tg://user?id={id}) `wasn't a SUDO User ...`"
            )
        elif del_sudo(id):
            return await ok.edit(
                f"**Removed [{user.user.first_name}](tg://user?id={id}) from SUDO User(s)**"
            )
        else:
            return await ok.edit("`SEEMS LIKE THIS FUNCTION CHOOSE TO BREAK ITSELF`")

    args = ult.pattern_match.group(1)

    if re.search(r"[\s]", args) is not None:
        args = args.split(" ")
        msg = ""
        sudos = get_sudos()
        for item in args:
            user = ""
            try:
                user = await ult.client(GetFullUserRequest(int(item)))
            except BaseException:
                pass
            if not hasattr(user, "user"):
                msg += f"• `{item}` __Invalid UserID__\n"
            elif item in sudos and del_sudo(item):
                msg += (
                    f"• [{user.user.first_name}](tg://user?id={id}) __Removed SUDO__\n"
                )
            elif item not in sudos:
                msg += (
                    f"• [{user.user.first_name}](tg://user?id={id}) __Wasn't a SUDO__\n"
                )
            else:
                msg += f"• `{item}` __Failed to Remove SUDO__\n"
        return await ok.edit(msg)

    id = args.strip()
    user = ""

    try:
        user = await ult.client(GetFullUserRequest(int(i)))
    except BaseException:
        pass

    if not id.isdigit():
        return await ok.edit("`Integer(s) Expected`")
    elif not hasattr(user, "user"):
        return await ok.edit("`Invalid UserID`")
    elif not is_sudo(id):
        return await ok.edit(
            f"[{user.user.first_name}](tg://user?id={id}) wasn't a SUDO user ..."
        )
    elif del_sudo(id):
        return await ok.edit(
            f"**Removed [{user.user.first_name}](tg://user?id={id}) from SUDO User**"
        )
    else:
        return await ok.edit(f"**Failed to Remove `{id}` as SUDO User ... **")


@ultroid_cmd(
    pattern="listsudo$",
)
async def _(ult):
    ok = await eor(ult, "`...`")
    sudos = get_sudos()
    if "" in sudos:
        return await ok.edit("`No SUDO User was assigned ...`")
    msg = ""
    for i in sudos:
        user = ""
        try:
            user = await ok.client(GetFullUserRequest(int(i.strip())))
        except BaseException:
            pass
        if hasattr(user, "user"):
            msg += f"• [{user.user.first_name}](tg://user?id={i}) ( `{i}` )\n"
        else:
            msg += f"• `{i}` -> Invalid User\n"
    return await ok.edit(f"**List of SUDO Users :**\n{msg}")


HELP.update({f"{__name__.split('.')[1]}": f"{__doc__.format(i=HNDLR)}"})
