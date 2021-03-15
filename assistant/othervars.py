# Ultroid - UserBot
# Copyright (C) 2020 TeamUltroid
#
# This file is a part of < https://github.com/TeamUltroid/Ultroid/ >
# PLease read the GNU Affero General Public License in
# <https://www.github.com/TeamUltroid/Ultroid/blob/main/LICENSE/>.

from . import *

TOKEN_FILE = "resources/auths/auth_token.txt"


@callback("authorise")
@owner
async def _(e):
    if not e.is_private:
        return
    if not udB.get("GDRIVE_CLIENT_ID"):
        return await e.edit(
            "Client ID and Secret is Empty.\nFill it First.",
            buttons=Button.inline("Back", data="gdrive"),
        )
    storage = await create_token_file(TOKEN_FILE, e)
    authorize(TOKEN_FILE, storage)
    f = open(TOKEN_FILE, "r")
    token_file_data = f.read()
    udB.set("GDRIVE_TOKEN", token_file_data)
    await e.reply(
        "`Success!\nYou are all set to use Google Drive with Ultroid Userbot.`",
        buttons=Button.inline("Main Menu", data="setter"),
    )


@callback("folderid")
@owner
async def _(e):
    if not e.is_private:
        return
    await e.edit(
        "Send your FOLDER ID\n\n"
        + "For FOLDER ID:\n"
        + "1. Open Google Drive App.\n"
        + "2. Create Folder.\n"
        + "3. Make that folder public.\n"
        + "4. Copy link of that folder."
        + "5. Send all characters which is after id= ."
    )
    async with ultroid_bot.asst.conversation(e.sender_id) as conv:
        reply = conv.wait_event(events.NewMessage(from_users=e.sender_id))
        repl = await reply
        udB.set("GDRIVE_FOLDER_ID", repl.text)
        await repl.reply(
            "Success Now You Can Authorise.",
            buttons=Button.inline("« Back", data="gdrive"),
        )


@callback("clientsec")
@owner
async def _(e):
    if not e.is_private:
        return
    await e.edit("Send your CLIENT SECRET")
    async with ultroid_bot.asst.conversation(e.sender_id) as conv:
        reply = conv.wait_event(events.NewMessage(from_users=e.sender_id))
        repl = await reply
        udB.set("GDRIVE_CLIENT_SECRET", repl.text)
        await repl.reply(
            "Success!\nNow You Can Authorise or add FOLDER ID.",
            buttons=Button.inline("« Back", data="gdrive"),
        )


@callback("clientid")
@owner
async def _(e):
    if not e.is_private:
        return
    await e.edit("Send your CLIENT ID ending with .com")
    async with ultroid_bot.asst.conversation(e.sender_id) as conv:
        reply = conv.wait_event(events.NewMessage(from_users=e.sender_id))
        repl = await reply
        if not repl.text.endswith(".com"):
            return await repl.reply("`Wrong CLIENT ID`")
        udB.set("GDRIVE_CLIENT_ID", repl.text)
        await repl.reply(
            "Success now set CLIENT SECRET",
            buttons=Button.inline("« Back", data="gdrive"),
        )


@callback("gdrive")
@owner
async def _(e):
    if not e.is_private:
        return
    await e.edit(
        "Go [here](https://console.developers.google.com/flows/enableapi?apiid=drive) and get your CLIENT ID and CLIENT SECRET",
        buttons=[
            [
                Button.inline("Cʟɪᴇɴᴛ Iᴅ", data="clientid"),
                Button.inline("Cʟɪᴇɴᴛ Sᴇᴄʀᴇᴛ", data="clientsec"),
            ],
            [
                Button.inline("Fᴏʟᴅᴇʀ Iᴅ", data="folderid"),
                Button.inline("Aᴜᴛʜᴏʀɪsᴇ", data="authorise"),
            ],
            [Button.inline("« Bᴀᴄᴋ", data="otvars")],
        ],
        link_preview=False,
    )


@callback("otvars")
@owner
async def otvaar(event):
    await event.edit(
        "Other Variables to set for @TheUltroid:",
        buttons=[
            [
                Button.inline("Tᴀɢ Lᴏɢɢᴇʀ", data="taglog"),
                Button.inline("SᴜᴘᴇʀFʙᴀɴ", data="sfban"),
            ],
            [
                Button.inline("Sᴜᴅᴏ Mᴏᴅᴇ", data="sudo"),
                Button.inline("Hᴀɴᴅʟᴇʀ", data="hhndlr"),
            ],
            [
                Button.inline("Exᴛʀᴀ Pʟᴜɢɪɴs", data="plg"),
                Button.inline("Aᴅᴅᴏɴs", data="eaddon"),
            ],
            [
                Button.inline("Eᴍᴏᴊɪ ɪɴ Hᴇʟᴘ", data="emoj"),
                Button.inline("Sᴇᴛ ɢDʀɪᴠᴇ", data="gdrive"),
            ],
            [Button.inline("« Bᴀᴄᴋ", data="setter")],
        ],
    )


