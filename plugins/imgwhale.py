# Ultroid - UserBot
# Copyright (C) 2020 TeamUltroid
#
# This file is a part of < https://github.com/TeamUltroid/Ultroid/ >
# PLease read the GNU Affero General Public License in
# <https://www.github.com/TeamUltroid/Ultroid/blob/main/LICENSE/>.


"""
✘ Commands Available

• `{i}imgwhale`
    Upload image to https://ImgWhale.xyz !

- Optionally, You can add your ImgWhale API Key in `IMGWHALE_KEY` database var.
"""

from os import remove

from . import *


@ultroid_cmd(pattern="imgwhale")
async def imgwhale(event):
    msg = await event.eor(get_string("com_1"))
    reply = await event.get_reply_message()
    if not reply:
        return await msg.edit("`Reply to Image...`")
    if reply.photo:
        file = await reply.download_media()
    elif reply.document and reply.document.thumbs:
        file = await reply.download_media(thumb=-1)
    else:
        return await msg.edit("`Reply to Image...`")
    api_key = udB.get_key("IMGWHALE_KEY")
    extra = f"?key={api_key}" if api_key else ""
    post = await async_searcher(
        f"https://imgwhale.xyz/new{extra}",
        method="POST",
        data={"image": open(file, "rb")},
        re_json=True,
    )
    if post.get("error"):
        return await msg.edit(post["message"])
    await msg.edit(
        f"Successfully Uploaded to [ImgWhale](https://imgwhale.xyz/{post['fileId']})!",
        link_preview=True,
    )
    remove(file)
