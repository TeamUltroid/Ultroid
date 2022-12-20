# Ultroid - UserBot
# Copyright (C) 2021-2022 TeamUltroid
#
# This file is a part of < https://github.com/TeamUltroid/Ultroid/ >
# PLease read the GNU Affero General Public License in
# <https://www.github.com/TeamUltroid/Ultroid/blob/main/LICENSE/>.
"""
✘ Commands Available -

• `{i}border <reply to photo/sticker>`
    To create border around that media..
    Ex - `{i}border 12,22,23`
       - `{i}border 12,22,23 ; width (in number)`

• `{i}grey <reply to any media>`
    To make it black nd white.

• `{i}color <reply to any Black nd White media>`
    To make it Colorfull.

• `{i}toon <reply to any media>`
    To make it toon.

• `{i}danger <reply to any media>`
    To make it look Danger.

• `{i}negative <reply to any media>`
    To make negative image.

• `{i}blur <reply to any media>`
    To make it blurry.

• `{i}quad <reply to any media>`
    create a Vortex.

• `{i}mirror <reply to any media>`
    To create mirror pic.

• `{i}flip <reply to any media>`
    To make it flip.

• `{i}sketch <reply to any media>`
    To draw its sketch.

• `{i}blue <reply to any media>`
    just cool.

• `{i}csample <color name /color code>`
   example : `{i}csample red`
             `{i}csample #ffffff`

• `{i}pixelator <reply image>`
    Create a Pixelated Image..
"""
import os

from . import LOGS, con

try:
    import cv2
except ImportError:
    LOGS.error(f"{__file__}: OpenCv not Installed.")

import numpy as np

try:
    from PIL import Image
except ImportError:
    Image = None
    LOGS.info(f"{__file__}: PIL  not Installed.")
from telegraph import upload_file as upf
from telethon.errors.rpcerrorlist import (
    ChatSendMediaForbiddenError,
    MessageDeleteForbiddenError,
)

from . import (
    Redis,
    async_searcher,
    download_file,
    get_string,
    requests,
    udB,
    ultroid_cmd,
)


@ultroid_cmd(pattern="color$")
async def _(event):
    reply = await event.get_reply_message()
    if not (reply and reply.media):
        return await event.eor("`Reply To a Black and White Image`")
    xx = await event.eor("`Coloring image 🎨🖌️...`")
    image = await reply.download_media()
    img = cv2.VideoCapture(image)
    ret, frame = img.read()
    cv2.imwrite("ult.jpg", frame)
    if udB.get_key("DEEP_API"):
        key = Redis("DEEP_API")
    else:
        key = "quickstart-QUdJIGlzIGNvbWluZy4uLi4K"
    r = requests.post(
        "https://api.deepai.org/api/colorizer",
        files={"image": open("ult.jpg", "rb")},
        headers={"api-key": key},
    )
    os.remove("ult.jpg")
    os.remove(image)
    if "status" in r.json():
        return await event.edit(
            r.json()["status"] + "\nGet api nd set `{i}setdb DEEP_API key`"
        )
    r_json = r.json()["output_url"]
    await event.client.send_file(event.chat_id, r_json, reply_to=reply)
    await xx.delete()


@ultroid_cmd(pattern="(grey|blur|negative|danger|mirror|quad|sketch|flip|toon)$")
async def ult_tools(event):
    match = event.pattern_match.group(1)
    ureply = await event.get_reply_message()
    if not (ureply and (ureply.media)):
        await event.eor(get_string("cvt_3"))
        return
    ultt = await ureply.download_media()
    xx = await event.eor(get_string("com_1"))
    if ultt.endswith(".tgs"):
        xx = await xx.edit(get_string("sts_9"))
    file = await con.convert(ultt, convert_to="png", outname="ult")
    ult = cv2.imread(file)
    if match == "grey":
        ultroid = cv2.cvtColor(ult, cv2.COLOR_BGR2GRAY)
    elif match == "blur":
        ultroid = cv2.GaussianBlur(ult, (35, 35), 0)
    elif match == "negative":
        ultroid = cv2.bitwise_not(ult)
    elif match == "danger":
        dan = cv2.cvtColor(ult, cv2.COLOR_BGR2RGB)
        ultroid = cv2.cvtColor(dan, cv2.COLOR_HSV2BGR)
    elif match == "mirror":
        ish = cv2.flip(ult, 1)
        ultroid = cv2.hconcat([ult, ish])
    elif match == "flip":
        trn = cv2.flip(ult, 1)
        ish = cv2.rotate(trn, cv2.ROTATE_180)
        ultroid = cv2.vconcat([ult, ish])
    elif match == "quad":
        ult = cv2.imread(file)
        roid = cv2.flip(ult, 1)
        mici = cv2.hconcat([ult, roid])
        fr = cv2.flip(mici, 1)
        trn = cv2.rotate(fr, cv2.ROTATE_180)
        ultroid = cv2.vconcat([mici, trn])
    elif match == "sketch":
        gray_image = cv2.cvtColor(ult, cv2.COLOR_BGR2GRAY)
        inverted_gray_image = 255 - gray_image
        blurred_img = cv2.GaussianBlur(inverted_gray_image, (21, 21), 0)
        inverted_blurred_img = 255 - blurred_img
        ultroid = cv2.divide(gray_image, inverted_blurred_img, scale=256.0)
    elif match == "toon":
        height, width, _ = ult.shape
        samples = np.zeros([height * width, 3], dtype=np.float32)
        count = 0
        for x in range(height):
            for y in range(width):
                samples[count] = ult[x][y]
                count += 1
        _, labels, centers = cv2.kmeans(
            samples,
            12,
            None,
            (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 10000, 0.0001),
            5,
            cv2.KMEANS_PP_CENTERS,
        )
        centers = np.uint8(centers)
        ish = centers[labels.flatten()]
        ultroid = ish.reshape(ult.shape)
    cv2.imwrite("ult.jpg", ultroid)
    await ureply.reply(
        file="ult.jpg",
        force_document=False,
    )
    await xx.delete()
    os.remove("ult.jpg")
    os.remove(file)


