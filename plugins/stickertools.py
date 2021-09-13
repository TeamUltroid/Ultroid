# Ultroid - UserBot
# Copyright (C) 2021 TeamUltroid
#
# This file is a part of < https://github.com/TeamUltroid/Ultroid/ >
# PLease read the GNU Affero General Public License in
# <https://www.github.com/TeamUltroid/Ultroid/blob/main/LICENSE/>.
"""
✘ Commands Available -

• `{i}destroy <reply to animated sticker>`
    To destroy the sticker.

• `{i}tiny <reply to media>`
    To create Tiny stickers.

• `{i}convert <gif/img/sticker>`
    Reply to sticker to convert into gif or image.

• `{i}kang <reply to image/sticker>`
    Kang the sticker (add to your pack).

• `{i}packkang <pack name>`
    Kang the Complete sticker set (with custom name).

• `{i}round <reply to any media>`
    To extract round sticker.

• `{i}waifu <text>`
    p text on random stickers.

"""
import asyncio
import io
import os
import random
import re
from os import remove

import cv2
import numpy as np
import requests
from carbonnow import Carbon
from PIL import Image, ImageDraw
from telethon.errors import (
    ChatSendStickersForbiddenError,
    PackShortNameOccupiedError,
    YouBlockedUserError,
)
from telethon.tl.types import (
    DocumentAttributeFilename,
    DocumentAttributeSticker,
    MessageMediaPhoto,
)
from telethon.utils import get_input_document

from . import *

EMOJI_PATTERN = re.compile(
    "["
    "\U0001F1E0-\U0001F1FF"  # flags (iOS)
    "\U0001F300-\U0001F5FF"  # symbols & pictographs
    "\U0001F600-\U0001F64F"  # emoticons
    "\U0001F680-\U0001F6FF"  # transport & map symbols
    "\U0001F700-\U0001F77F"  # alchemical symbols
    "\U0001F780-\U0001F7FF"  # Geometric Shapes Extended
    "\U0001F800-\U0001F8FF"  # Supplemental Arrows-C
    "\U0001F900-\U0001F9FF"  # Supplemental Symbols and Pictographs
    "\U0001FA00-\U0001FA6F"  # Chess Symbols
    "\U0001FA70-\U0001FAFF"  # Symbols and Pictographs Extended-A
    "\U00002702-\U000027B0"  # Dingbats
    "]+",
)


def deEmojify(inputString: str) -> str:
    """Remove emojis and other non-safe characters from string"""
    return re.sub(EMOJI_PATTERN, "", inputString)


@ultroid_cmd(
    pattern="waifu ?(.*)",
)
async def waifu(animu):
    xx = await eor(animu, "`Processing...`")
    # """Creates random anime sticker!"""
    text = animu.pattern_match.group(1)
    if not text:
        if animu.is_reply:
            text = (await animu.get_reply_message()).message
        else:
            await xx.edit("`You haven't written any article, Waifu is going away.`")
            return
    waifus = [32, 33, 37, 40, 41, 42, 58, 20]
    finalcall = "#" + (str(random.choice(waifus)))
    try:
        sticcers = await animu.client.inline_query(
            "stickerizerbot",
            f"{finalcall}{(deEmojify(text))}",
        )
        await sticcers[0].click(
            animu.chat_id,
            reply_to=animu.reply_to_msg_id,
            silent=bool(animu.is_reply),
            hide_via=True,
        )

        await xx.delete()
    except ChatSendStickersForbiddenError:
        await xx.edit("Sorry boss, I can't send Sticker Here !!")


@ultroid_cmd(
    pattern="convert ?(.*)",
)
async def uconverter(event):
    xx = await eor(event, "`Processing...`")
    a = await event.get_reply_message()
    ok = ["image/webp", "application/x-tgsticker"]
    if not (a.media and a.media.document and a.media.document.mime_type in ok):
        return await eor(event, "`Reply to a Sticker...`")
    input_ = event.pattern_match.group(1)
    b = await event.client.download_media(a, "resources/downloads/")
    if "gif" in input_:
        cmd = ["lottie_convert.py", b, "something.gif"]
        file = "something.gif"
    elif "img" in input_:
        cmd = ["lottie_convert.py", b, "something.png"]
        file = "something.png"
    elif "sticker" in input_:
        cmd = ["lottie_convert.py", b, "something.webp"]
        file = "something.webp"
    else:
        return await xx.edit("**Please select from gif/img/sticker**")
    process = await asyncio.create_subprocess_exec(
        *cmd,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )
    stdout, stderr = await process.communicate()
    stderr.decode().strip()
    stdout.decode().strip()
    os.remove(b)
    await event.client.send_file(event.chat_id, file, force_document=False)
    os.remove(file)
    await xx.delete()


