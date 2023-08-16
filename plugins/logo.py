import glob
import os
import random

from core import rm
from PIL import Image, ImageDraw, ImageFont
from telethon.tl.types import InputMessagesFilterPhotos
from utilities.helper import download_file, mediainfo

from . import check_filename, get_string, inline_mention, ultroid_cmd


@ultroid_cmd(pattern="logo( (.*)|$)")
async def logo_func(event):
    xx = await event.eor(get_string("com_1"))
    name = event.pattern_match.group(1).strip()
    if not name:
        return await xx.eor("`Give a name too!`", time=5)
    bg_, font_ = None, None
    if event.reply_to_msg_id:
        temp = await event.get_reply_message()
        if temp.media:
            if hasattr(temp.media, "document") and (
                ("font" in temp.file.mime_type)
                or (".ttf" in temp.file.name)
                or (".otf" in temp.file.name)
            ):
                font_ = await temp.download_media("resources/fonts/")
            elif "pic" in mediainfo(temp.media):
                bg_ = await temp.download_media()
    if not bg_:
        if event.client._bot:
            SRCH = [
                "blur background",
                "background",
                "neon lights",
                "nature",
                "abstract",
                "space",
                "3d render",
            ]
            with rm.get("search", helper=True, dispose=True) as mod:
                res = await mod.unsplash(random.choice(SRCH), limit=1)
            bg_, _ = await download_file(res[0], "resources/downloads/logo.png")
            newimg = "resources/downloads/unsplash-temp.jpg"
            img_ = Image.open(bg_)
            img_.resize((5000, 5000)).save(newimg)
            os.remove(bg_)
            bg_ = newimg
        else:
            pics = []
            async for i in event.client.iter_messages(
                "@UltroidLogos", filter=InputMessagesFilterPhotos
            ):
                pics.append(i)
            id_ = random.choice(pics)
            bg_ = await id_.download_media()

    if not font_:
        fpath_ = glob.glob("resources/fonts/*")
        if not bool(fpath_):
            return await xx.edit("Add fonts in `resourses/fonts/` directory before using this command.")
        font_ = random.choice(fpath_)
    if len(name) <= 8:
        strke = 10
    elif len(name) >= 9:
        strke = 5
    else:
        strke = 20
    name = LogoHelper.make_logo(
        bg_,
        name,
        font_,
        fill="white",
        stroke_width=strke,
        stroke_fill="black",
    )
    await xx.edit("`Done!`")
    await event.client.send_file(
        event.chat_id,
        file=name,
        caption=f"Logo by {inline_mention(event.client.me)}",
        force_document=True,
    )
    os.remove(name)
    await xx.delete()
    if os.path.exists(bg_):
        os.remove(bg_)


class LogoHelper:
    @staticmethod
    def find_font_size(text, font, image, target_width_ratio):
        tested_font_size = 100
        tested_font = ImageFont.truetype(font, tested_font_size)
        observed_width, observed_height = tested_font.getsize(text)
        estimated_font_size = (
            tested_font_size / (observed_width /
                                image.width) * target_width_ratio
        )
        return round(estimated_font_size)

    @staticmethod
    def make_logo(imgpath, text, funt, **args):
        fill = args.get("fill")
        width_ratio = args.get("width_ratio") or 0.7
        stroke_width = int(args.get("stroke_width"))
        stroke_fill = args.get("stroke_fill")

        img = Image.open(imgpath)
        width, height = img.size
        draw = ImageDraw.Draw(img)
        font_size = LogoHelper.find_font_size(text, funt, img, width_ratio)
        font = ImageFont.truetype(funt, font_size)
        w, h = font.getsize(text)
        draw.text(
            ((width - w) / 2, (height - h) / 2),
            text,
            font=font,
            fill=fill,
            stroke_width=stroke_width,
            stroke_fill=stroke_fill,
        )
        file_name = check_filename("logo.png")
        img.save(file_name, "PNG")
        return file_name
