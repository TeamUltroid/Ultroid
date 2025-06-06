# Ultroid - UserBot
# Copyright (C) 2021-2025 TeamUltroid
#
# This file is a part of < https://github.com/TeamUltroid/Ultroid/ >
# PLease read the GNU Affero General Public License in
# <https://www.github.com/TeamUltroid/Ultroid/blob/main/LICENSE/>.
"""
❍ Commands Available -

• `{i}destroy <reply to animated sticker>`
    To destroy the sticker.

• `{i}tiny <reply to media>`
    To create Tiny stickers.

• `{i}packkang <pack name>`
    Kang the Complete sticker set (with custom name).

• `{i}round <reply to any media>`
    To extract round sticker.
"""
import glob
import io
import os
import random
from os import remove

try:
    import cv2
except ImportError:
    cv2 = None
try:
    import numpy as np
except ImportError:
    np = None
try:
    from PIL import Image, ImageDraw
except ImportError:
    pass

from telethon.errors import PeerIdInvalidError, YouBlockedUserError
from telethon.tl.functions.messages import UploadMediaRequest
from telethon.tl.types import (
    DocumentAttributeFilename,
    DocumentAttributeSticker,
    InputPeerSelf,
)
from telethon.utils import get_input_document

from . import (
    KANGING_STR,
    LOGS,
    asst,
    async_searcher,
    bash,
    con,
    functions,
    get_string,
    inline_mention,
    mediainfo,
    ultroid_cmd,
    quotly,
    types,
    udB,
)


@ultroid_cmd(pattern="packkang")
async def pack_kangish(_):
    _e = await _.get_reply_message()
    local = None
    try:
        cmdtext = _.text.split(maxsplit=1)[1]
    except IndexError:
        cmdtext = None
    if cmdtext and os.path.isdir(cmdtext):
        local = True
    elif not (_e and _e.sticker and _e.file.mime_type == "image/webp"):
        return await _.eor(get_string("sts_4"))
    msg = await _.eor(get_string("com_1"))
    _packname = cmdtext or f"Ultroid Kang Pack By {_.sender_id}"
    typee = None
    if not local:
        _id = _e.media.document.attributes[1].stickerset.id
        _hash = _e.media.document.attributes[1].stickerset.access_hash
        _get_stiks = await _.client(
            functions.messages.GetStickerSetRequest(
                stickerset=types.InputStickerSetID(id=_id, access_hash=_hash), hash=0
            )
        )
        docs = _get_stiks.documents
    else:
        docs = []
        files = glob.glob(f"{cmdtext}/*")
        exte = files[-1]
        if exte.endswith(".tgs"):
            typee = "anim"
        elif exte.endswith(".webm"):
            typee = "vid"
        count = 0
        for file in files:
            if file.endswith((".tgs", ".webm")):
                count += 1
                upl = await asst.upload_file(file)
                docs.append(await asst(UploadMediaRequest(InputPeerSelf(), upl)))
                if count % 5 == 0:
                    await msg.edit(f"`Uploaded {count} files.`")

    stiks = []
    for i in docs:
        x = get_input_document(i)
        stiks.append(
            types.InputStickerSetItem(
                document=x,
                emoji=(
                    random.choice(["😐", "👍", "😂"])
                    if local
                    else (i.attributes[1]).alt
                ),
            )
        )
    try:
        short_name = "ult_" + _packname.replace(" ", "_") + str(_.id)
        _r_e_s = await asst(
            functions.stickers.CreateStickerSetRequest(
                user_id=_.sender_id,
                title=_packname,
                short_name=f"{short_name}_by_{asst.me.username}",
                animated=typee == "anim",
                videos=typee == "vid",
                stickers=stiks,
            )
        )
    except PeerIdInvalidError:
        return await msg.eor(
            f"Hey {inline_mention(_.sender)} send `/start` to @{asst.me.username} and later try this command again.."
        )
    except BaseException as er:
        LOGS.exception(er)
        return await msg.eor(str(er))
    await msg.eor(
        get_string("sts_5").format(f"https://t.me/addstickers/{_r_e_s.set.short_name}"),
    )


