# Ultroid - UserBot
# Copyright (C) 2021 TeamUltroid
#
# This file is a part of < https://github.com/TeamUltroid/Ultroid/ >
# PLease read the GNU Affero General Public License in
# <https://www.github.com/TeamUltroid/Ultroid/blob/main/LICENSE/>.
"""
✘ Commands Available -

• `{i}instadl <Instagram Url>`
  `Download Instagram Media...`

• `{i}instadata <username>`
  `Get Instagram Data of someone or self`

• Fill `INSTA_USERNAME` and `INSTA_PASSWORD`
  before using it..
"""

import os


from . import *


@ultroid_cmd(pattern="instadl ?(.*)")
async def insta_dl(e):
    match = e.pattern_match.group(1)
    replied = await e.get_reply_message()
    tt = await eor(e, get_string("com_1"))
    if match:
        text = match
    elif e.is_reply and "insta" in replied.message:
        text = replied.message
    else:
        return await eor(tt, "Provide a Link to Download...")

    CL = await create_instagram_client(un, up)
    if CL:
        try:
            media = CL.video_download(CL.media_pk_from_url(text))
            await e.reply(f"**Uploaded Successfully\nLink :** {text}", file=media)
            await tt.delete()
            os.remove(media)
            return
        except Exception as B:
            LOGS.exception(B)
            return await eor(tt, str(B))
    if isinstance(e.media, types.MessageMediaWebPage) and isinstance(
        e.media.webpage, types.WebPage
    ):
        photo = e.media.webpage.photo or e.media.webpage.document
        if not photo:
            return await eor(
                tt,
                "Please Fill `INSTA_USERNAME` and `INSTA_PASSWORD` to Use This Comamand!",
            )
        await tt.delete()
        return await e.reply(
            f"**Link** :{text}\n\nIf This Wasnt Excepted Result, Please Fill `INSTA_USERNAME` and `INSTA_PASSWORD`...",
            file=photo,
        )
    await eor(tt, "Please Fill Instagram Credential to Use this Command...")


@ultroid_cmd(pattern="instadata ?(.*)")
async def soon_(e):
    cl = await create_instagram_client(e)
    if not cl:
        return await eor(e, "`Please Fill Instagram Credentials to Use This...`")
    match = e.pattern_match.group(1)
    ew = await eor(e, get_string("com_1"))
    if match:
        try:
            iid = cl.user_id_from_username(match)
            data = cl.user_info(iid)
        except Exception as g:
            return await eor(ew, f"**ERROR** : `{g}`")
    else:
        data = cl.account_info()
        data = cl.user_info(data.pk)
    photo = data.profile_pic_url
    unam = "https://instagram.com/" + data.username
    msg = f"• **Full Name** : __{data.full_name}__"
    msg += f"\n• **UserName** : [@{data.username}]({unam})"
    msg += f"\n• **Verified** : {data.is_verified}"
    msg += f"\n• **Posts Count** : {data.media_count}"
    msg += f"\n• **Followers** : {data.follower_count}"
    msg += f"\n• **Following** : {data.following_count}"
    msg += f"\n• **Category** : {data.category_name}"
    await e.reply(
        msg,
        file=photo,
        force_document=True,
        attributes=[types.DocumentAttributeFilename("InstaUltroid.jpg")],
    )
    await ew.delete()