@callback("emoj")
@owner
async def emoji(event):
    await event.delete()
    pru = event.sender_id
    var = "EMOJI_IN_HELP"
    name = f"Emoji in `{HNDLR}help` menu"
    async with event.client.conversation(pru) as conv:
        await conv.send_message("Send emoji u want to set 🙃.\n\nUse /cancel to cancel.")
        response = conv.wait_event(events.NewMessage(chats=pru))
        response = await response
        themssg = response.message.message
        if themssg == "/cancel":
            return await conv.send_message("Cancelled!!")
        elif themssg.startswith(("/", HNDLR)):
            return await conv.send_message("Incorrect Emoji")
        else:
            await setit(event, var, themssg)
            await conv.send_message(
                "{} changed to {}\n".format(name, themssg),
                buttons=[Button.inline("« Bᴀᴄᴋ", data="otvars")],
            )


@callback("plg")
@owner
async def pluginch(event):
    await event.delete()
    pru = event.sender_id
    var = "PLUGIN_CHANNEL"
    name = "Plugin Channel"
    async with event.client.conversation(pru) as conv:
        await conv.send_message(
            "Send id or username of a channel from where u want to install all plugins\n\nOur Channel~ @ultroidplugins\n\nUse /cancel to cancel."
        )
        response = conv.wait_event(events.NewMessage(chats=pru))
        response = await response
        themssg = response.message.message
        if themssg == "/cancel":
            return await conv.send_message("Cancelled!!")
        elif themssg.startswith(("/", HNDLR)):
            return await conv.send_message("Incorrect channel")
        else:
            await setit(event, var, themssg)
            await conv.send_message(
                "{} changed to {}\n After Setting All Things Do Restart".format(
                    name, themssg
                ),
                buttons=[Button.inline("« Bᴀᴄᴋ", data="otvars")],
            )


@callback("hhndlr")
@owner
async def hndlrr(event):
    await event.delete()
    pru = event.sender_id
    var = "HNDLR"
    name = "Handler/ Trigger"
    async with event.client.conversation(pru) as conv:
        await conv.send_message(
            f"Send The Symbol Which u want as Handler/Trigger to use bot\nUr Current Handler is [ `{HNDLR}` ]\n\n use /cancel to cancel."
        )
        response = conv.wait_event(events.NewMessage(chats=pru))
        response = await response
        themssg = response.message.message
        if themssg == "/cancel":
            return await conv.send_message("Cancelled!!")
        elif len(themssg) > 1:
            return await conv.send_message("Incorrect Handler")
        elif themssg.startswith(("/", "#", "@")):
            return await conv.send_message("Incorrect Handler")
        else:
            await setit(event, var, themssg)
            await conv.send_message(
                "{} changed to {}".format(name, themssg),
                buttons=[Button.inline("« Bᴀᴄᴋ", data="otvars")],
            )


@callback("taglog")
@owner
async def tagloggerr(event):
    await event.delete()
    pru = event.sender_id
    var = "TAG_LOG"
    name = "Tag Log Group"
    async with event.client.conversation(pru) as conv:
        await conv.send_message(
            f"Make a group, add your assistant and make it admin.\nGet the `{hndlr}id` of that group and send it here for tag logs.\n\nUse /cancel to cancel."
        )
        response = conv.wait_event(events.NewMessage(chats=pru))
        response = await response
        themssg = response.message.message
        if themssg == "/cancel":
            return await conv.send_message("Cancelled!!")
        else:
            await setit(event, var, themssg)
            await conv.send_message(
                "{} changed to {}".format(name, themssg),
                buttons=[Button.inline("« Bᴀᴄᴋ", data="otvars")],
            )


@callback("eaddon")
@owner
async def pmset(event):
    await event.edit(
        "ADDONS~ Extra Plugins:",
        buttons=[
            [Button.inline("Aᴅᴅᴏɴs  Oɴ", data="edon")],
            [Button.inline("Aᴅᴅᴏɴs  Oғғ", data="edof")],
            [Button.inline("« Bᴀᴄᴋ", data="otvars")],
        ],
    )


