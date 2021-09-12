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
"""

import os

from . import *


@ultroid_cmd(pattern="install", fullsudo=True)
async def install(event):
    await safeinstall(event)


@ultroid_cmd(
    pattern=r"unload ?(.*)",
)
async def unload(event):
    shortname = event.pattern_match.group(1)
    if not shortname:
        await eor(event, "`Give name of plugin which u want to unload`")
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
        return await eor(event, "**Yᴏᴜ Cᴀɴ'ᴛ Uɴʟᴏᴀᴅ Oғғɪᴄɪᴀʟ Pʟᴜɢɪɴs**", time=3)
    else:
        return await eor(event, f"**Nᴏ Pʟᴜɢɪɴ Nᴀᴍᴇᴅ** `{shortname}`", time=3)


@ultroid_cmd(
    pattern=r"uninstall ?(.*)",
)
async def uninstall(event):
    shortname = event.pattern_match.group(1)
    if not shortname:
        await eor(event, "`Give name of plugin which u want to uninstall`")
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
        return await eor(event, "**Yᴏᴜ Cᴀɴ'ᴛ Uɴɪɴsᴛᴀʟʟ Oғғɪᴄɪᴀʟ Pʟᴜɢɪɴs**", time=3)
    else:
        return await eor(event, f"**Nᴏ Pʟᴜɢɪɴ Nᴀᴍᴇᴅ** `{shortname}`", time=3)


@ultroid_cmd(
    pattern=r"load ?(.*)",
    fullsudo=True,
)
async def load(event):
    shortname = event.pattern_match.group(1)
    if not shortname:
        await eor(event, "`Give name of plugin which u want to load`")
        return
    try:
        try:
            un_plug(shortname)
        except BaseException:
            pass
        load_addons(shortname)
        await eor(event, f"**Sᴜᴄᴄᴇssғᴜʟʟʏ Lᴏᴀᴅᴇᴅ** `{shortname}`", time=3)
    except Exception as e:
        await eod(
            event,
            f"**Could not load** `{shortname}` **because of the following error.**\n`{e}`",
            time=3,
        )
