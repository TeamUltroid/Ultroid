# Ultroid - UserBot
# Copyright (C) 2021 TeamUltroid
#
# This file is a part of < https://github.com/TeamUltroid/Ultroid/ >
# PLease read the GNU Affero General Public License in
# <https://www.github.com/TeamUltroid/Ultroid/blob/main/LICENSE/>.
"""
✘ Commands Available -

• `{i}superfban <reply to user/userid/username>`
    FBan the person across all feds in which you are admin.

• `{i}superunfban <reply to user/userid/username>`
    Un-FBan the person across all feds in which you are admin.

Specify FBan Group and Feds to exclude in the assistant.

• `{i}fstat <username/id/reply to user>`
    Collect fed stat of the person in Rose.

• `{i}fedinfo <(fedid)>`
    Collect federation info of the given fed id, or of the fed you own, from Rose.
"""
import asyncio
import os

from pyUltroid.dB import DEVLIST
from telethon.errors.rpcerrorlist import YouBlockedUserError

from . import eor, get_string, get_user_id, udB, ultroid_bot, ultroid_cmd

bot = "@MissRose_bot"


@ultroid_cmd(
    pattern="superfban ?(.*)",
)
async def _(event):
    msg = await eor(event, get_string("sf_1"))
    inputt = event.pattern_match.group(1)
    if event.reply_to_msg_id:
        FBAN = (await event.get_reply_message()).sender_id
        if inputt:
            REASON = inputt
    elif inputt:
        REASON = "#TBMassBanned"
        arg = event.text.split()
        if len(arg) == 2:
            FBAN = await get_user_id(arg[1])
        elif len(arg) > 2:
            FBAN = await get_user_id(arg[1])
            REASON = event.text.split(maxsplit=2)[-1]
        else:
            return await msg.edit(get_string("sf_22"))

    if FBAN in DEVLIST:
        return await msg.edit("The user is my Dev and cannot be FBanned!")

    if udB.get("FBAN_GROUP_ID"):
        chat = int(udB.get("FBAN_GROUP_ID"))
    else:
        chat = await event.get_chat()
    fedList = []
    if not fedList:
        for a in range(3):
            async with event.client.conversation("@MissRose_bot") as bot_conv:
                await bot_conv.send_message("/start")
                await asyncio.sleep(3)
                await bot_conv.send_message("/myfeds")
                await asyncio.sleep(3)
                try:
                    response = await bot_conv.get_response()
                except asyncio.exceptions.TimeoutError:
                    return await msg.edit(
                        get_string("sf_4"),
                    )
                await asyncio.sleep(3)
                if "make a file" in response.text or "Looks like" in response.text:
                    await response.click(0)
                    await asyncio.sleep(3)
                    fedfile = await bot_conv.get_response()
                    await asyncio.sleep(3)
                    if fedfile.media:
                        downloaded_file_name = await ultroid_bot.download_media(
                            fedfile,
                            "fedlist",
                        )
                        await asyncio.sleep(6)
                        file = open(downloaded_file_name, errors="ignore")
                        lines = file.readlines()
                        for line in lines:
                            try:
                                fedList.append(line[:36])
                            except BaseException:
                                pass
                    elif get_string("sf_5") in (await bot_conv.get_edit):
                        return await msg.edit(get_string("sf_6"))
                if not fedList:
                    await msg.edit(
                        f"Unable to collect FedAdminList. Retrying ({a+1}/3)...",
                    )
                else:
                    break
        else:
            await msg.edit(get_string("sf_8"))
        In = False
        tempFedId = ""
        for x in response.text:
            if x == "`":
                if In:
                    In = False
                    fedList.append(tempFedId)
                    tempFedId = ""
                else:
                    In = True
            elif In:
                tempFedId += x
    if not fedList:
        return await msg.edit(get_string("sf_9"))
    await msg.edit(f"FBaning in {len(fedList)} feds.")
    try:
        await ultroid_bot.send_message(chat, "/start")
    except BaseException:
        return await msg.edit(get_string("sf_11"))
    await asyncio.sleep(3)
    if udB.get("EXCLUDE_FED"):
        excludeFed = udB.get("EXCLUDE_FED").split(" ")
        for num, item in enumerate(excludeFed):
            excludeFed[num] = item.strip()
    exCount = 0
    for fed in fedList:
        if udB.get("EXCLUDE_FED") and fed in excludeFed:
            await ultroid_bot.send_message(chat, f"{fed} Excluded.")
            exCount += 1
            continue
        await event.client.send_message(chat, f"/joinfed {fed}")
        await asyncio.sleep(3)
        await event.client.send_message(chat, f"/fban {FBAN} {REASON}")
        await asyncio.sleep(3)
    try:
        os.remove("fedlist")
    except Exception as e:
        print(f"Error in removing FedAdmin file.\n{e}")
    await msg.edit(
        f"SuperFBan Completed.\nTotal Feds - {len(fedList)}.\nExcluded - {exCount}.\nAffected {len(fedList) - exCount} feds.\n#TB",
    )


