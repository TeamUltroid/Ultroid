# Ultroid - UserBot
# Copyright (C) 2020 TeamUltroid
#
# This file is a part of < https://github.com/TeamUltroid/Ultroid/ >
# PLease read the GNU Affero General Public License in
# <https://www.github.com/TeamUltroid/Ultroid/blob/main/LICENSE/>.

"""
✘ Commands Available -

• `{i}toon <reply to any media>`
    To make it toon.

• `{i}danger <reply to any media>`
    To make it look Danger.

• `{i}grey <reply to any media>`
    To make it black nd white.

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
"""

import asyncio
import os

import cv2
import numpy as np
from PIL import Image
from telegraph import upload_file as upf
from validators.url import url

from . import *


@ultroid_cmd(
    pattern="sketch$",
)
async def sketch(e):
    ureply = await e.get_reply_message()
    xx = await eor(e, "`...`")
    if not (ureply and (ureply.media)):
        await xx.edit("`Reply to any media`")
        return
    ultt = await ureply.download_media()
    if ultt.endswith(".tgs"):
        await xx.edit("`Ooo Animated Sticker 👀...`")
        cmd = ["lottie_convert.py", ultt, "ult.png"]
        file = "ult.png"
        process = await asyncio.create_subprocess_exec(
            *cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
        )
        stdout, stderr = await process.communicate()
        stderr.decode().strip()
        stdout.decode().strip()
    else:
        await xx.edit("`Processing...`")
        img = cv2.VideoCapture(ultt)
        heh, lol = img.read()
        cv2.imwrite("ult.png", lol)
        file = "ult.png"
    img = cv2.imread(file)
    gray_image = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    inverted_gray_image = 255 - gray_image
    blurred_img = cv2.GaussianBlur(inverted_gray_image, (21, 21), 0)
    inverted_blurred_img = 255 - blurred_img
    pencil_sketch_IMG = cv2.divide(gray_image, inverted_blurred_img, scale=256.0)
    cv2.imwrite("ultroid.png", pencil_sketch_IMG)
    await e.client.send_file(e.chat_id, file="ultroid.png")
    await xx.delete()
    os.remove(file)
    os.remove("ultroid.png")


@ultroid_cmd(
    pattern="grey$",
)
async def ultd(event):
    ureply = await event.get_reply_message()
    if not (ureply and (ureply.media)):
        await eor(event, "`Reply to any media`")
        return
    ultt = await ureply.download_media()
    if ultt.endswith(".tgs"):
        xx = await eor(event, "`Ooo Animated Sticker 👀...`")
        cmd = ["lottie_convert.py", ultt, "ult.png"]
        file = "ult.png"
        process = await asyncio.create_subprocess_exec(
            *cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
        )
        stdout, stderr = await process.communicate()
        stderr.decode().strip()
        stdout.decode().strip()
    else:
        xx = await eor(event, "`Processing...`")
        img = cv2.VideoCapture(ultt)
        heh, lol = img.read()
        cv2.imwrite("ult.png", lol)
        file = "ult.png"
    ult = cv2.imread(file)
    ultroid = cv2.cvtColor(ult, cv2.COLOR_BGR2GRAY)
    cv2.imwrite("ult.jpg", ultroid)
    await event.client.send_file(
        event.chat_id, "ult.jpg", force_document=False, reply_to=event.reply_to_msg_id
    )
    await xx.delete()
    os.remove("ult.png")
    os.remove("ult.jpg")
    os.remove(ultt)


@ultroid_cmd(
    pattern="blur$",
)
async def ultd(event):
    ureply = await event.get_reply_message()
    if not (ureply and (ureply.media)):
        await eor(event, "`Reply to any media`")
        return
    ultt = await ureply.download_media()
    if ultt.endswith(".tgs"):
        xx = await eor(event, "`Ooo Animated Sticker 👀...`")
        cmd = ["lottie_convert.py", ultt, "ult.png"]
        file = "ult.png"
        process = await asyncio.create_subprocess_exec(
            *cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
        )
        stdout, stderr = await process.communicate()
        stderr.decode().strip()
        stdout.decode().strip()
    else:
        xx = await eor(event, "`Processing...`")
        img = cv2.VideoCapture(ultt)
        heh, lol = img.read()
        cv2.imwrite("ult.png", lol)
        file = "ult.png"
    ult = cv2.imread(file)
    ultroid = cv2.GaussianBlur(ult, (35, 35), 0)
    cv2.imwrite("ult.jpg", ultroid)
    await event.client.send_file(
        event.chat_id, "ult.jpg", force_document=False, reply_to=event.reply_to_msg_id
    )
    await xx.delete()
    os.remove("ult.png")
    os.remove("ult.jpg")
    os.remove(ultt)


