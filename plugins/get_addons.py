# Ultroid - UserBot
# Copyright (C) 2021 TeamUltroid
#
# This file is a part of < https://github.com/TeamUltroid/Ultroid/ >
# PLease read the GNU Affero General Public License in
# <https://www.github.com/TeamUltroid/Ultroid/blob/main/LICENSE/>.

"""
✘ Commands Available -

• `{i}getaddons <raw link to code>`
    Load Plugins from the given raw link.
"""

import requests
from pyUltroid.startup.utils import load_addons

from . import *


@ultroid_cmd(pattern="getaddons ?(.*)")
async def get_the_addons_lol(event):
    thelink = event.pattern_match.group(1)
    xx = await eor(event, get_string("com_1"))
    fool = "Please provide a raw link!"
    if thelink is None:
        return await eor(xx, fool, time=10)
    split_thelink = thelink.split("/")
    if "raw" not in thelink:
        return await eor(xx, fool, time=10)
    name_of_it = split_thelink[(len(split_thelink) - 1)]
    plug = requests.get(thelink).text
    fil = f"addons/{name_of_it}"
    await xx.edit("Packing the codes...")
    with open(fil, "w", encoding="utf-8") as uult:
        uult.write(plug)
    await xx.edit("Packed. Now loading the plugin..")
    shortname = name_of_it.split(".")[0]
    try:
        load_addons(shortname)
        await eor(xx, f"**Sᴜᴄᴄᴇssғᴜʟʟʏ Lᴏᴀᴅᴇᴅ** `{shortname}`", time=15)
    except Exception as e:
        await eod(
            xx,
            f"**Could not load** `{shortname}` **because of the following error.**\n`{e}`",
            time=3,
        )
