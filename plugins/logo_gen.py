# Ultroid - UserBot
# Copyright (C) 2020 TeamUltroid
#
# This file is a part of < https://github.com/TeamUltroid/Ultroid/ >
# PLease read the GNU Affero General Public License in
# <https://www.github.com/TeamUltroid/Ultroid/blob/main/LICENSE/>.

"""
✘ Commands Available -

• `{i}logo <name>`
   Generate a logo of the give

"""

import random
import os
from PIL import Image, ImageDraw, ImageFont
from . import *
import time

@ultroid_cmd(pattern="logo ?(.*)")
async def logo_gen(event):
    xx = await eor(event, get_string("com_1"))
    name = event.pattern_match.group(1)
    if not name:
        await eod(xx, "`Give a name too!`", time=5)
    fpath_ = "./resources/fonts/"
    bpath_ = "./resources/bgs/"
    f = random.choice(os.listdir(fpath_))
    bg = random.choice(os.listdir(bpath_))
    font_ = fpath_ + f
    bg_ = bpath_ + bg
    # next level logic, ignore
    if len(name) < 8:
        fnt_size = 150
        strke = 10
    elif len(name) > 10:
        fnt_size = 50
        strke = 5
    else:
        fnt_size = 130
        strke = 20
    img = Image.open(bg_)
    draw = ImageDraw.Draw(img)
    font = ImageFont.truetype(font_, fnt_size)
    w, h = draw.textsize(name, font=font)
    h += int(h*0.21)
    image_width, image_height = img.size
    draw.text(((image_width-w)/2, (image_height-h)/2), name, font=font, fill=(255, 255, 255))
    x = (image_width-w)/2
    y = (image_height-h)/2
    draw.text((x, y), name, font=font, fill="white", stroke_width=strke, stroke_fill="black")
    flnme = f"ultd.png"
    img.save(flnme, "png")
    await xx.edit("`Done!`")
    if os.path.exists(flnme):
        tt = time.time()
        up = await uploader(flnme, flnme, tt, xx, "`Uploading...`")
        await ultroid.send_file(event.chat_id, file=up, caption=f"Logo by [{OWNER_NAME}](tg://user?id={OWNER_ID})", foce_document=True)
        os.remove(flnme)
        await xx.delete()

HELP.update({f"{__name__.split('.')[1]}": f"{__doc__.format(i=HNDLR)}"})
