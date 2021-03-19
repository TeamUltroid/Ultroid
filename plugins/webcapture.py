# Ultroid - UserBot
# Copyright (C) 2020 TeamUltroid
#
# This file is a part of < https://github.com/TeamUltroid/Ultroid/ >
# PLease read the GNU Affero General Public License in
# <https://www.github.com/TeamUltroid/Ultroid/blob/main/LICENSE/>.

"""
✘ Commands Available -

• `{i}webshot <url>`
    Get a screenshot of the webpage.

"""

from . import *
import requests

@ultroid_cmd(pattern="webshot")
async def webss(event):
    xx = await eor(event, get_string("com_1"))
    mssg = event.text.split(' ', maxsplit=2)
    try:
        xurl = mssg[1]
    except IndexError:
        return await eod(xx, "`Give a URL please!`", time=5)
    try:
        response = requests.get(xurl)
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

    lnk = f"https://screenshotapi.net/api/v1/screenshot?url={xurl}"
    ok = requests.get(lnk).json()
    try:
        sshot = ok["screenshot"]
        crt_at = ok["created_at"]
    except:
        return await eod(xx, "Something Went Wrong :(", time=10)
    await xx.reply(f"**WebShot Generated**\n**Url**: {xurl}\n**Created at**: {crt_at}", file=sshot, link_preview=False)
    await xx.delete()