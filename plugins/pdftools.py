# Ultroid - UserBot
# Copyright (C) 2021-2022 TeamUltroid
#
# This file is a part of < https://github.com/TeamUltroid/Ultroid/ >
# PLease read the GNU Affero General Public License in
# <https://www.github.com/TeamUltroid/Ultroid/blob/main/LICENSE/>.
"""
✘ Commands Available -

• `{i}pdf <page num> <reply to pdf file>`
    Extract & send page as an Image.(note-: For extracting all pages, just use .pdf)
    to upload selected range `{i}pdf 1-7`

• `{i}pdtext <page num> <reply to pdf file>`
    Extract Text From the Pdf.(note-: For Extraction all text just use .pdtext)
    to extract selected pages `{i}pdf 1-7`

• `{i}pdscan <reply to image>`
    It scan, crop & send image(s) as pdf.

• `{i}pdsave <reply to image/pdf>`
    It scan, crop & save file to merge.
    you can merge many pages in a single pdf.

• `{i}pdsend `
    Merge & send the pdf, collected from .pdsave.
"""
import glob
import os
import shutil
import time

import cv2
import numpy as np

try:
    from PIL import Image
except ImportError:
    Image = None
    LOGS.info(f"{__file__}: PIL  not Installed.")
from PyPDF2 import PdfFileMerger, PdfFileReader, PdfFileWriter
from telethon.errors.rpcerrorlist import PhotoSaveFileInvalidError
from utilities.tools import four_point_transform

from .. import (HNDLR, LOGS, bash, check_filename, downloader, eor, get_string,
                ultroid_cmd)

if not os.path.isdir("pdf"):
    os.mkdir("pdf")


@ultroid_cmd(
    pattern="pdf( (.*)|$)",
)
async def pdfseimg(event):
    ok = await event.get_reply_message()
    msg = event.pattern_match.group(1).strip()
    if not (ok and (ok.document and (ok.document.mime_type == "application/pdf"))):
        await event.eor("`Reply The pdf u Want to Download..`")
        return
    xx = await event.eor(get_string("com_1"))
    file = ok.media.document
    k = time.time()
    filename = "hehe.pdf"
    result = await downloader(
        f"pdf/{filename}", file, xx, k, f"Downloading {filename}..."
    )

    await xx.delete()
    pdfp = "pdf/hehe.pdf"
    pdfp.replace(".pdf", "")
    pdf = PdfFileReader(pdfp)
    if not msg:
        ok = []
        for num in range(pdf.numPages):
            pw = PdfFileWriter()
            pw.addPage(pdf.getPage(num))
            fil = os.path.join(f"pdf/ult{num + 1}.png")
            ok.append(fil)
            with open(fil, "wb") as f:
                pw.write(f)
        os.remove(pdfp)
        for z in ok:
            await event.client.send_file(event.chat_id, z)
        shutil.rmtree("pdf")
        os.mkdir("pdf")
        await xx.delete()
    elif "-" in msg:
        ok = int(msg.split("-")[-1]) - 1
        for o in range(ok):
            pw = PdfFileWriter()
            pw.addPage(pdf.getPage(o))
            with open(os.path.join("ult.png"), "wb") as f:
                pw.write(f)
            await event.reply(
                file="ult.png",
            )
            os.remove("ult.png")
        os.remove(pdfp)
    else:
        o = int(msg) - 1
        pw = PdfFileWriter()
        pw.addPage(pdf.getPage(o))
        with open(os.path.join("ult.png"), "wb") as f:
            pw.write(f)
        os.remove(pdfp)
        try:
            await event.reply(file="ult.png")
        except PhotoSaveFileInvalidError:
            await event.reply(file="ult.png", force_document=True)
        os.remove("ult.png")


