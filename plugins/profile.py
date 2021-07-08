# Ultroid - UserBot
# Copyright (C) 2021 TeamUltroid
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
    if not ult.out and not is_fullsudo(ult.sender_id):
        return await eod(ult, "`This Command Is Sudo Restricted.`")
    ok = await eor(ult, "...")
    set = ult.pattern_match.group(1)
    try:
        await ult.client(UpdateProfileRequest(about=set))
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
    if not ult.out and not is_fullsudo(ult.sender_id):
        return await eod(ult, "`This Command Is Sudo Restricted.`")
    ok = await eor(ult, "...")
    names = ult.pattern_match.group(1)
    first_name = names
    last_name = ""
    if "//" in names:
        first_name, last_name = names.split("//", 1)
    try:
        await ult.client(
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
    if not ult.out and not is_fullsudo(ult.sender_id):
        return await eod(ult, "`This Command Is Sudo Restricted.`")
    if not ult.is_reply:
        return await eod(ult, "`Reply to a Media..`")
    reply_message = await ult.get_reply_message()
    ok = await eor(ult, "...")
    replfile = await reply_message.download_media()
    file = await ult.client.upload_file(replfile)
    mediain = mediainfo(reply_message.media)
    try:
        if "pic" in mediain:
            await ult.client(UploadProfilePhotoRequest(file))
        elif "gif" or "video" in mediain:
            await ult.client(UploadProfilePhotoRequest(video=file))
        else:
            return await ok.edit("`Invalid MEDIA Type !`")
        await ok.edit("`My Profile Photo has Successfully Changed !`")
    except Exception as ex:
        await ok.edit("Error occured.\n`{}`".format(str(ex)))
    os.remove(replfile)
    await asyncio.sleep(10)
    await ok.delete()


# delete profile pic(s)


@ultroid_cmd(
    pattern="delpfp ?(.*)",
)
async def remove_profilepic(delpfp):
    if not delpfp.out and not is_fullsudo(delpfp.sender_id):
        return await eod(delpfp, "`This Command Is Sudo Restricted.`")
    ok = await eor(delpfp, "...")
    group = delpfp.text[8:]
    if group == "all":
        lim = 0
    elif group.isdigit():
        lim = int(group)
    else:
        lim = 1
    pfplist = await delpfp.client(
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
    await delpfp.client(DeletePhotosRequest(id=input_photos))
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
        okla = await e.client.download_profile_photo(
            ult,
            "profile.jpg",
            download_big=True,
        )
        await a.delete()
        await e.reply(file=okla)
        os.remove(okla)
    except Exception as er:
        await eor(e, f"ERROR - {str(er)}")
