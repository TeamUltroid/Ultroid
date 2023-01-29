# Ultroid - UserBot
# Copyright (C) 2021-2022 TeamUltroid
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

• `{i}poto <username>/reply`
  `{i}poto <reply/upload-limit>/all`

  Ex: `{i}poto 10` - uploads starting 10 pfps of user.
    Upload the photo of Chat/User if Available.
"""

import contextlib
import os

from telethon.tl.functions.account import UpdateProfileRequest
from telethon.tl.functions.photos import DeletePhotosRequest, UploadProfilePhotoRequest

from .. import eor, get_string, mediainfo, ultroid_cmd

TMP_DOWNLOAD_DIRECTORY = "resources/downloads/"

# bio changer


@ultroid_cmd(pattern="setbio( (.*)|$)", fullsudo=True)
async def _(ult):
    ok = await ult.eor("...")
    set = ult.pattern_match.group(1).strip()
    try:
        await ult.client(UpdateProfileRequest(about=set))
        await ok.eor(f"Profile bio changed to\n`{set}`")
    except Exception as ex:
        await ok.eor(f"Error occured.\n`{str(ex)}`")


# name changer


@ultroid_cmd(pattern="setname ?((.|//)*)", fullsudo=True)
async def _(ult):
    ok = await ult.eor("...")
    names = first_name = ult.pattern_match.group(1).strip()
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
        await ok.eor(f"Name changed to `{names}`")
    except Exception as ex:
        await ok.eor(f"Error occured.\n`{str(ex)}`")


# profile pic


@ultroid_cmd(pattern="setpic$", fullsudo=True)
async def _(ult):
    if not ult.is_reply:
        return await ult.eor("`Reply to a Media..`", time=5)
    reply_message = await ult.get_reply_message()
    ok = await ult.eor(get_string("com_1"))
    replfile = await reply_message.download_media()
    file = await ult.client.upload_file(replfile)
    try:
        if "pic" in mediainfo(reply_message.media):
            await ult.client(UploadProfilePhotoRequest(file))
        else:
            await ult.client(UploadProfilePhotoRequest(video=file))
        await ok.eor("`My Profile Photo has Successfully Changed !`")
    except Exception as ex:
        await ok.eor(f"Error occured.\n`{str(ex)}`")
    os.remove(replfile)


# delete profile pic(s)


@ultroid_cmd(pattern="delpfp( (.*)|$)", fullsudo=True)
async def remove_profilepic(delpfp):
    ok = await delpfp.eor("`...`")
    group = delpfp.text[8:]
    if group == "all":
        lim = 0
    elif group.isdigit():
        lim = int(group)
    else:
        lim = 1
    pfplist = await delpfp.client.get_profile_photos("me", limit=lim)
    await delpfp.client(DeletePhotosRequest(pfplist))
    await ok.eor(f"`Successfully deleted {len(pfplist)} profile picture(s).`")


@ultroid_cmd(pattern="poto( (.*)|$)")
async def gpoto(e):
    ult = e.pattern_match.group(1).strip()

    if e.is_reply:
        gs = await e.get_reply_message()
        user_id = gs.sender_id
    elif ult:
        split = ult.split()
        user_id = split[0]
        ult = ult[-1] if len(ult) > 1 else None
    else:
        user_id = e.chat_id

    a = await e.eor(get_string("com_1"))
    limit = None

    just_dl = ult in ["-dl", "--dl"]
    if just_dl:
        ult = None

    if ult and ult != "all":
        with contextlib.suppress(ValueError):
            limit = int(ult)
    if not limit or e.client._bot:
        okla = await e.client.download_profile_photo(user_id)
    else:
        okla = []
        if limit == "all":
            limit = None
        async for photo in e.client.iter_profile_photos(user_id, limit=limit):
            photo_path = await e.client.download_media(photo)
            if photo.video_sizes:
                await e.respond(file=photo_path)
                os.remove(photo_path)
            else:
                okla.append(photo_path)
    if not okla:
        return await a.eor("`Pfp Not Found...`")
    if not just_dl:
        await a.delete()
        await e.reply(file=okla)
        if not isinstance(okla, list):
            okla = [okla]
        for file in okla:
            os.remove(file)
        return
    if isinstance(okla, list):
        okla = "\n".join(okla)
    await a.edit(f"Downloaded pfp to [ `{okla}` ].")