@ultroid_cmd(pattern="packkang")
async def pack_kangish(_):
    _e = await _.get_reply_message()
    if not _e:
        return await eor(_, "`Reply to Sticker.`")
    if len(_.text) > 9:
        _packname = _.text.split(" ", maxsplit=1)[1]
    else:
        _packname = f"Ultroid Kang Pack By {_.sender_id}"
    if _e and _e.media and _e.media.document.mime_type == "image/webp":
        _id = _e.media.document.attributes[1].stickerset.id
        _hash = _e.media.document.attributes[1].stickerset.access_hash
        _get_stiks = await _.client(
            functions.messages.GetStickerSetRequest(
                stickerset=types.InputStickerSetID(id=_id, access_hash=_hash)
            )
        )
        stiks = []
        for i in _get_stiks.documents:
            x = get_input_document(i)
            stiks.append(
                types.InputStickerSetItem(
                    document=x,
                    emoji=(i.attributes[1]).alt,
                )
            )
        try:
            eval(udB.get("PACKKANG"))
        except BaseException:
            udB.set("PACKKANG", "{}")
        ok = eval(udB.get("PACKKANG"))
        try:
            pack = ok[_.sender_id] + 1
        except BaseException:
            pack = 1
        try:
            _r_e_s = await asst(
                functions.stickers.CreateStickerSetRequest(
                    user_id=_.sender_id,
                    title=_packname,
                    short_name=f"u{_.sender_id}_{pack}_by_{(await tgbot.get_me()).username}",
                    stickers=stiks,
                )
            )
            ok.update({_.sender_id: pack})
            udB.set("PACKKANG", str(ok))
        except PackShortNameOccupiedError:
            time.sleep(1)
            pack += 1
            _r_e_s = await asst(
                functions.stickers.CreateStickerSetRequest(
                    user_id=_.sender_id,
                    title=_packname,
                    short_name=f"u{_.sender_id}_{pack}_by_{(await tgbot.get_me()).username}",
                    stickers=stiks,
                )
            )
            ok.update({_.sender_id: pack})
            udB.set("PACKKANG", str(ok))
        await eor(
            _,
            f"Pack Kanged Successfully.\nKanged Pack: [link](https://t.me/addstickers/{_r_e_s.set.short_name})",
        )
    else:
        await eor(_, "Unsupported File")


