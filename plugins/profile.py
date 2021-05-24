# Ultroid - UserBot
# Copyright (C) 2020 TeamUltroid
#
# This file is a part of < https://github.com/TeamUltroid/Ultroid/ >
# PLease read the GNU Affero General Public License in
# <https://www.github.com/TeamUltroid/Ultroid/blob/main/LICENSE/>.

"""
✘ Commands Available -

• `{i}setname <first name // last name>`
    Change your profile name.

• `{i}setbio <bio>`
    Change your profile bio.

• `{i}setpic <reply to pic>`
    Change your profile pic.

• `{i}delpfp <n>(optional)`
    Delete one profile pic, if no value given, else delete n number of pics.

• `{i}poto <username>`
    Upload the photo of Chat/User if Available.
"""

import asyncio
import os

from telethon.tl.functions.account import UpdateProfileRequest
from telethon.tl.functions.photos import (
    DeletePhotosRequest,
    GetUserPhotosRequest,
    UploadProfilePhotoRequest,
)
from telethon.tl.types import InputPhoto

from . import *

TMP_DOWNLOAD_DIRECTORY = "resources/downloads/"

# bio changer


@ultroid_cmd(
    pattern="setbio ?(.*)",
)
async def _(ult):
    if not e.out and not is_fullsudo(e.sender_id):
        return await eod(e, "`This Command Is Sudo Restricted.`")
    ok = await eor(ult, "...")
    set = ult.pattern_match.group(1)
    try:
        await ultroid_bot(UpdateProfileRequest(about=set))
        await ok.edit(f"Profile bio changed to\n`{set}`")
    except Exception as ex:
        await ok.edit("Error occured.\n`{}`".format(str(ex)))
    await asyncio.sleep(10)
    await ok.delete()


# name changer


@ultroid_cmd(
    pattern="setname ?((.|//)*)",
)
async def _(ult):
    if not e.out and not is_fullsudo(e.sender_id):
        return await eod(e, "`This Command Is Sudo Restricted.`")
    ok = await eor(ult, "...")
    names = ult.pattern_match.group(1)
    first_name = names
    last_name = ""
    if "//" in names:
        first_name, last_name = names.split("//", 1)
    try:
        await ultroid_bot(
            UpdateProfileRequest(
                first_name=first_name,
                last_name=last_name,
            ),
        )
        await ok.edit(f"Name changed to `{names}`")
    except Exception as ex:
        await ok.edit("Error occured.\n`{}`".format(str(ex)))
    await asyncio.sleep(10)
    await ok.delete()


# profile pic


@ultroid_cmd(
    pattern="setpic$",
)
async def _(ult):
    if not e.out and not is_fullsudo(e.sender_id):
        return await eod(e, "`This Command Is Sudo Restricted.`")
    ok = await eor(ult, "...")
    reply_message = await ult.get_reply_message()
    await ok.edit("`Downloading that picture...`")
    if not os.path.isdir(TMP_DOWNLOAD_DIRECTORY):
        os.makedirs(TMP_DOWNLOAD_DIRECTORY)
    photo = None
    try:
        photo = await ultroid_bot.download_media(reply_message, TMP_DOWNLOAD_DIRECTORY)
    except Exception as ex:
        await ok.edit("Error occured.\n`{}`".format(str(ex)))
    else:
        if photo:
            await ok.edit("`Uploading it to my profile...`")
            file = await ultroid_bot.upload_file(photo)
            try:
                await ultroid_bot(UploadProfilePhotoRequest(file))
            except Exception as ex:
                await ok.edit("Error occured.\n`{}`".format(str(ex)))
            else:
                await ok.edit("`My profile picture has been changed !`")
    await asyncio.sleep(10)
    await ok.delete()
    try:
        os.remove(photo)
    except Exception as ex:
        LOGS.exception(ex)


# delete profile pic(s)


@ultroid_cmd(
    pattern="delpfp ?(.*)",
)
async def remove_profilepic(delpfp):
    if not e.out and not is_fullsudo(e.sender_id):
        return await eod(e, "`This Command Is Sudo Restricted.`")
    ok = await eor(delpfp, "...")
    group = delpfp.text[8:]
    if group == "all":
        lim = 0
    elif group.isdigit():
        lim = int(group)
    else:
        lim = 1
    pfplist = await ultroid_bot(
        GetUserPhotosRequest(user_id=delpfp.from_id, offset=0, max_id=0, limit=lim),
    )
    input_photos = []
    for sep in pfplist.photos:
        input_photos.append(
            InputPhoto(
                id=sep.id,
                access_hash=sep.access_hash,
                file_reference=sep.file_reference,
            ),
        )
    await ultroid_bot(DeletePhotosRequest(id=input_photos))
    await ok.edit(f"`Successfully deleted {len(input_photos)} profile picture(s).`")
    await asyncio.sleep(10)
    await ok.delete()


@ultroid_cmd(pattern="poto ?(.*)")
async def gpoto(e):
    ult = e.pattern_match.group(1)
    a = await eor(e, "`Processing...`")
    if not ult and e.is_reply:
        gs = await e.get_reply_message()
        ult = gs.sender_id
    if not (ult or e.is_reply):
        ult = e.chat_id
    try:
        okla = await ultroid_bot.download_profile_photo(
            ult,
            "profile.jpg",
            download_big=True,
        )
        await a.delete()
        await ultroid_bot.send_message(e.chat_id, file=okla)
        os.remove(okla)
    except Exception as er:
        await eor(e, f"ERROR - {str(er)}")


HELP.update({f"{__name__.split('.')[1]}": f"{__doc__.format(i=HNDLR)}"})
