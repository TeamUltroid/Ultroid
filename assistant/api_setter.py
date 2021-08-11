# Ultroid - UserBot
# Copyright (C) 2021 TeamUltroid
#
# This file is a part of < https://github.com/TeamUltroid/Ultroid/ >
# PLease read the GNU Affero General Public License in
# <https://www.github.com/TeamUltroid/Ultroid/blob/main/LICENSE/>.

from . import *

# main menu for api setting


@callback("apiset")
@owner
async def apiset(event):
    await event.edit(
        get_string("ast_1"),
        buttons=[
            [Button.inline("Remove.bg API", data="rmbg")],
            [Button.inline("DEEP API", data="dapi")],
            [Button.inline("OCR API", data="oapi")],
            [Button.inline("« Back", data="setter")],
        ],
    )


@callback("rmbg")
@owner
async def rmbgapi(event):
    await event.delete()
    pru = event.sender_id
    var = "RMBG_API"
    name = "Remove.bg API Key"
    async with event.client.conversation(pru) as conv:
        await conv.send_message(get_string("ast_2"))
        response = conv.wait_event(events.NewMessage(chats=pru))
        response = await response
        themssg = response.message.message
        if themssg == "/cancel":
            return await conv.send_message(
                "Cancelled!!",
                buttons=get_back_button("apiset"),
            )
        await setit(event, var, themssg)
        await conv.send_message(
            f"{name} changed to {themssg}",
            buttons=get_back_button("apiset"),
        )


@callback("dapi")
@owner
async def rmbgapi(event):
    await event.delete()
    pru = event.sender_id
    var = "DEEP_API"
    name = "DEEP AI API Key"
    async with event.client.conversation(pru) as conv:
        await conv.send_message("Get Your Deep Api from deepai.org and send here.")
        response = conv.wait_event(events.NewMessage(chats=pru))
        response = await response
        themssg = response.message.message
        if themssg == "/cancel":
            return await conv.send_message(
                "Cancelled!!",
                buttons=get_back_button("apiset"),
            )
        await setit(event, var, themssg)
        await conv.send_message(
            f"{name} changed to {themssg}",
            buttons=get_back_button("apiset"),
        )


@callback("oapi")
@owner
async def rmbgapi(event):
    await event.delete()
    pru = event.sender_id
    var = "OCR_API"
    name = "OCR API Key"
    async with event.client.conversation(pru) as conv:
        await conv.send_message("Get Your OCR api from ocr.space Send Send Here.")
        response = conv.wait_event(events.NewMessage(chats=pru))
        response = await response
        themssg = response.message.message
        if themssg == "/cancel":
            return await conv.send_message(
                "Cancelled!!",
                buttons=get_back_button("apiset"),
            )
        await setit(event, var, themssg)
        await conv.send_message(
            f"{name} changed to {themssg}",
            buttons=get_back_button("apiset"),
        )
