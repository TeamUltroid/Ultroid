# Ultroid - UserBot
# Copyright (C) 2021-2025 TeamUltroid
#
# This file is a part of < https://github.com/TeamUltroid/Ultroid/ >
# PLease read the GNU Affero General Public License in
# <https://www.github.com/TeamUltroid/Ultroid/blob/main/LICENSE/>.


from . import get_help

__doc__ = get_help("help_core")


import os
import aiohttp
import base64
from pathlib import Path
from pyUltroid.startup.loader import load_addons
from pyUltroid.state_config import temp_config_store
from pyUltroid.configs import CENTRAL_REPO_URL
import ast

from . import LOGS, async_searcher, eod, get_string, safeinstall, ultroid_cmd, un_plug, ultroid_bot


@ultroid_cmd(pattern="install", fullsudo=True)
async def install(event):
    await safeinstall(event)


@ultroid_cmd(
    pattern=r"unload( (.*)|$)",
)
async def unload(event):
    shortname = event.pattern_match.group(1).strip()
    if not shortname:
        await event.eor(get_string("core_9"))
        return
    lsd = os.listdir("addons")
    zym = f"{shortname}.py"
    if zym in lsd:
        try:
            un_plug(shortname)
            await event.eor(f"**Uɴʟᴏᴀᴅᴇᴅ** `{shortname}` **Sᴜᴄᴄᴇssғᴜʟʟʏ.**", time=3)
        except Exception as ex:
            LOGS.exception(ex)
            return await event.eor(str(ex))
    elif zym in os.listdir("plugins"):
        return await event.eor(get_string("core_11"), time=3)
    else:
        await event.eor(f"**Nᴏ Pʟᴜɢɪɴ Nᴀᴍᴇᴅ** `{shortname}`", time=3)


@ultroid_cmd(
    pattern=r"uninstall( (.*)|$)",
)
async def uninstall(event):
    shortname = event.pattern_match.group(1).strip()
    if not shortname:
        await event.eor(get_string("core_13"))
        return
    lsd = os.listdir("addons")
    zym = f"{shortname}.py"
    if zym in lsd:
        try:
            un_plug(shortname)
            await event.eor(f"**Uɴɪɴsᴛᴀʟʟᴇᴅ** `{shortname}` **Sᴜᴄᴄᴇssғᴜʟʟʏ.**", time=3)
            os.remove(f"addons/{shortname}.py")
        except Exception as ex:
            return await event.eor(str(ex))
    elif zym in os.listdir("plugins"):
        return await event.eor(get_string("core_15"), time=3)
    else:
        return await event.eor(f"**Nᴏ Pʟᴜɢɪɴ Nᴀᴍᴇᴅ** `{shortname}`", time=3)


@ultroid_cmd(
    pattern=r"load( (.*)|$)",
    fullsudo=True,
)
async def load(event):
    shortname = event.pattern_match.group(1).strip()
    if not shortname:
        await event.eor(get_string("core_16"))
        return
    try:
        try:
            un_plug(shortname)
        except BaseException:
            pass
        load_addons(f"addons/{shortname}.py")
        await event.eor(get_string("core_17").format(shortname), time=3)
    except Exception as e:
        LOGS.exception(e)
        await eod(
            event,
            get_string("core_18").format(shortname, e),
            time=3,
        )


@ultroid_cmd(pattern="getaddons( (.*)|$)", fullsudo=True)
async def get_the_addons_lol(event):
    thelink = event.pattern_match.group(1).strip()
    xx = await event.eor(get_string("com_1"))
    fool = get_string("gas_1")
    if thelink is None:
        return await xx.eor(fool, time=10)
    split_thelink = thelink.split("/")
    if not ("raw" in thelink and thelink.endswith(".py")):
        return await xx.eor(fool, time=10)
    name_of_it = split_thelink[-1]
    plug = await async_searcher(thelink)
    fil = f"addons/{name_of_it}"
    await xx.edit("Packing the codes...")
    with open(fil, "w", encoding="utf-8") as uult:
        uult.write(plug)
    await xx.edit("Packed. Now loading the plugin..")
    shortname = name_of_it.split(".")[0]
    try:
        load_addons(fil)
        await xx.eor(get_string("core_17").format(shortname), time=15)
    except Exception as e:
        LOGS.exception(e)
        await eod(
            xx,
            get_string("core_18").format(shortname, e),
            time=3,
        )


@ultroid_cmd(pattern="publishpg", fullsudo=True)
async def publish_plugin_from_reply(event):
    reply = await event.get_reply_message()
    if not (reply and reply.document):
        return await event.eor("Reply to a plugin file or code to publish.")
    file_path = await reply.download_media()

    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()

    plugin_filename = Path(file_path).name
    bot_id = ultroid_bot.me.id
    encoded_init_data = temp_config_store.get(f"X-TG-INIT-DATA-{bot_id}")
    encoded_hash = temp_config_store.get(f"X-TG-HASH-{bot_id}")
    if not encoded_init_data or not encoded_hash:
        return await event.eor("Authentication data not found. Please authenticate with Ultroid Central first.")

    init_data = base64.b64decode(encoded_init_data.encode()).decode()
    hash_value = base64.b64decode(encoded_hash.encode()).decode()

    title = plugin_filename.replace('_', ' ').replace('.py', '').title()
    try:
        docstring = ast.get_docstring(ast.parse(content))
    except Exception:
        docstring = None
    description = docstring or "Uploaded from Ultroid via publishpg command."
    tags = [plugin_filename.replace('.py', '')]
    packages = []
    commands = []

    json_data = {
        "title": title,
        "description": description,
        "tags": tags,
        "packages": packages,
        "commands": commands,
        "is_trusted": False,
        "is_official": False,
        "plugin_filename": plugin_filename,
        "plugin_content": base64.b64encode(content.encode('utf-8')).decode('utf-8')
    }

    headers = {
        "Content-Type": "application/json",
        "X-Telegram-Init-Data": init_data,
        "X-Telegram-Hash": hash_value
    }

    async with aiohttp.ClientSession() as session:
        plugin_url = f"{CENTRAL_REPO_URL}/api/v1/plugins"
        async with session.post(plugin_url, json=json_data, headers=headers) as response:
            status = response.status
            resp_text = await response.text()
            if status in (200, 201):
                await event.eor(f"✅ Successfully published plugin `{title}`.")
            else:
                await event.eor(f"❌ Failed to publish plugin. Status: {status}\n{resp_text[:200]}")

    Path(file_path).unlink(missing_ok=True)
