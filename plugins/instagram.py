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

import instagrapi

from . import *

CLIENT = []


def create_client(username, password):
    settings = {}
    if udB.get("INSTA_SET"):
        settings = eval(udB.get("INSTA_SET"))
    try:
        return CLIENT[0]
    except IndexError:
        cl = instagrapi.Client(settings)
        cl.login(username, password)
        CLIENT.append(cl)
        udB.set("INSTA_SET", str(cl.get_settings()))
        return cl


@ultroid_cmd(pattern="instadl ?(.*)")
async def insta_dl(e):
    match = e.pattern_match.group(1)
    replied = await e.get_reply_message()
    tt = await eor(e, "`Processing...`")
    if match:
        text = match
    elif e.is_reply and "insta" in replied.message:
        text = replied.message
    else:
        return await eor(tt, "Provide a Link to Download...")
    un = udB.get("INSTA_USERNAME")
    up = udB.get("INSTA_PASSWORD")
    if un and up:
        try:
            CL = create_client(un, up)
            media = CL.video_download(CL.media_pk_from_url(text))
            await e.reply(f"**Uploaded Successfully\nLink :** {text}", file=media)
            await tt.delete()
            os.remove(media)
            return
        except Exception as B:
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
    un = udB.get("INSTA_USERNAME")
    up = udB.get("INSTA_PASSWORD")
    if not un and up:
        return await eor(e, "`Please Fill Instagram Credentials to Use This...`")
    match = e.pattern_match.group(1)
    ew = await eor(e, "`Processing...`")
    try:
        cl = create_client(un, up)
    except Exception as g:
        return await eor(ew, str(g))
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
