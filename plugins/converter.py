# Ultroid - UserBot
# Copyright (C) 2021 TeamUltroid
#
# This file is a part of < https://github.com/TeamUltroid/Ultroid/ >
# PLease read the GNU Affero General Public License in
# <https://www.github.com/TeamUltroid/Ultroid/blob/main/LICENSE/>.
"""
✘ Commands Available -

• `{i}mtoi <reply to media>`
    Media to image conversion

• `{i}mtos <reply to media>`
    Convert media to sticker.

• `{i}doc <filename.ext>`
    Reply to a text msg to save it in a file.

• `{i}open`
    Reply to a file to reveal it's text.

• `{i}rename <file name with extension>`
    Rename the file

• `{i}thumbnail <reply to image/thumbnail file>`
    Upload Your file with your custom thumbnail.
"""
import os
import time

try:
    import cv2
except ImportError:
    cv2 = None

from PIL import Image
from telegraph import upload_file as uf

from . import bash, downloader, eor, get_paste, get_string, udB, ultroid_cmd, uploader

opn = []


@ultroid_cmd(
    pattern="thumbnail$",
)
async def _(e):
    r = await e.get_reply_message()
    if r.photo:
        dl = await r.download_media()
    elif r.document and r.document.thumbs:
        dl = await r.download_media(thumb=-1)
    else:
        return await eor(e, "`Reply to Photo or media with thumb...`")
    variable = uf(dl)
    os.remove(dl)
    nn = "https://telegra.ph" + variable[0]
    udB.set("CUSTOM_THUMBNAIL", str(nn))
    await bash(f"wget {nn} -O resources/extras/ultroid.jpg")
    await eor(e, get_string("cvt_6").format(nn), link_preview=False)


@ultroid_cmd(
    pattern="rename ?(.*)",
)
async def imak(event):
    reply = await event.get_reply_message()
    t = time.time()
    if not reply:
        return await eor(event, get_string("cvt_1"))
    inp = event.pattern_match.group(1)
    if not inp:
        return await eor(event, get_string("cvt_2"))
    xx = await eor(event, get_string("com_1"))
    if reply.media:
        if hasattr(reply.media, "document"):
            file = reply.media.document
            image = await downloader(
                reply.file.name or str(time.time()),
                reply.media.document,
                xx,
                t,
                get_string("com_5"),
            )

            file = image.name
        else:
            file = await event.client.download_media(reply.media)
    os.rename(file, inp)
    k = time.time()
    xxx = await uploader(inp, inp, k, xx, get_string("com_6"))
    await event.reply(
        f"`{xxx.name}`",
        file=xxx,
        force_document=True,
        thumb="resources/extras/ultroid.jpg",
    )
    os.remove(inp)
    await xx.delete()


@ultroid_cmd(
    pattern="mtoi$",
)
async def imak(event):
    reply = await event.get_reply_message()
    if not (reply and (reply.media)):
        await eor(event, get_string("cvt_3"))
        return
    xx = await eor(event, get_string("com_1"))
    image = await reply.download_media()
    file = "ult.png"
    if image.endswith((".webp", ".png")):
        c = Image.open(image)
        c.save(file)
    elif image.endswith(".tgs"):
        await bash(f"lottie_convert.py '{image}' {file}")
    else:
        img = cv2.VideoCapture(image)
        ult, roid = img.read()
        cv2.imwrite(file, roid)
    await event.reply(file=file)
    await xx.delete()
    os.remove(file)
    os.remove(image)


@ultroid_cmd(
    pattern="mtos$",
)
async def smak(event):
    reply = await event.get_reply_message()
    if not (reply and (reply.media)):
        await eor(event, get_string("cvt_3"))
        return
    xx = await eor(event, get_string("com_1"))
    image = await reply.download_media()
    file = "ult.webp"
    if image.endswith((".webp", ".png", ".jpg")):
        c = Image.open(image)
        c.save(file)
    else:
        img = cv2.VideoCapture(image)
        ult, roid = img.read()
        cv2.imwrite(file, roid)
    await event.reply(file=file)
    await xx.delete()
    os.remove(file)
    os.remove(image)


@ultroid_cmd(
    pattern="doc ?(.*)",
)
async def _(event):
    input_str = event.pattern_match.group(1)
    if not (input_str and event.is_reply):
        return await eor(event, get_string("cvt_1"), time=5)
    xx = await eor(event, get_string("com_1"))
    a = await event.get_reply_message()
    if not a.message:
        return await xx.edit(get_string("ex_1"))
    with open(input_str, "w") as b:
        b.write(str(a.message))
    await xx.edit(f"**Packing into** `{input_str}`")
    await event.reply(file=input_str, thumb="resources/extras/ultroid.jpg")
    await xx.delete()
    os.remove(input_str)


@ultroid_cmd(
    pattern="open$",
)
async def _(event):
    a = await event.get_reply_message()
    if not (a and a.media):
        return await eor(event, get_string("cvt_7"), time=5)
    xx = await eor(event, get_string("com_1"))
    b = await a.download_media()
    try:
        with open(b) as c:
            d = c.read()
    except UnicodeDecodeError:
        return await eor(xx, get_string("cvt_8"), time=5)
    try:
        await xx.edit(f"```{d}```")
    except BaseException:
        what, key = await get_paste(d)
        await xx.edit(
            f"**MESSAGE EXCEEDS TELEGRAM LIMITS**\n\nSo Pasted It On [SPACEBIN](https://spaceb.in/{key})"
        )
    os.remove(b)