@callback("edon")
@owner
async def eddon(event):
    var = "ADDONS"
    await setit(event, var, "True")
    await event.edit(
        "Done! ADDONS has been turned on!!\n\n After Setting All Things Do Restart",
        buttons=[Button.inline("« Bᴀᴄᴋ", data="eaddon")],
    )


@callback("edof")
@owner
async def eddof(event):
    var = "ADDONS"
    await setit(event, var, "False")
    await event.edit(
        "Done! ADDONS has been turned off!! After Setting All Things Do Restart",
        buttons=[Button.inline("« Bᴀᴄᴋ", data="eaddon")],
    )


@callback("sudo")
@owner
async def pmset(event):
    await event.edit(
        f"SUDO MODE ~ Some peoples can use ur Bot which u selected. To know More use `{HNDLR}help sudo`",
        buttons=[
            [Button.inline("Sᴜᴅᴏ Mᴏᴅᴇ  Oɴ", data="onsudo")],
            [Button.inline("Sᴜᴅᴏ Mᴏᴅᴇ  Oғғ", data="ofsudo")],
            [Button.inline("« Bᴀᴄᴋ", data="otvars")],
        ],
    )


@callback("onsudo")
@owner
async def eddon(event):
    var = "SUDO"
    await setit(event, var, "True")
    await event.edit(
        "Done! SUDO MODE has been turned on!!\n\n After Setting All Things Do Restart",
        buttons=[Button.inline("« Bᴀᴄᴋ", data="sudo")],
    )


@callback("ofsudo")
@owner
async def eddof(event):
    var = "SUDO"
    await setit(event, var, "False")
    await event.edit(
        "Done! SUDO MODE has been turned off!! After Setting All Things Do Restart",
        buttons=[Button.inline("« Bᴀᴄᴋ", data="sudo")],
    )


@callback("sfban")
@owner
async def sfban(event):
    await event.edit(
        "SuperFban Settings:",
        buttons=[
            [Button.inline("FBᴀɴ Gʀᴏᴜᴘ", data="sfgrp")],
            [Button.inline("Exᴄʟᴜᴅᴇ Fᴇᴅs", data="sfexf")],
            [Button.inline("« Bᴀᴄᴋ", data="otvars")],
        ],
    )


@callback("sfgrp")
@owner
async def sfgrp(event):
    await event.delete()
    name = "FBan Group ID"
    var = "FBAN_GROUP_ID"
    pru = event.sender_id
    async with asst.conversation(pru) as conv:
        await conv.send_message(
            f"Make a group, add @MissRose_Bot, send `{hndlr}id`, copy that and send it here.\nUse /cancel to go back."
        )
        response = conv.wait_event(events.NewMessage(chats=pru))
        response = await response
        themssg = response.message.message
        if themssg == "/cancel":
            return await conv.send_message("Cancelled!!")
        else:
            await setit(event, var, themssg)
            await conv.send_message(
                "{} changed to {}".format(name, themssg),
                buttons=[Button.inline("« Bᴀᴄᴋ", data="sfban")],
            )


@callback("sfexf")
@owner
async def sfexf(event):
    await event.delete()
    name = "Excluded Feds"
    var = "EXCLUDE_FED"
    pru = event.sender_id
    async with asst.conversation(pru) as conv:
        await conv.send_message(
            f"Send the Fed IDs you want to exclude in the ban. Split by a space.\neg`id1 id2 id3`\nSet is as `None` if you dont want any.\nUse /cancel to go back."
        )
        response = conv.wait_event(events.NewMessage(chats=pru))
        response = await response
        themssg = response.message.message
        if themssg == "/cancel":
            return await conv.send_message("Cancelled!!")
        else:
            await setit(event, var, themssg)
            await conv.send_message(
                "{} changed to {}".format(name, themssg),
                buttons=[Button.inline("« Bᴀᴄᴋ", data="sfban")],
            )

# Ultroid - UserBot
# Copyright (C) 2020 TeamUltroid
#
# This file is a part of < https://github.com/TeamUltroid/Ultroid/ >
# PLease read the GNU Affero General Public License in
# <https://www.github.com/TeamUltroid/Ultroid/blob/main/LICENSE/>.

import os

from telegraph import Telegraph
from telegraph import upload_file as upl

from . import *

# --------------------------------------------------------------------#
telegraph = Telegraph()
r = telegraph.create_account(short_name="Ultroid")
auth_url = r["auth_url"]
# --------------------------------------------------------------------#


