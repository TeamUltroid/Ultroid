# Ultroid - UserBot
# Copyright (C) 2021 TeamUltroid
#
# This file is a part of < https://github.com/TeamUltroid/Ultroid/ >
# PLease read the GNU Affero General Public License in
# <https://www.github.com/TeamUltroid/Ultroid/blob/main/LICENSE/>.
"""
✘ Commands Available -

• `{i}install <reply to plugin>`
    To install the plugin,
  `{i}install f`
    To force Install.

• `{i}uninstall <plugin name>`
    To unload and remove the plugin.

• `{i}load <plugin name>`
    To load unloaded unofficial plugin.

• `{i}unload <plugin name>`
    To unload unofficial plugin.

• `{i}help <plugin name>`
    Shows you a help menu (like this) for every plugin.

• `{i}getaddons <raw link to code>`
    Load Plugins from the given raw link.
"""

import os

from pyUltroid.startup.loader import load_addons

from . import eod, eor, get_string, requests, safeinstall, ultroid_cmd, un_plug


@ultroid_cmd(pattern="install", fullsudo=True)
async def install(event):
    await safeinstall(event)


@ultroid_cmd(
    pattern=r"unload ?(.*)",
)
async def unload(event):
    shortname = event.pattern_match.group(1)
    if not shortname:
        await eor(event, get_string("core_9"))
        return
    lsd = os.listdir("addons")
    lst = os.listdir("plugins")
    zym = shortname + ".py"
    if zym in lsd:
        try:
            un_plug(shortname)
            await eor(event, f"**Uɴʟᴏᴀᴅᴇᴅ** `{shortname}` **Sᴜᴄᴄᴇssғᴜʟʟʏ.**", time=3)
        except Exception as ex:
            return await eor(event, str(ex))
    elif zym in lst:
        return await eor(event, get_string("core_11"), time=3)
    else:
        return await eor(event, f"**Nᴏ Pʟᴜɢɪɴ Nᴀᴍᴇᴅ** `{shortname}`", time=3)


@ultroid_cmd(
    pattern=r"uninstall ?(.*)",
)
async def uninstall(event):
    shortname = event.pattern_match.group(1)
    if not shortname:
        await eor(event, get_string("core_13"))
        return
    lsd = os.listdir("addons")
    lst = os.listdir("plugins")
    zym = shortname + ".py"
    if zym in lsd:
        try:
            un_plug(shortname)
            await eor(event, f"**Uɴɪɴsᴛᴀʟʟᴇᴅ** `{shortname}` **Sᴜᴄᴄᴇssғᴜʟʟʏ.**", time=3)
            os.remove(f"addons/{shortname}.py")
        except Exception as ex:
            return await eor(event, str(ex))
    elif zym in lst:
        return await eor(event, get_string("core_15"), time=3)
    else:
        return await eor(event, f"**Nᴏ Pʟᴜɢɪɴ Nᴀᴍᴇᴅ** `{shortname}`", time=3)


@ultroid_cmd(
    pattern=r"load ?(.*)",
    fullsudo=True,
)
async def load(event):
    shortname = event.pattern_match.group(1)
    if not shortname:
        await eor(event, get_string("core_16"))
        return
    try:
        try:
            un_plug(shortname)
        except BaseException:
            pass
        load_addons(shortname)
        await eor(event, get_string("core_17").format(shortname), time=3)
    except Exception as e:
        await eod(
            event,
            get_string("core_18").format(shortname, e),
            time=3,
        )


@ultroid_cmd(pattern="getaddons ?(.*)", fullsudo=True)
async def get_the_addons_lol(event):
    thelink = event.pattern_match.group(1)
    xx = await eor(event, get_string("com_1"))
    fool = get_string("gas_1")
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
        await eor(xx, get_string("core_17").format(shortname), time=15)
    except Exception as e:
        await eod(
            xx,
            get_string("core_18").format(shortname, e),
            time=3,
        )
