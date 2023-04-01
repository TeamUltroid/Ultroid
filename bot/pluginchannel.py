import asyncio
import os, shutil

from core import ultroid_bot
from core.setup import LOGS
from core.utils.addons import load_addons
from telethon.tl.types import InputMessagesFilterDocument


async def get_from_channels(plugin_channels):
    if not os.path.exists("modules/channels"):
        os.mkdir("modules/channels")
    LOGS.info("• Loading Plugins from Plugin Channel(s) •")
    for chat in plugin_channels:
        LOGS.info(f"{'•'*4} {chat}")
        _path = f"modules/channels/c{chat}/"
        # Clear, to remove deleted plugins
        if os.path.exists(_path):
            shutil.rmtree(_path)
        os.mkdir(_path)
        with open(f"{_path}/__init__.py", "w") as file:
            file.write("from modules import *")
        try:
            async for x in ultroid_bot.iter_messages(
                chat, search=".py", filter=InputMessagesFilterDocument, wait_time=7
            ):
                plugin = _path + \
                    x.file.name.replace("_", "-").replace("|", "-")
                if not os.path.exists(plugin):
                    await asyncio.sleep(0.6)
                    if x.text == "#IGNORE":
                        continue
                    plugin = await x.download_media(plugin)
                try:
                    load_addons(plugin)
                except Exception as e:
                    LOGS.info(f"Ultroid - PLUGIN_CHANNEL - ERROR - {plugin}")
                    LOGS.exception(e)
                    os.remove(plugin)
        except Exception as er:
            LOGS.exception(er)