@ultroid_cmd(
    pattern="superunfban ?(.*)",
)
async def _(event):
    msg = await eor(event, get_string("sf_15"))
    fedList = []
    if event.reply_to_msg_id:
        previous_message = await event.get_reply_message()
        if previous_message.media:
            downloaded_file_name = await ultroid_bot.download_media(
                previous_message,
                "fedlist",
            )
            file = open(downloaded_file_name, encoding="utf8")
            lines = file.readlines()
            for line in lines:
                try:
                    fedList.append(line[:36])
                except BaseException:
                    pass
            arg = event.text.split(" ", maxsplit=2)
            FBAN = arg[1]
            REASON = arg[2] if len(arg) > 2 else ""
        else:
            FBAN = previous_message.sender_id
            try:
                REASON = event.text.split(" ", maxsplit=1)[1]
            except BaseException:
                REASON = ""
            if REASON.strip() == "":
                REASON = ""
    else:
        arg = event.text.split(" ", maxsplit=2)
        if len(arg) > 2:
            try:
                FBAN = arg[1]
                REASON = arg[2]
            except BaseException:
                return await msg.edit(get_string("sf_2"))
        else:
            try:
                FBAN = arg[1]
                REASON = " #TBMassUnBanned "
            except BaseException:
                return await msg.edit(get_string("sf_2"))
    if udB.get("FBAN_GROUP_ID"):
        chat = int(udB.get("FBAN_GROUP_ID"))
    else:
        chat = await event.get_chat()
    if not fedList:
        for a in range(3):
            async with event.client.conversation("@MissRose_bot") as bot_conv:
                await bot_conv.send_message("/start")
                await asyncio.sleep(3)
                await bot_conv.send_message("/myfeds")
                await asyncio.sleep(3)
                try:
                    response = await bot_conv.get_response()
                except asyncio.exceptions.TimeoutError:
                    return await msg.edit(
                        get_string("sf_4"),
                    )
                await asyncio.sleep(3)
                if "make a file" in response.text or "Looks like" in response.text:
                    await response.click(0)
                    await asyncio.sleep(3)
                    fedfile = await bot_conv.get_response()
                    await asyncio.sleep(3)
                    if fedfile.media:
                        downloaded_file_name = await ultroid_bot.download_media(
                            fedfile,
                            "fedlist",
                        )
                        await asyncio.sleep(6)
                        file = open(downloaded_file_name, errors="ignore")
                        lines = file.readlines()
                        for line in lines:
                            try:
                                fedList.append(line[:36])
                            except BaseException:
                                pass
                    elif get_string("sf_5") in (await bot_conv.get_edit):
                        return await msg.edit(get_string("sf_6"))
                if not fedList:
                    await msg.edit(
                        f"Unable to collect FedAdminList. Retrying ({a+1}/3)...",
                    )
                else:
                    break
        else:
            await msg.edit(get_string("sf_8"))
        In = False
        tempFedId = ""
        for x in response.text:
            if x == "`":
                if In:
                    In = False
                    fedList.append(tempFedId)
                    tempFedId = ""
                else:
                    In = True
            elif In:
                tempFedId += x
    if not fedList:
        return await msg.edit(get_string("sf_9"))
    await msg.edit(f"UnFBaning in {len(fedList)} feds.")
    try:
        await event.client.send_message(chat, "/start")
    except BaseException:
        return await msg.edit(get_string("sf_11"))
    await asyncio.sleep(3)
    if udB.get("EXCLUDE_FED"):
        excludeFed = udB.get("EXCLUDE_FED").split(" ")
        for n, m in enumerate(excludeFed):
            excludeFed[n] = excludeFed[n].strip()
    exCount = 0
    for fed in fedList:
        if udB.get("EXCLUDE_FED") and fed in excludeFed:
            await event.client.send_message(chat, f"{fed} Excluded.")
            exCount += 1
            continue
        await ultroid_bot.send_message(chat, f"/joinfed {fed}")
        await asyncio.sleep(3)
        await ultroid_bot.send_message(chat, f"/unfban {FBAN} {REASON}")
        await asyncio.sleep(3)
    try:
        os.remove("fedlist")
    except Exception as e:
        print(f"Error in removing FedAdmin file.\n{e}")
    await msg.edit(
        f"SuperUnFBan Completed.\nTotal Feds - {len(fedList)}.\nExcluded - {exCount}.\n Affected {len(fedList) - exCount} feds.\n#TB",
    )


