import asyncio
import os

from core import ultroid_bot
from core.setup import LOGS
from core.utils.addons import load_addons
from database._core import PluginChannel
from telethon.tl.types import InputMessagesFilterDocument


async def get_from_channels(plugin_channels):
    if not os.path.exists("addons"):
        os.mkdir("addons")
    LOGS.info("• Loading Plugins from Plugin Channel(s) •")
    for chat in plugin_channels:
        if PluginChannel.get(chat) is None:
            PluginChannel[chat] = {}
        LOGS.info(f"{'•'*4} {chat}")
        try:
            async for x in ultroid_bot.iter_messages(
                chat, search=".py", filter=InputMessagesFilterDocument, wait_time=10
            ):
                plugin = "addons/" + \
                    x.file.name.replace("_", "-").replace("|", "-")
                if not os.path.exists(plugin):
                    await asyncio.sleep(0.6)
                    if x.text == "#IGNORE":
                        continue
                    plugin = await x.download_media(plugin)
                PluginChannel[chat][x.id] = plugin
                try:
                    load_addons(plugin)
                except Exception as e:
                    LOGS.info(f"Ultroid - PLUGIN_CHANNEL - ERROR - {plugin}")
                    LOGS.exception(e)
                    os.remove(plugin)
        except Exception as er:
            LOGS.exception(er)
