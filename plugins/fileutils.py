# Ultroid - UserBot
# Copyright (C) 2021-2022 TeamUltroid
#
# This file is a part of < https://github.com/TeamUltroid/Ultroid/ >
# PLease read the GNU Affero General Public License in
# <https://www.github.com/TeamUltroid/Ultroid/blob/main/LICENSE/>.

from localization import get_help

__doc__ = get_help("converter")

import os
import time

from core.remote import rm

from . import bash, get_string, udB, ultroid_cmd

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
        return await e.eor("`Reply to Photo or media with thumb...`")
    with rm.get("telegraph", helper=True, dispose=True) as mod:
        cl = mod.get_client()
        variable = cl.upload_file(dl)
    os.remove(dl)
    nn = f"https://graph.org{variable[0]}"
    udB.set_key("CUSTOM_THUMBNAIL", str(nn))
    await bash(f"wget {nn} -O resources/extras/ultroid.jpg")
    await e.eor(get_string("cvt_6").format(nn), link_preview=False)


@ultroid_cmd(
    pattern="rename( (.*)|$)",
)
async def imak(event):
    reply = await event.get_reply_message()
    t = time.time()
    if not reply:
        return await event.eor(get_string("cvt_1"))
    inp = event.pattern_match.group(1).strip()
    if not inp:
        return await event.eor(get_string("cvt_2"))
    xx = await event.eor(get_string("com_1"))
    if reply.media:
        if hasattr(reply.media, "document"):
            file = reply.media.document
            image = await event.client.fast_downloader(
                reply.file.name or str(time.time()),
                reply.media.document,
                xx,
                t,
                get_string("com_5"),
            )

            file = image.name
        else:
            file = await event.client.download_media(reply.media)
    if os.path.exists(inp):
        os.remove(inp)
    # TODO: UNBOUND
    await bash(f'mv """{file}""" """{inp}"""')
    if not os.path.exists(inp) or os.path.exists(
            inp) and not os.path.getsize(inp):
        os.rename(file, inp)
    k = time.time()
    xxx = await event.client.fast_uploader(inp, inp, k, xx, get_string("com_6"))
    await event.reply(
        f"`{xxx.name}`",
        file=xxx,
        force_document=True
    )
    os.remove(inp)
    await xx.delete()


conv_keys = {
    "img": "png",
    "sticker": "webp",
    "webp": "webp",
    "image": "png",
    "webm": "webm",
    "gif": "gif",
    "json": "json",
    "tgs": "tgs",
}


@ultroid_cmd(
    pattern="convert( (.*)|$)",
)
async def uconverter(event):
    xx = await event.eor(get_string("com_1"))
    a = await event.get_reply_message()
    if a is None:
        return await event.eor("`Reply to Photo or media with thumb...`")
    input_ = event.pattern_match.group(1).strip()
    b = await a.download_media("resources/downloads/")
    if not b and (a.document and a.document.thumbs):
        b = await a.download_media(thumb=-1)
    if not b:
        return await xx.edit(get_string("cvt_3"))
    try:
        convert = conv_keys[input_]
    except KeyError:
        return await xx.edit(get_string("sts_3").format("gif/img/sticker/webm"))
    # TODO: FIX
    file = await con.convert(b, outname="ultroid", convert_to=convert)
    if file:
        await event.client.send_file(
            event.chat_id, file, reply_to=event.reply_to_msg_id or event.id
        )
        os.remove(file)
    await xx.delete()


@ultroid_cmd(
    pattern="doc( (.*)|$)",
)
async def _(event):
    input_str = event.pattern_match.group(1).strip()
    if not (input_str and event.is_reply):
        return await event.eor(get_string("cvt_1"), time=5)
    xx = await event.eor(get_string("com_1"))
    a = await event.get_reply_message()
    if not a.message:
        return await xx.edit(get_string("ex_1"))
    with open(input_str, "w") as b:
        b.write(str(a.message))
    await xx.edit(f"**Packing into** `{input_str}`")
    await event.reply(file=input_str)
    await xx.delete()
    os.remove(input_str)


@ultroid_cmd(
    pattern="open( (.*)|$)",
)
async def _(event):
    a = await event.get_reply_message()
    b = event.pattern_match.group(1).strip()
    if not ((a and a.media) or (b and os.path.exists(b))):
        return await event.eor(get_string("cvt_7"), time=5)
    xx = await event.eor(get_string("com_1"))
    rem = None
    if not b:
        b = await a.download_media()
        rem = True
    try:
        with open(b) as c:
            d = c.read()
    except UnicodeDecodeError:
        return await xx.eor(get_string("cvt_8"), time=5)
    try:
        await xx.edit(f"```{d}```")
    except BaseException:
        what, key = await get_paste(d)
        await xx.edit(
            f"**MESSAGE EXCEEDS TELEGRAM LIMITS**\n\nSo Pasted It On [SPACEBIN](https://spaceb.in/{key})"
        )
    if rem:
        os.remove(b)
