# Ultroid - UserBot
# Copyright (C) 2020 TeamUltroid
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

from telethon import Button

from . import *


@in_pattern(
    "send ?(.*)",
)
@in_owner
async def inline_handler(event):
    builder = event.builder
    input_str = event.pattern_match.group(1)
    plug = [*PLUGINS]
    plugs = []
    if input_str == None or input_str == "":
        for i in plug:
            try:
                plugs.append(
                    await event.builder.document(
                        f"./plugins/{i}.py",
                        title=f"{i}.py",
                        description=f"Module Found",
                        text=f"{i}.py use .paste to paste in neko and raw..",
                        buttons=[
                            [
                                Button.switch_inline(
                                    "Search Again..?", query="send ", same_peer=True
                                )
                            ]
                        ],
                    )
                )
            except BaseException:
                pass
        await event.answer(plugs)
    else:
        try:
            ultroid = builder.document(
                f"./plugins/{input_str}.py",
                title=f"{input_str}.py",
                description=f"Module {input_str} Found",
                text=f"{input_str}.py use .paste to paste in neko and raw..",
                buttons=[
                    [
                        Button.switch_inline(
                            "Search Again..?", query="send ", same_peer=True
                        )
                    ]
                ],
            )
            await event.answer([ultroid])
            return
        except BaseException:
            ultroidcode = builder.article(
                title=f"Module {input_str}.py Not Found",
                description=f"No Such Module",
                text=f"No Module Named {input_str}.py",
                buttons=[
                    [
                        Button.switch_inline(
                            "Search Again", query="send ", same_peer=True
                        )
                    ]
                ],
            )
            await event.answer([ultroidcode])
            return


@ultroid_cmd(
    pattern="install",
)
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
            await eod(event, f"**Uɴʟᴏᴀᴅᴇᴅ** `{shortname}` **Sᴜᴄᴄᴇssғᴜʟʟʏ.**", time=3)
        except Exception as ex:
            return await eor(event, str(ex))
    elif zym in lst:
        return await eod(event, "**Yᴏᴜ Cᴀɴ'ᴛ Uɴʟᴏᴀᴅ Oғғɪᴄɪᴀʟ Pʟᴜɢɪɴs**", time=3)
    else:
        return await eod(event, f"**Nᴏ Pʟᴜɢɪɴ Nᴀᴍᴇᴅ** `{shortname}`", time=3)


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
            await eod(event, f"**Uɴɪɴsᴛᴀʟʟᴇᴅ** `{shortname}` **Sᴜᴄᴄᴇssғᴜʟʟʏ.**", time=3)
            os.remove(f"addons/{shortname}.py")
        except Exception as ex:
            return await eor(event, str(ex))
    elif zym in lst:
        return await eod(event, "**Yᴏᴜ Cᴀɴ'ᴛ Uɴɪɴsᴛᴀʟʟ Oғғɪᴄɪᴀʟ Pʟᴜɢɪɴs**", time=3)
    else:
        return await eod(event, f"**Nᴏ Pʟᴜɢɪɴ Nᴀᴍᴇᴅ** `{shortname}`", time=3)


@ultroid_cmd(
    pattern=r"load ?(.*)",
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
        await eod(event, f"**Sᴜᴄᴄᴇssғᴜʟʟʏ Lᴏᴀᴅᴇᴅ** `{shortname}`", time=3)
    except Exception as e:
        await eod(
            event,
            f"**Could not load** `{shortname}` **because of the following error.**\n`{str(e)}`",
            time=3,
        )


HELP.update({f"{__name__.split('.')[1]}": f"{__doc__.format(i=HNDLR)}"})