@ultroid_cmd(
    pattern="pdtext( (.*)|$)",
)
async def pdfsetxt(event):
    ok = await event.get_reply_message()
    msg = event.pattern_match.group(1).strip()
    if not ok and ok.document and ok.document.mime_type == "application/pdf":
        await event.eor("`Reply The pdf u Want to Download..`")
        return
    xx = await event.eor(get_string("com_1"))
    file = ok.media.document
    k = time.time()
    filename = ok.file.name
    result = await downloader(filename, file, xx, k, f"Downloading {filename}...")
    await xx.delete()
    dl = result.name
    if not msg:
        pdf = PdfFileReader(dl)
        text = f"{dl.split('.')[0]}.txt"
        with open(text, "w") as f:
            for page_num in range(pdf.numPages):
                pageObj = pdf.getPage(page_num)
                txt = pageObj.extractText()
                f.write(f"Page {page_num + 1}\n")
                f.write("".center(100, "-"))
                f.write(txt)
        await event.client.send_file(
            event.chat_id,
            text,
            reply_to=event.reply_to_msg_id,
        )
        os.remove(text)
        os.remove(dl)
        return
    if "-" in msg:
        u, d = msg.split("-")
        a = PdfFileReader(dl)
        str = "".join(a.getPage(i).extractText()
                      for i in range(int(u) - 1, int(d)))
        text = f"{dl.split('.')[0]} {msg}.txt"
    else:
        u = int(msg) - 1
        a = PdfFileReader(dl)
        str = a.getPage(u).extractText()
        text = f"{dl.split('.')[0]} Pg-{msg}.txt"

    with open(text, "w") as f:
        f.write(str)
    await event.client.send_file(
        event.chat_id,
        text,
        reply_to=event.reply_to_msg_id,
    )
    os.remove(text)
    os.remove(dl)


@ultroid_cmd(
    pattern="pdscan( (.*)|$)",
)
async def imgscan(event):
    ok = await event.get_reply_message()
    if not (ok and (ok.media)):
        await event.eor("`Reply The pdf u Want to Download..`")
        return
    if not (
        ok.photo
        or (ok.file.name and ok.file.name.endswith(("png", "jpg", "jpeg", "webp")))
    ):
        await event.eor("`Reply to a Image only...`")
        return
    ultt = await ok.download_media()
    xx = await event.eor(get_string("com_1"))
    image = cv2.imread(ultt)
    original_image = image.copy()
    ratio = image.shape[0] / 500.0
    hi, wid = image.shape[:2]
    ra = 500 / float(hi)
    dmes = (int(wid * ra), 500)
    image = cv2.resize(image, dmes, interpolation=cv2.INTER_AREA)
    image_yuv = cv2.cvtColor(image, cv2.COLOR_BGR2YUV)
    image_y = np.zeros(image_yuv.shape[:2], np.uint8)
    image_y[:, :] = image_yuv[:, :, 0]
    image_blurred = cv2.GaussianBlur(image_y, (3, 3), 0)
    edges = cv2.Canny(image_blurred, 50, 200, apertureSize=3)
    contours, hierarchy = cv2.findContours(
        edges,
        cv2.RETR_EXTERNAL,
        cv2.CHAIN_APPROX_SIMPLE,
    )
    polygons = []
    for cnt in contours:
        hull = cv2.convexHull(cnt)
        polygons.append(
            cv2.approxPolyDP(
                hull,
                0.01 *
                cv2.arcLength(
                    hull,
                    True),
                False))
        sortedPoly = sorted(polygons, key=cv2.contourArea, reverse=True)
        cv2.drawContours(image, sortedPoly[0], -1, (0, 0, 255), 5)
        simplified_cnt = sortedPoly[0]
    if len(simplified_cnt) == 4:
        try:
            from skimage.filters import threshold_local
        except ImportError:
            LOGS.info(f"Scikit-Image is not Installed.")
            await xx.edit("`Installing Scikit-Image...\nThis may take some long...`")
            _, __ = await bash("pip install scikit-image")
            LOGS.info(_)
            from skimage.filters import threshold_local
        cropped_image = four_point_transform(
            original_image,
            simplified_cnt.reshape(4, 2) * ratio,
        )
        gray_image = cv2.cvtColor(cropped_image, cv2.COLOR_BGR2GRAY)
        T = threshold_local(gray_image, 11, offset=10, method="gaussian")
        ok = (gray_image > T).astype("uint8") * 255
    if len(simplified_cnt) != 4:
        ok = cv2.detailEnhance(original_image, sigma_s=10, sigma_r=0.15)
    cv2.imwrite("o.png", ok)
    image1 = Image.open("o.png")
    im1 = image1.convert("RGB")
    scann = f"Scanned {ultt.split('.')[0]}.pdf"
    im1.save(scann)
    await event.client.send_file(event.chat_id, scann, reply_to=event.reply_to_msg_id)
    await xx.delete()
    os.remove(ultt)
    os.remove("o.png")
    os.remove(scann)