@ultroid_cmd(
    pattern="kang",
)
async def hehe(args):
    ultroid_bot = args.client
    xx = await eor(args, "`Processing...`")
    user = ultroid_bot.me
    if not user.username:
        user.username = user.first_name
    message = await args.get_reply_message()
    photo = None
    is_anim = False
    emoji = None
    if message and (message.media or message.text):
        if isinstance(message.media, MessageMediaPhoto) or message.text:
            await xx.edit(f"`{random.choice(KANGING_STR)}`")
            photo = io.BytesIO()
            photo = await ultroid_bot.download_media(message.photo, photo)
            if not photo and message.text:
                carbon = Carbon(
                    base_url="https://carbonara.vercel.app/api/cook", code=message.text
                )
                photo = await carbon.memorize("carbon_kang")
        elif "image" in message.media.document.mime_type.split("/"):
            await xx.edit(f"`{random.choice(KANGING_STR)}`")
            photo = io.BytesIO()
            await ultroid_bot.download_file(message.media.document, photo)
            if (
                DocumentAttributeFilename(file_name="sticker.webp")
                in message.media.document.attributes
            ):
                emoji = message.media.document.attributes[1].alt
        elif "video" in message.media.document.mime_type.split("/"):
            await xx.edit(f"`{random.choice(KANGING_STR)}`")
            xy = await message.download_media()
            y = cv2.VideoCapture(xy)
            heh, lol = y.read()
            cv2.imwrite("ult.webp", lol)
            photo = "ult.webp"
        elif "tgsticker" in message.media.document.mime_type:
            await xx.edit(f"`{random.choice(KANGING_STR)}`")
            await ultroid_bot.download_file(
                message.media.document,
                "AnimatedSticker.tgs",
            )

            attributes = message.media.document.attributes
            for attribute in attributes:
                if isinstance(attribute, DocumentAttributeSticker):
                    emoji = attribute.alt

            is_anim = True
            photo = 1
        else:
            await xx.edit("`Unsupported File!`")
            return
    else:
        await xx.edit("`I can't kang that...`")
        return

    if photo:
        splat = args.text.split()
        pack = 1
        if not emoji:
            emoji = "🏵"
        if len(splat) == 3:
            pack = splat[2]  # User sent ultroid_both
            emoji = splat[1]
        elif len(splat) == 2:
            if splat[1].isnumeric():
                pack = int(splat[1])
            else:
                emoji = splat[1]

        packname = f"ult_{user.id}_{pack}"
        packnick = f"@{user.username}'s Pack {pack}"
        cmd = "/newpack"
        file = io.BytesIO()

        if not is_anim:
            image = await resize_photo(photo)
            file.name = "sticker.png"
            image.save(file, "PNG")
        else:
            packname += "_anim"
            packnick += " (Animated)"
            cmd = "/newanimated"

        response = requests.get(f"http://t.me/addstickers/{packname}")
        htmlstr = response.text.split("\n")

        if (
            "  A <strong>Telegram</strong> user has created the <strong>Sticker&nbsp;Set</strong>."
            not in htmlstr
        ):
            async with ultroid_bot.conversation("@Stickers") as conv:
                try:
                    await conv.send_message("/addsticker")
                except YouBlockedUserError:
                    LOGS.info("Unblocking @Stickers for kang...")
                    await ultroid_bot(functions.contacts.UnblockRequest("stickers"))
                    await conv.send_message("/addsticker")
                await conv.get_response()
                await ultroid_bot.send_read_acknowledge(conv.chat_id)
                await conv.send_message(packname)
                x = await conv.get_response()
                while "120" in x.text:
                    pack += 1
                    packname = f"ult_{user.id}_{pack}"
                    packnick = f"@{user.username}'s Pack {pack}"
                    await xx.edit(
                        "`Switching to Pack "
                        + str(pack)
                        + " due to insufficient space`",
                    )
                    await conv.send_message(packname)
                    x = await conv.get_response()
                    if x.text == "Invalid pack selected.":
                        await conv.send_message(cmd)
                        await conv.get_response()
                        await ultroid_bot.send_read_acknowledge(conv.chat_id)
                        await conv.send_message(packnick)
                        await conv.get_response()
                        await ultroid_bot.send_read_acknowledge(conv.chat_id)
                        if is_anim:
                            await conv.send_file("AnimatedSticker.tgs")
                            remove("AnimatedSticker.tgs")
                        else:
                            file.seek(0)
                            await conv.send_file(file, force_document=True)
                        await conv.get_response()
                        await conv.send_message(emoji)
                        await ultroid_bot.send_read_acknowledge(conv.chat_id)
                        await conv.get_response()
                        await conv.send_message("/publish")
                        if is_anim:
                            await conv.get_response()
                            await conv.send_message(f"<{packnick}>")
                        await conv.get_response()
                        await ultroid_bot.send_read_acknowledge(conv.chat_id)
                        await conv.send_message("/skip")
                        await ultroid_bot.send_read_acknowledge(conv.chat_id)
                        await conv.get_response()
                        await conv.send_message(packname)
                        await ultroid_bot.send_read_acknowledge(conv.chat_id)
                        await conv.get_response()
                        await ultroid_bot.send_read_acknowledge(conv.chat_id)
                        await xx.edit(
                            f"`Sticker added in a Different Pack !\
                            \nThis Pack is Newly created!\
                            \nYour pack can be found` [here](t.me/addstickers/{packname})",
                            parse_mode="md",
                        )
                        return
                if is_anim:
                    await conv.send_file("AnimatedSticker.tgs")
                    remove("AnimatedSticker.tgs")
                else:
                    file.seek(0)
                    await conv.send_file(file, force_document=True)
                rsp = await conv.get_response()
                if "Sorry, the file type is invalid." in rsp.text:
                    await xx.edit(
                        "`Failed to add sticker, use` @Stickers `bot to add the sticker manually.`",
                    )
                    return
                await conv.send_message(emoji)
                await ultroid_bot.send_read_acknowledge(conv.chat_id)
                await conv.get_response()
                await conv.send_message("/done")
                await conv.get_response()
                await ultroid_bot.send_read_acknowledge(conv.chat_id)
        else:
            await xx.edit("`Brewing a new Pack...`")
            async with ultroid_bot.conversation("Stickers") as conv:
                await conv.send_message(cmd)
                await conv.get_response()
                await ultroid_bot.send_read_acknowledge(conv.chat_id)
                await conv.send_message(packnick)
                await conv.get_response()
                await ultroid_bot.send_read_acknowledge(conv.chat_id)
                if is_anim:
                    await conv.send_file("AnimatedSticker.tgs")
                    remove("AnimatedSticker.tgs")
                else:
                    file.seek(0)
                    await conv.send_file(file, force_document=True)
                rsp = await conv.get_response()
                if "Sorry, the file type is invalid." in rsp.text:
                    await xx.edit(
                        "`Failed to add sticker, use` @Stickers `bot to add the sticker manually.`",
                    )
                    return
                await conv.send_message(emoji)
                await ultroid_bot.send_read_acknowledge(conv.chat_id)
                await conv.get_response()
                await conv.send_message("/publish")
                if is_anim:
                    await conv.get_response()
                    await conv.send_message(f"<{packnick}>")

                await conv.get_response()
                await ultroid_bot.send_read_acknowledge(conv.chat_id)
                await conv.send_message("/skip")
                await ultroid_bot.send_read_acknowledge(conv.chat_id)
                await conv.get_response()
                await conv.send_message(packname)
                await ultroid_bot.send_read_acknowledge(conv.chat_id)
                await conv.get_response()
                await ultroid_bot.send_read_acknowledge(conv.chat_id)
        await xx.edit(
            f"`Kanged!`\
            \n`Emoji` - {emoji}\
            \n`Sticker Pack` [here](t.me/addstickers/{packname})",
            parse_mode="md",
        )
        try:
            os.remove(photo)
        except BaseException:
            pass


