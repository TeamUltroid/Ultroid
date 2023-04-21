# Ultroid - UserBot
# Copyright (C) 2021-2022 TeamUltroid
#
# This file is a part of < https://github.com/TeamUltroid/Ultroid/ >
# PLease read the GNU Affero General Public License in
# <https://www.github.com/TeamUltroid/Ultroid/blob/main/LICENSE/>.
"""
✘ Commands Available -

• `{i}qrcode <text/reply to text>`
   `Makes qrcode of text`

• `{i}addqr <reply image> <text>`
   `Makes qr of text and add it to image.`

• `{i}qrdecode <reply to qrcode>`
   `It decodes the qrcode.`
"""
import os

try:
    import cv2
except ImportError:
    cv2 = None

import qrcode
from PIL import Image
from telethon.tl.types import MessageMediaDocument as doc

from . import check_filename, get_string, ultroid_bot, ultroid_cmd


@ultroid_cmd(pattern="qrcode( (.*)|$)")
async def cd(e):
    reply = await e.get_reply_message()
    msg = e.pattern_match.group(1).strip()
    if reply and reply.text:
        msg = reply.text
    elif not msg:
        return await e.eor("`Give Some Text or Reply", time=5)
    cimg =  None
    if reply and (reply.sticker or reply.photo):
        cimg = await reply.download_media()
    elif ultroid_bot.me.photo and not ultroid_bot.me.photo.has_video:
        cimg = await e.client.get_profile_photos(ultroid_bot.uid, limit=1)[0]

    kk = await e.eor(get_string("com_1"))
    img = cimg or "resources/thumb.webp"
    ok = Image.open(img)
    logo = ok.resize((60, 60))
    cod = qrcode.QRCode(error_correction=qrcode.constants.ERROR_CORRECT_H)
    cod.add_data(msg)
    cod.make()
    imgg = cod.make_image().convert("RGB")
    pstn = ((imgg.size[0] - logo.size[0]) // 2, (imgg.size[1] - logo.size[1]) // 2)
    imgg.paste(logo, pstn)
    newname = check_filename("qr.jpg")
    imgg.save(newname)
    await e.client.send_file(e.chat_id, newname, supports_streaming=True)
    await kk.delete()
    os.remove(newname)
    if cimg:
        os.remove(cimg)


@ultroid_cmd(pattern="addqr( (.*)|$)")
async def qrwater(e):
    msg = e.pattern_match.group(1).strip()
    r = await e.get_reply_message()
    dl = await e.client.download_media(
        r, thumb=-1 if isinstance(r.media, doc) else None
    )
    if not dl:
        return await e.eor("`Reply Any Media and Give Text`", time=5)
    kk = await e.eor(get_string("com_1"))
    img_bg = Image.open(dl)
    qr = qrcode.QRCode(box_size=5)
    qr.add_data(msg)
    qr.make()
    img_qr = qr.make_image()
    pos = (img_bg.size[0] - img_qr.size[0], img_bg.size[1] - img_qr.size[1])
    img_bg.paste(img_qr, pos)
    img_bg.save(dl)
    await e.client.send_file(e.chat_id, dl, supports_streaming=True)
    await kk.delete()
    os.remove(dl)


@ultroid_cmd(pattern="qrdecode$")
async def decod(e):
    r = await e.get_reply_message()
    if not (r and r.media):
        return await e.eor("`Reply to Qrcode Media`", time=5)
    kk = await e.eor(get_string("com_1"))
    dl = await e.client.download_media(
        r, thumb=-1 if isinstance(r.media, doc) else None
    )
    if not dl:
        return
    im = cv2.imread(dl)
    try:
        det = cv2.QRCodeDetector()
        tx, y, z = det.detectAndDecode(im)
        await kk.edit("**Decoded Text:\n\n**" + tx)
    except BaseException:
        await kk.edit("`Reply To Media in Which Qr image present.`")
    os.remove(dl)