@callback("alvcstm")
@owner
async def alvcs(event):
    await event.edit(
        "Customise your {}alive. Choose from the below options -".format(HNDLR),
        buttons=[
            [Button.inline("Aʟɪᴠᴇ Tᴇxᴛ", data="alvtx")],
            [Button.inline("Aʟɪᴠᴇ ᴍᴇᴅɪᴀ", data="alvmed")],
            [Button.inline("Dᴇʟᴇᴛᴇ Aʟɪᴠᴇ Mᴇᴅɪᴀ", data="delmed")],
            [Button.inline("« Bᴀᴄᴋ", data="setter")],
        ],
    )


@callback("alvtx")
@owner
async def name(event):
    await event.delete()
    pru = event.sender_id
    var = "ALIVE_TEXT"
    name = "Alive Text"
    async with event.client.conversation(pru) as conv:
        await conv.send_message(
            "**Alive Text**\nEnter the new alive text.\n\nUse /cancel to terminate the operation."
        )
        response = conv.wait_event(events.NewMessage(chats=pru))
        response = await response
        themssg = response.message.message
        if themssg == "/cancel":
            return await conv.send_message("Cancelled!!")
        else:
            await setit(event, var, themssg)
            await conv.send_message(
                "{} changed to {}\n\nAfter Setting All Things Do restart".format(
                    name, themssg
                )
            )


@callback("alvmed")
@owner
async def media(event):
    await event.delete()
    pru = event.sender_id
    var = "ALIVE_PIC"
    name = "Alive Media"
    async with event.client.conversation(pru) as conv:
        await conv.send_message(
            "**Alive Media**\nSend me a pic/gif/bot api id of sticker to set as alive media.\n\nUse /cancel to terminate the operation."
        )
        response = await conv.get_response()
        try:
            themssg = response.message.message
            if themssg == "/cancel":
                return await conv.send_message("Operation cancelled!!")
        except BaseException:
            pass
        media = await event.client.download_media(response, "alvpc")
        if (
            not (response.text).startswith("/")
            and not response.text == ""
            and not response.media
        ):
            url = response.text
        else:
            try:
                x = upl(media)
                url = f"https://telegra.ph/{x[0]}"
                os.remove(media)
            except BaseException:
                return await conv.send_message("Terminated.")
        await setit(event, var, url)
        await conv.send_message("{} has been set.".format(name))


@callback("delmed")
@owner
async def dell(event):
    try:
        udB.delete("ALIVE_PIC")
        return await event.edit("Done!")
    except BaseException:
        return await event.edit("Something went wrong...")


@callback("pmcstm")
@owner
async def alvcs(event):
    await event.edit(
        "Customise your PMPERMIT Settings -",
        buttons=[
            [
                Button.inline("Pᴍ Tᴇxᴛ", data="pmtxt"),
                Button.inline("Pᴍ Mᴇᴅɪᴀ", data="pmmed"),
            ],
            [
                Button.inline("Aᴜᴛᴏ Aᴘᴘʀᴏᴠᴇ", data="apauto"),
                Button.inline("PMLOGGER", data="pml"),
            ],
            [
                Button.inline("Sᴇᴛ Wᴀʀɴs", data="swarn"),
                Button.inline("Dᴇʟᴇᴛᴇ Pᴍ Mᴇᴅɪᴀ", data="delpmmed"),
            ],
            [Button.inline("« Bᴀᴄᴋ", data="pmset")],
        ],
    )


@callback("pmtxt")
@owner
async def name(event):
    await event.delete()
    pru = event.sender_id
    var = "PM_TEXT"
    name = "PM Text"
    async with event.client.conversation(pru) as conv:
        await conv.send_message(
            "**PM Text**\nEnter the new Pmpermit text.\n\nu can use `{name}` `{fullname}` `{count}` `{mention}` `{username}` to get this from user Too\n\nUse /cancel to terminate the operation."
        )
        response = conv.wait_event(events.NewMessage(chats=pru))
        response = await response
        themssg = response.message.message
        if themssg == "/cancel":
            return await conv.send_message("Cancelled!!")
        else:
            await setit(event, var, themssg)
            await conv.send_message(
                "{} changed to {}\n\nAfter Setting All Things Do restart".format(
                    name, themssg
                )
            )


@callback("swarn")
@owner
async def name(event):
    m = range(1, 10)
    tultd = [Button.inline(f"{x}", data=f"wrns_{x}") for x in m]
    lst = list(zip(tultd[::3], tultd[1::3], tultd[2::3]))
    lst.append([Button.inline("« Bᴀᴄᴋ", data="pmcstm")])
    await event.edit(
        "Select the number of warnings for a user before getting blocked in PMs.",
        buttons=lst,
    )