@ultroid_cmd(
    pattern="fstat ?(.*)",
)
async def _(event):
    ok = await eor(event, "`Checking...`")
    if event.reply_to_msg_id:
        previous_message = await event.get_reply_message()
        sysarg = str(previous_message.sender_id)
        user = f"[user](tg://user?id={sysarg})"
        if event.pattern_match.group(1):
            sysarg += f" {event.pattern_match.group(1)}"
    else:
        sysarg = event.pattern_match.group(1)
        user = sysarg
    if sysarg == "":
        await ok.edit(
            get_string("sf_17"),
        )
    else:
        async with event.client.conversation(bot) as conv:
            try:
                await conv.send_message("/start")
                await conv.get_response()
                await conv.send_message("/fedstat " + sysarg)
                audio = await conv.get_response()
                if audio.message.startswith("This command can only be used once"):
                    await ok.edit(
                        "Oops, you can use this command only once every minute!",
                    )
                elif "Looks like" in audio.text:
                    await audio.click(0)
                    await asyncio.sleep(2)
                    audio = await conv.get_response()
                    await event.client.send_file(
                        event.chat_id,
                        audio,
                        caption=f"List of feds {user} has been banned in.\n\nCollected using Ultroid.",
                        link_preview=False,
                    )
                    await ok.delete()
                else:
                    okk = await conv.get_edit()
                    await ok.edit(okk.message)
                await ultroid_bot.send_read_acknowledge(bot)
            except YouBlockedUserError:
                await ok.edit("**Error**\n `Unblock` @MissRose_Bot `and try again!")


@ultroid_cmd(
    pattern="fedinfo ?(.*)",
)
async def _(event):
    ok = await event.edit(get_string("sf_20"))
    sysarg = event.pattern_match.group(1)
    async with event.client.conversation(bot) as conv:
        try:
            await conv.send_message("/start")
            await conv.get_response()
            await conv.send_message("/fedinfo " + sysarg)
            audio = await conv.get_response()
            await event.client.send_read_acknowledge(bot)
            await ok.edit(audio.text + "\n\nFedInfo Extracted by Ultroid")
        except YouBlockedUserError:
            await ok.edit("**Error**\n `Unblock` @MissRose_Bot `and try again!")