@ultroid_cmd(
    pattern="round$",
)
async def ultdround(event):
    ureply = await event.get_reply_message()
    xx = await eor(event, "`Processing...`")
    if not (ureply and (ureply.media)):
        await xx.edit("`Reply to any media`")
        return
    ultt = await ureply.download_media()
    if ultt.endswith(".tgs"):
        await xx.edit("`Ooo Animated Sticker 👀...`")
        cmd = ["lottie_convert.py", ultt, "ult.png"]
        file = "ult.png"
        process = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        stdout, stderr = await process.communicate()
        stderr.decode().strip()
        stdout.decode().strip()
    elif ultt.endswith((".gif", ".mp4", ".mkv")):
        await xx.edit("`Processing...`")
        img = cv2.VideoCapture(ultt)
        heh, lol = img.read()
        cv2.imwrite("ult.png", lol)
        file = "ult.png"
    else:
        file = ultt
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
    if not event.is_reply:
        return await eor(event, "`Reply to Animated Sticker Only...`")
    if not (
        ult.media and ult.media.document and "tgsticker" in ult.media.document.mime_type
    ):
        return await eor(event, "`Reply to Animated Sticker only`")
    await event.client.download_media(ult, "ultroid.tgs")
    xx = await eor(event, "`Processing...`")
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
    await bash("lottie_convert.py json.json ultroid.tgs")
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
        await eor(event, "`Reply To Media`")
        return
    xx = await eor(event, "`Processing...`")
    ik = await event.client.download_media(reply)
    im1 = Image.open("resources/extras/ultroid_blank.png")
    if ik.endswith(".tgs"):
        await event.client.download_media(reply, "ult.tgs")
        await bash("lottie_convert.py ult.tgs json.json")
        with open("json.json") as json:
            jsn = json.read()
        jsn = jsn.replace("512", "2000")
        open("json.json", "w").write(jsn)
        await bash("lottie_convert.py json.json ult.tgs")
        file = "ult.tgs"
        os.remove("json.json")
    elif ik.endswith((".gif", ".mp4")):
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
    await event.client.send_file(event.chat_id, file, reply_to=event.reply_to_msg_id)
    await xx.delete()
    os.remove(file)
    os.remove(ik)