@ultroid_cmd(
    pattern="round$",
)
async def ultdround(event):
    ureply = await event.get_reply_message()
    xx = await event.eor(get_string("com_1"))
    if not (ureply and (ureply.media)):
        await xx.edit(get_string("sts_10"))
        return
    ultt = await ureply.download_media()
    file = await con.convert(
        ultt,
        convert_to="png",
        allowed_formats=["jpg", "jpeg", "png"],
        outname="round",
        remove_old=True,
    )
    img = Image.open(file).convert("RGB")
    npImage = np.array(img)
    h, w = img.size
    alpha = Image.new("L", img.size, 0)
    draw = ImageDraw.Draw(alpha)
    draw.pieslice([0, 0, h, w], 0, 360, fill=255)
    npAlpha = np.array(alpha)
    npImage = np.dstack((npImage, npAlpha))
    Image.fromarray(npImage).save("ult.webp")
    await event.client.send_file(
        event.chat_id,
        "ult.webp",
        force_document=False,
        reply_to=event.reply_to_msg_id,
    )
    await xx.delete()
    os.remove(file)
    os.remove("ult.webp")


@ultroid_cmd(
    pattern="destroy$",
)
async def ultdestroy(event):
    ult = await event.get_reply_message()
    if not (ult and ult.media and "animated" in mediainfo(ult.media)):
        return await event.eor(get_string("sts_2"))
    await event.client.download_media(ult, "ultroid.tgs")
    xx = await event.eor(get_string("com_1"))
    await bash("lottie_convert.py ultroid.tgs json.json")
    with open("json.json") as json:
        jsn = json.read()
    jsn = (
        jsn.replace("[100]", "[200]")
        .replace("[10]", "[40]")
        .replace("[-1]", "[-10]")
        .replace("[0]", "[15]")
        .replace("[1]", "[20]")
        .replace("[2]", "[17]")
        .replace("[3]", "[40]")
        .replace("[4]", "[37]")
        .replace("[5]", "[60]")
        .replace("[6]", "[70]")
        .replace("[7]", "[40]")
        .replace("[8]", "[37]")
        .replace("[9]", "[110]")
    )
    open("json.json", "w").write(jsn)
    file = await con.animated_sticker("json.json", "ultroid.tgs")
    if file:
        await event.client.send_file(
            event.chat_id,
            file="ultroid.tgs",
            force_document=False,
            reply_to=event.reply_to_msg_id,
        )
    await xx.delete()
    os.remove("json.json")


@ultroid_cmd(
    pattern="tiny$",
)
async def ultiny(event):
    reply = await event.get_reply_message()
    if not (reply and (reply.media)):
        await event.eor(get_string("sts_10"))
        return
    xx = await event.eor(get_string("com_1"))
    ik = await reply.download_media()
    im1 = Image.open("resources/extras/ultroid_blank.png")
    if ik.endswith(".tgs"):
        await con.animated_sticker(ik, "json.json")
        with open("json.json") as json:
            jsn = json.read()
        jsn = jsn.replace("512", "2000")
        open("json.json", "w").write(jsn)
        await con.animated_sticker("json.json", "ult.tgs")
        file = "ult.tgs"
        os.remove("json.json")
    elif ik.endswith((".gif", ".webm", ".mp4")):
        iik = cv2.VideoCapture(ik)
        dani, busy = iik.read()
        cv2.imwrite("i.png", busy)
        fil = "i.png"
        im = Image.open(fil)
        z, d = im.size
        if z == d:
            xxx, yyy = 200, 200
        else:
            t = z + d
            a = z / t
            b = d / t
            aa = (a * 100) - 50
            bb = (b * 100) - 50
            xxx = 200 + 5 * aa
            yyy = 200 + 5 * bb
        k = im.resize((int(xxx), int(yyy)))
        k.save("k.png", format="PNG", optimize=True)
        im2 = Image.open("k.png")
        back_im = im1.copy()
        back_im.paste(im2, (150, 0))
        back_im.save("o.webp", "WEBP", quality=95)
        file = "o.webp"
        os.remove(fil)
        os.remove("k.png")
    else:
        im = Image.open(ik)
        z, d = im.size
        if z == d:
            xxx, yyy = 200, 200
        else:
            t = z + d
            a = z / t
            b = d / t
            aa = (a * 100) - 50
            bb = (b * 100) - 50
            xxx = 200 + 5 * aa
            yyy = 200 + 5 * bb
        k = im.resize((int(xxx), int(yyy)))
        k.save("k.png", format="PNG", optimize=True)
        im2 = Image.open("k.png")
        back_im = im1.copy()
        back_im.paste(im2, (150, 0))
        back_im.save("o.webp", "WEBP", quality=95)
        file = "o.webp"
        os.remove("k.png")
    if os.path.exists(file):
        await event.client.send_file(
            event.chat_id, file, reply_to=event.reply_to_msg_id
        )
        os.remove(file)
    await xx.delete()
    os.remove(ik)