@ultroid_cmd(
    pattern="negative$",
)
async def ultd(event):
    ureply = await event.get_reply_message()
    xx = await eor(event, "`...`")
    if not (ureply and (ureply.media)):
        await xx.edit("`Reply to any media`")
        return
    ultt = await ureply.download_media()
    if ultt.endswith(".tgs"):
        await xx.edit("`Ooo Animated Sticker 👀...`")
        cmd = ["lottie_convert.py", ultt, "ult.png"]
        file = "ult.png"
        process = await asyncio.create_subprocess_exec(
            *cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
        )
        stdout, stderr = await process.communicate()
        stderr.decode().strip()
        stdout.decode().strip()
    else:
        await xx.edit("`Processing...`")
        img = cv2.VideoCapture(ultt)
        heh, lol = img.read()
        cv2.imwrite("ult.png", lol)
        file = "ult.png"
    ult = cv2.imread(file)
    ultroid = cv2.bitwise_not(ult)
    cv2.imwrite("ult.jpg", ultroid)
    await event.client.send_file(
        event.chat_id, "ult.jpg", force_document=False, reply_to=event.reply_to_msg_id
    )
    await xx.delete()
    os.remove("ult.png")
    os.remove("ult.jpg")
    os.remove(ultt)


@ultroid_cmd(
    pattern="mirror$",
)
async def ultd(event):
    ureply = await event.get_reply_message()
    xx = await eor(event, "`...`")
    if not (ureply and (ureply.media)):
        await xx.edit("`Reply to any media`")
        return
    ultt = await ureply.download_media()
    if ultt.endswith(".tgs"):
        await xx.edit("`Ooo Animated Sticker 👀...`")
        cmd = ["lottie_convert.py", ultt, "ult.png"]
        file = "ult.png"
        process = await asyncio.create_subprocess_exec(
            *cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
        )
        stdout, stderr = await process.communicate()
        stderr.decode().strip()
        stdout.decode().strip()
    else:
        await xx.edit("`Processing...`")
        img = cv2.VideoCapture(ultt)
        heh, lol = img.read()
        cv2.imwrite("ult.png", lol)
        file = "ult.png"
    ult = cv2.imread(file)
    ish = cv2.flip(ult, 1)
    ultroid = cv2.hconcat([ult, ish])
    cv2.imwrite("ult.jpg", ultroid)
    await event.client.send_file(
        event.chat_id, "ult.jpg", force_document=False, reply_to=event.reply_to_msg_id
    )
    await xx.delete()
    os.remove("ult.png")
    os.remove("ult.jpg")
    os.remove(ultt)


@ultroid_cmd(
    pattern="flip$",
)
async def ultd(event):
    ureply = await event.get_reply_message()
    xx = await eor(event, "`...`")
    if not (ureply and (ureply.media)):
        await xx.edit("`Reply to any media`")
        return
    ultt = await ureply.download_media()
    if ultt.endswith(".tgs"):
        await xx.edit("`Ooo Animated Sticker 👀...`")
        cmd = ["lottie_convert.py", ultt, "ult.png"]
        file = "ult.png"
        process = await asyncio.create_subprocess_exec(
            *cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
        )
        stdout, stderr = await process.communicate()
        stderr.decode().strip()
        stdout.decode().strip()
    else:
        await xx.edit("`Processing...`")
        img = cv2.VideoCapture(ultt)
        heh, lol = img.read()
        cv2.imwrite("ult.png", lol)
        file = "ult.png"
    ult = cv2.imread(file)
    trn = cv2.flip(ult, 1)
    ish = cv2.rotate(trn, cv2.ROTATE_180)
    ultroid = cv2.vconcat([ult, ish])
    cv2.imwrite("ult.jpg", ultroid)
    await event.client.send_file(
        event.chat_id, "ult.jpg", force_document=False, reply_to=event.reply_to_msg_id
    )
    await xx.delete()
    os.remove("ult.png")
    os.remove("ult.jpg")
    os.remove(ultt)


@ultroid_cmd(
    pattern="quad$",
)
async def ultd(event):
    ureply = await event.get_reply_message()
    xx = await eor(event, "`...`")
    if not (ureply and (ureply.media)):
        await xx.edit("`Reply to any media`")
        return
    ultt = await ureply.download_media()
    if ultt.endswith(".tgs"):
        await xx.edit("`Ooo Animated Sticker 👀...`")
        cmd = ["lottie_convert.py", ultt, "ult.png"]
        file = "ult.png"
        process = await asyncio.create_subprocess_exec(
            *cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
        )
        stdout, stderr = await process.communicate()
        stderr.decode().strip()
        stdout.decode().strip()
    else:
        await xx.edit("`Processing...`")
        img = cv2.VideoCapture(ultt)
        heh, lol = img.read()
        cv2.imwrite("ult.png", lol)
        file = "ult.png"
    ult = cv2.imread(file)
    roid = cv2.flip(ult, 1)
    mici = cv2.hconcat([ult, roid])
    fr = cv2.flip(mici, 1)
    trn = cv2.rotate(fr, cv2.ROTATE_180)
    ultroid = cv2.vconcat([mici, trn])
    cv2.imwrite("ult.jpg", ultroid)
    await event.client.send_file(
        event.chat_id, "ult.jpg", force_document=False, reply_to=event.reply_to_msg_id
    )
    await xx.delete()
    os.remove("ult.png")
    os.remove("ult.jpg")
    os.remove(ultt)