@callback(re.compile(b"wrns_(.*)"))
@owner
async def set_wrns(event):
    value = int(event.data_match.group(1).decode("UTF-8"))
    dn = udB.set("PMWARNS", value)
    if dn:
        await event.edit(
            f"PM Warns Set to {value}.\nNew users will have {value} chances in PMs before getting banned."
        )
    else:
        await event.edit(f"Something went wrong, please check your {hndlr}logs!")


@callback("pmmed")
@owner
async def media(event):
    await event.delete()
    pru = event.sender_id
    var = "PMPIC"
    name = "PM Media"
    async with event.client.conversation(pru) as conv:
        await conv.send_message(
            "**PM Media**\nSend me a pic/gif/bot api id of sticker to set as pmpermit media.\n\nUse /cancel to terminate the operation."
        )
        response = await conv.get_response()
        try:
            themssg = response.message.message
            if themssg == "/cancel":
                return await conv.send_message("Operation cancelled!!")
        except BaseException:
            pass
        media = await event.client.download_media(response, "pmpc")
        if (
            not (response.text).startswith("/")
            and not response.text == ""
            and not response.media
        ):
            url = response.text
        else:
            try:
                x = upl(media)
                url = f"https://telegra.ph/{x[0]}"
                os.remove(media)
            except BaseException:
                return await conv.send_message("Terminated.")
        await setit(event, var, url)
        await conv.send_message("{} has been set.".format(name))


@callback("delpmmed")
@owner
async def dell(event):
    try:
        udB.delete("PMPIC")
        return await event.edit("Done!")
    except BaseException:
        return await event.edit("Something went wrong...")


@callback("apauto")
@owner
async def apauto(event):
    await event.edit(
        "This'll auto approve on outgoing messages",
        buttons=[
            [Button.inline("Aᴜᴛᴏ Aᴘᴘʀᴏᴠᴇ ON", data="apon")],
            [Button.inline("Aᴜᴛᴏ Aᴘᴘʀᴏᴠᴇ OFF", data="apof")],
            [Button.inline("« Bᴀᴄᴋ", data="pmcstm")],
        ],
    )


@callback("apon")
@owner
async def apon(event):
    var = "AUTOAPPROVE"
    await setit(event, var, "True")
    await event.edit(f"Done!! AUTOAPPROVE  Started!!")


@callback("apof")
@owner
async def apof(event):
    try:
        udB.delete("AUTOAPPROVE")
        return await event.edit("Done! AUTOAPPROVE Stopped!!")
    except BaseException:
        return await event.edit("Something went wrong...")


@callback("pml")
@owner
async def alvcs(event):
    await event.edit(
        "PMLOGGER This Will Forward Ur Pm to Ur Private Group -",
        buttons=[
            [Button.inline("PMLOGGER ON", data="pmlog")],
            [Button.inline("PMLOGGER OFF", data="pmlogof")],
            [Button.inline("« Bᴀᴄᴋ", data="pmcstm")],
        ],
    )


@callback("pmlog")
@owner
async def pmlog(event):
    var = "PMLOG"
    await setit(event, var, "True")
    await event.edit(f"Done!! PMLOGGER  Started!!")


@callback("pmlogof")
@owner
async def pmlogof(event):
    try:
        udB.delete("PMLOG")
        return await event.edit("Done! PMLOGGER Stopped!!")
    except BaseException:
        return await event.edit("Something went wrong...")


@callback("ppmset")
@owner
async def pmset(event):
    await event.edit("PMPermit Settings:",
         buttons=[
            [Button.inline("Tᴜʀɴ PMPᴇʀᴍɪᴛ Oɴ", data="pmon")],
            [Button.inline("Tᴜʀɴ PMPᴇʀᴍɪᴛ Oғғ", data="pmoff")],
            [Button.inline("Cᴜsᴛᴏᴍɪᴢᴇ PMPᴇʀᴍɪᴛ", data="pmcstm")],
            [Button.inline("« Bᴀᴄᴋ", data="setter")],
        ],
    )


@callback("pmon")
@owner
async def pmonn(event):
    var = "PMSETTING"
    await setit(event, var, "True")
    await event.edit(f"Done! PMPermit has been turned on!!")


@callback("pmoff")
@owner
async def pmofff(event):
    var = "PMSETTING"
    await setit(event, var, "False")
    await event.edit(f"Done! PMPermit has been turned off!!")
