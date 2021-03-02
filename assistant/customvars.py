# Ultroid - UserBot
# Copyright (C) 2020 TeamUltroid
#
# This file is a part of < https://github.com/TeamUltroid/Ultroid/ >
# PLease read the GNU Affero General Public License in
# <https://www.github.com/TeamUltroid/Ultroid/blob/main/LICENSE/>.

import os

from telegraph import Telegraph, upload_file

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
        "Customise your {}alive. Choose from the below options -".format(Var.HNDLR),
        buttons=[
            [Button.inline("Aʟɪᴠᴇ Tᴇxᴛ", data="alvtx")],
            [Button.inline("Aʟɪᴠᴇ ᴍᴇᴅᴜᴀ", data="alvmed")],
            [Button.inline("Dᴇʟᴇᴛᴇ Aʟɪᴠᴇ Mᴇᴅɪᴀ", data="delmed")],
            [Button.inline("« Bᴀᴄᴋ", data="allcstms")],
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
                "{} changed to {}\n\nDo {}restart".format(name, themssg, Var.HNDLR)
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
        if not (response.text).startswith("/") and not response.text == "":
            url = response.text
        else:
            try:
                x = upload_file(media)
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
            [Button.inline("Pᴍ Tᴇxᴛ", data="pmtxt")],
            [Button.inline("Pᴍ Mᴇᴅɪᴀ", data="pmmed")],
            [Button.inline("PMLOGGER", data="pml")],
            [Button.inline("Dᴇʟᴇᴛᴇ Pᴍ Mᴇᴅɪᴀ", data="delpmmed")],
            [Button.inline("« Bᴀᴄᴋ", data="allcstms")],
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
            "**PM Text**\nEnter the new Pmpermit text.\n\nu can use `{name}` `{fullname}` `{count}` `{mention}` `{username}` Too\n\nUse /cancel to terminate the operation."
        )
        response = conv.wait_event(events.NewMessage(chats=pru))
        response = await response
        themssg = response.message.message
        if themssg == "/cancel":
            return await conv.send_message("Cancelled!!")
        else:
            await setit(event, var, themssg)
            await conv.send_message(
                "{} changed to {}\n\nDo {}restart".format(name, themssg, Var.HNDLR)
            )


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
        media = await event.client.download_media(response, "alvpcc")
        if not (response.text).startswith("/") and not response.text == "":
            url = response.text
        else:
            try:
                x = upload_file(media)
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
