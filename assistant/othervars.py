# Ultroid - UserBot
# Copyright (C) 2020 TeamUltroid
#
# This file is a part of < https://github.com/TeamUltroid/Ultroid/ >
# PLease read the GNU Affero General Public License in
# <https://www.github.com/TeamUltroid/Ultroid/blob/main/LICENSE/>.

from . import *

# main menuu for setting other vars


@callback("otvars")
@owner
async def otvaar(event):
    await event.edit(
        "Other Variables to set for @TheUltroid:",
        buttons=[
            [Button.inline("Tag Logger", data="taglog")],
            [Button.inline("PM Permit", data="pmset")],
            [Button.inline("SuperFban", data="sfban")],
            [Button.inline("« Back", data="setter")],
        ],
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
            await conv.send_message("{} changed to {}".format(name, themssg))


@callback("pmset")
@owner
async def pmset(event):
    await event.edit(
        "PMPermit Settings:",
        buttons=[
            [Button.inline("Turn PMPermit On", data="pmon")],
            [Button.inline("Turn PMPermit Off", data="pmoff")],
            [Button.inline("« Back", data="otvars")],
        ],
    )


@callback("pmon")
@owner
async def pmonn(event):
    var = "PMSETTING"
    await setit(event, var, "True")
    await event.edit(f"Done! PMPermit has been turned on!! Please `{hndlr}restart`")


@callback("pmoff")
@owner
async def pmofff(event):
    var = "PMSETTING"
    await setit(event, var, "False")
    await event.edit(f"Done! PMPermit has been turned off!! Please `{hndlr}restart`")


@callback("sfban")
@owner
async def sfban(event):
    await event.edit(
        "SuperFban Settings:",
        buttons=[
            [Button.inline("FBan Group", data="sfgrp")],
            [Button.inline("Exclude Feds", data="sfexf")],
            [Button.inline("« Back", data="otvars")],
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
            await conv.send_message("{} changed to {}".format(name, themssg))


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
            await conv.send_message("{} changed to {}".format(name, themssg))