@ultroid_cmd(
    pattern="toon$",
)
async def ultd(event):
    ureply = await event.get_reply_message()
    xx = await eor(event, "`...`")
    if not (ureply and (ureply.media)):
        await xx.edit("`Reply to any media`")
        return
    ultt = await ureply.download_media()
    if ultt.endswith(".tgs"):
        await xx.edit("`Ooo Animated Sticker 👀...`")
        cmd = ["lottie_convert.py", ultt, "ult.png"]
        file = "ult.png"
        process = await asyncio.create_subprocess_exec(
            *cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
        )
        stdout, stderr = await process.communicate()
        stderr.decode().strip()
        stdout.decode().strip()
    else:
        await xx.edit("`Processing...`")
        img = cv2.VideoCapture(ultt)
        heh, lol = img.read()
        cv2.imwrite("ult.png", lol)
        file = "ult.png"
    ult = cv2.imread(file)
    height, width, channels = ult.shape
    samples = np.zeros([height * width, 3], dtype=np.float32)
    count = 0
    for x in range(height):
        for y in range(width):
            samples[count] = ult[x][y]
            count += 1
    compactness, labels, centers = cv2.kmeans(
        samples,
        12,
        None,
        (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 10000, 0.0001),
        5,
        cv2.KMEANS_PP_CENTERS,
    )
    centers = np.uint8(centers)
    ish = centers[labels.flatten()]
    ultroid = ish.reshape((ult.shape))
    cv2.imwrite("ult.jpg", ultroid)
    await event.client.send_file(
        event.chat_id, "ult.jpg", force_document=False, reply_to=event.reply_to_msg_id
    )
    await xx.delete()
    os.remove("ult.png")
    os.remove("ult.jpg")
    os.remove(ultt)


@ultroid_cmd(
    pattern="danger$",
)
async def ultd(event):
    ureply = await event.get_reply_message()
    xx = await eor(event, "`...`")
    if not (ureply and (ureply.media)):
        await xx.edit("`Reply to any media`")
        return
    ultt = await ureply.download_media()
    if ultt.endswith(".tgs"):
        await xx.edit("`Ooo Animated Sticker 👀...`")
        cmd = ["lottie_convert.py", ultt, "ult.png"]
        file = "ult.png"
        process = await asyncio.create_subprocess_exec(
            *cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
        )
        stdout, stderr = await process.communicate()
        stderr.decode().strip()
        stdout.decode().strip()
    else:
        await xx.edit("`Processing...`")
        img = cv2.VideoCapture(ultt)
        heh, lol = img.read()
        cv2.imwrite("ult.png", lol)
        file = "ult.png"
    ult = cv2.imread(file)
    dan = cv2.cvtColor(ult, cv2.COLOR_BGR2RGB)
    ultroid = cv2.cvtColor(dan, cv2.COLOR_HSV2BGR)
    cv2.imwrite("ult.jpg", ultroid)
    await event.client.send_file(
        event.chat_id, "ult.jpg", force_document=False, reply_to=event.reply_to_msg_id
    )
    await xx.delete()
    os.remove("ult.png")
    os.remove("ult.jpg")
    os.remove(ultt)


@ultroid_cmd(
    pattern="blue$",
)
async def ultd(event):
    ureply = await event.get_reply_message()
    xx = await eor(event, "`...`")
    if not (ureply and (ureply.media)):
        await xx.edit("`Reply to any media`")
        return
    ultt = await ureply.download_media()
    if ultt.endswith(".tgs"):
        await xx.edit("`Ooo Animated Sticker 👀...`")
        cmd = ["lottie_convert.py", ultt, "ult.png"]
        file = "ult.png"
        process = await asyncio.create_subprocess_exec(
            *cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
        )
        stdout, stderr = await process.communicate()
        stderr.decode().strip()
        stdout.decode().strip()
    else:
        await xx.edit("`Processing...`")
        img = cv2.VideoCapture(ultt)
        heh, lol = img.read()
        cv2.imwrite("ult.png", lol)
        file = "ult.png"
    got = upf(file)
    lnk = f"https://telegra.ph{got[0]}"
    r = requests.get(
        f"https://nekobot.xyz/api/imagegen?type=blurpify&image={lnk}"
    ).json()
    ms = r.get("message")
    utd = url(ms)
    if not utd:
        return
    with open("ult.png", "wb") as f:
        f.write(requests.get(ms).content)
    img = Image.open("ult.png").convert("RGB")
    img.save("ult.webp", "webp")
    await event.client.send_file(
        event.chat_id, "ult.webp", force_document=False, reply_to=event.reply_to_msg_id
    )
    await xx.delete()
    os.remove("ult.png")
    os.remove("ult.webp")
    os.remove(ultt)


HELP.update({f"{__name__.split('.')[1]}": f"{__doc__.format(i=HNDLR)}"})
