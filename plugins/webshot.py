# Ultroid - UserBot
# Copyright (C) 2021 TeamUltroid
#
# This file is a part of < https://github.com/TeamUltroid/Ultroid/ >
# PLease read the GNU Affero General Public License in
# <https://www.github.com/TeamUltroid/Ultroid/blob/main/LICENSE/>.

"""
✘ Commands Available -

• `{i}webshot <url>`
    Get a screenshot of the webpage.

"""

import io

import requests
from selenium import webdriver

from . import *


@ultroid_cmd(pattern="webshot")
async def webss(event):
    xx = await eor(event, get_string("com_1"))
    mssg = event.text.split(" ", maxsplit=2)
    try:
        xurl = mssg[1]
    except IndexError:
        return await eod(xx, "`Give a URL please!`", time=5)
    try:
        requests.get(xurl)
    except requests.ConnectionError:
        return await eod(xx, "Invalid URL!", time=5)
    except requests.exceptions.MissingSchema:
        try:
            r = requests.get("https://" + xurl)
        except requests.ConnectionError:
            try:
                r2 = requests.get("http://" + xurl)
            except requests.ConnectionError:
                return await eod(xx, "Invalid URL!", time=5)
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument("--ignore-certificate-errors")
    chrome_options.add_argument("--test-type")
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.binary_location = "/usr/bin/google-chrome"
    driver = webdriver.Chrome(chrome_options=chrome_options)
    driver.get(xurl)
    height = driver.execute_script(
        "return Math.max(document.body.scrollHeight, document.body.offsetHeight, document.documentElement.clientHeight, document.documentElement.scrollHeight, document.documentElement.offsetHeight);"
    )
    width = driver.execute_script(
        "return Math.max(document.body.scrollWidth, document.body.offsetWidth, document.documentElement.clientWidth, document.documentElement.scrollWidth, document.documentElement.offsetWidth);"
    )
    driver.set_window_size(width + 100, height + 100)
    im_png = driver.get_screenshot_as_png()
    driver.close()
    with io.BytesIO(im_png) as sshot:
        sshot.name = "webshot.png"
        await xx.reply(
            f"**WebShot Generated**\n**URL**: {xurl}",
            file=sshot,
            link_preview=False,
            force_document=True,
        )
    await xx.delete()