@ultroid_cmd(
    pattern="pdsave( (.*)|$)",
)
async def savepdf(event):
    ok = await event.get_reply_message()
    if not (ok and (ok.media)):
        await eor(
            event,
            "`Reply to Images/pdf which u want to merge as a single pdf..`",
        )
        return
    ultt = await ok.download_media()
    if ultt.endswith(("png", "jpg", "jpeg", "webp")):
        xx = await event.eor(get_string("com_1"))
        image = cv2.imread(ultt)
        original_image = image.copy()
        ratio = image.shape[0] / 500.0
        h_, _v = image.shape[:2]
        m_ = 500 / float(h_)
        image = cv2.resize(image, (int(_v * m_), 500),
                           interpolation=cv2.INTER_AREA)
        image_yuv = cv2.cvtColor(image, cv2.COLOR_BGR2YUV)
        image_y = np.zeros(image_yuv.shape[:2], np.uint8)
        image_y[:, :] = image_yuv[:, :, 0]
        image_blurred = cv2.GaussianBlur(image_y, (3, 3), 0)
        edges = cv2.Canny(image_blurred, 50, 200, apertureSize=3)
        contours, hierarchy = cv2.findContours(
            edges,
            cv2.RETR_EXTERNAL,
            cv2.CHAIN_APPROX_SIMPLE,
        )
        polygons = []
        for cnt in contours:
            hull = cv2.convexHull(cnt)
            polygons.append(
                cv2.approxPolyDP(
                    hull,
                    0.01 *
                    cv2.arcLength(
                        hull,
                        True),
                    False),
            )
            sortedPoly = sorted(polygons, key=cv2.contourArea, reverse=True)
            cv2.drawContours(image, sortedPoly[0], -1, (0, 0, 255), 5)
            simplified_cnt = sortedPoly[0]
        if len(simplified_cnt) == 4:
            try:
                from skimage.filters import threshold_local
            except ImportError:
                LOGS.info(f"Scikit-Image is not Installed.")
                await xx.edit(
                    "`Installing Scikit-Image...\nThis may take some long...`"
                )
                _, __ = await bash("pip install scikit-image")
                LOGS.info(_)
                from skimage.filters import threshold_local
            cropped_image = four_point_transform(
                original_image,
                simplified_cnt.reshape(4, 2) * ratio,
            )
            gray_image = cv2.cvtColor(cropped_image, cv2.COLOR_BGR2GRAY)
            T = threshold_local(gray_image, 11, offset=10, method="gaussian")
            ok = (gray_image > T).astype("uint8") * 255
        if len(simplified_cnt) != 4:
            ok = cv2.detailEnhance(original_image, sigma_s=10, sigma_r=0.15)
        cv2.imwrite("o.png", ok)
        image1 = Image.open("o.png")
        im1 = image1.convert("RGB")
        a = check_filename("pdf/scan.pdf")
        im1.save(a)
        await xx.edit(
            f"Done, Now Reply Another Image/pdf if completed then use {HNDLR}pdsend to merge nd send all as pdf",
        )
        os.remove("o.png")
    elif ultt.endswith(".pdf"):
        a = check_filename("pdf/scan.pdf")
        await event.client.download_media(ok, a)
        await eor(
            event,
            f"Done, Now Reply Another Image/pdf if completed then use {HNDLR}pdsend to merge nd send all as pdf",
        )
    else:
        await event.eor("`Reply to a Image/pdf only...`")
    os.remove(ultt)


@ultroid_cmd(
    pattern="pdsend( (.*)|$)",
)
async def sendpdf(event):
    if not os.path.exists("pdf/scan.pdf"):
        await eor(
            event,
            "first select pages by replying .pdsave of which u want to make multi page pdf file",
        )
        return
    msg = event.pattern_match.group(1).strip()
    ok = f"{msg}.pdf" if msg else "My PDF File.pdf"
    merger = PdfFileMerger()
    afl = glob.glob("pdf/*")
    ok_ = [*sorted(afl)]
    for item in ok_:
        if item.endswith("pdf"):
            merger.append(item)
    merger.write(ok)
    await event.client.send_file(event.chat_id, ok_, reply_to=event.reply_to_msg_id)
    os.remove(ok_)
    shutil.rmtree("pdf/")
    os.makedirs("pdf/")