@ultroid_cmd(pattern="csample (.*)")
async def sampl(ult):
    if color := ult.pattern_match.group(1).strip():
        img = Image.new("RGB", (200, 100), f"{color}")
        img.save("csample.png")
        try:
            try:
                await ult.delete()
                await ult.respond(f"Colour Sample for `{color}` !", file="csample.png"
                )
            except MessageDeleteForbiddenError:
                await ult.reply(f"Colour Sample for `{color}` !", file="csample.png")
        except ChatSendMediaForbiddenError:
            await ult.eor("Umm! Sending Media is disabled here!")

    else:
        await ult.eor("Wrong Color Name/Hex Code specified!")


@ultroid_cmd(
    pattern="blue$",
)
async def ultd(event):
    ureply = await event.get_reply_message()
    xx = await event.eor("`...`")
    if not (ureply and (ureply.media)):
        await xx.edit(get_string("cvt_3"))
        return
    ultt = await ureply.download_media()
    if ultt.endswith(".tgs"):
        await xx.edit(get_string("sts_9"))
    file = await con.convert(ultt, convert_to="png", outname="ult")
    got = upf(file)
    lnk = f"https://graph.org{got[0]}"
    r = await async_searcher(
        f"https://nekobot.xyz/api/imagegen?type=blurpify&image={lnk}", re_json=True
    )
    ms = r.get("message")
    if not r["success"]:
        return await xx.edit(ms)
    await download_file(ms, "ult.png")
    img = Image.open("ult.png").convert("RGB")
    img.save("ult.webp", "webp")
    await event.client.send_file(
        event.chat_id,
        "ult.webp",
        force_document=False,
        reply_to=event.reply_to_msg_id,
    )
    await xx.delete()
    os.remove("ult.png")
    os.remove("ult.webp")
    os.remove(ultt)


@ultroid_cmd(pattern="border( (.*)|$)")
async def ok(event):
    hm = await event.get_reply_message()
    if not (hm and (hm.photo or hm.sticker)):
        return await event.eor("`Reply to Sticker or Photo..`")
    col = event.pattern_match.group(1).strip()
    wh = 20
    if not col:
        col = [255, 255, 255]
    else:
        try:
            if ";" in col:
                col_ = col.split(";", maxsplit=1)
                wh = int(col_[1])
                col = col_[0]
            col = [int(col) for col in col.split(",")[:2]]
        except ValueError:
            return await event.eor("`Not a Valid Input...`")
    okla = await hm.download_media()
    img1 = cv2.imread(okla)
    constant = cv2.copyMakeBorder(img1, wh, wh, wh, wh, cv2.BORDER_CONSTANT, value=col)
    cv2.imwrite("output.png", constant)
    await event.client.send_file(event.chat.id, "output.png")
    os.remove("output.png")
    os.remove(okla)
    await event.delete()


@ultroid_cmd(pattern="pixelator( (.*)|$)")
async def pixelator(event):
    reply_message = await event.get_reply_message()
    if not (reply_message and (reply_message.photo or reply_message.sticker)):
        return await event.eor("`Reply to a photo`")
    hw = 50
    try:
        hw = int(event.pattern_match.group(1).strip())
    except (ValueError, TypeError):
        pass
    msg = await event.eor(get_string("com_1"))
    image = await reply_message.download_media()
    input_ = cv2.imread(image)
    height, width = input_.shape[:2]
    w, h = (hw, hw)
    temp = cv2.resize(input_, (w, h), interpolation=cv2.INTER_LINEAR)
    output = cv2.resize(temp, (width, height), interpolation=cv2.INTER_NEAREST)
    cv2.imwrite("output.jpg", output)
    await msg.respond("• Pixelated by Ultroid", file="output.jpg")
    await msg.delete()
    os.remove("output.jpg")
    os.remove(image)
