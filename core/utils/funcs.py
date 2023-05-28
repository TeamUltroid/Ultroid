import asyncio
import os
import time

from core import LOGS, asst, udB, ultroid_bot
from core.loader import load
from core.remote import rm

from utilities.helper import unload_plugin
from database._core import PluginChannel
from telethon.events import NewMessage, MessageDeleted


async def onNewPlugin(ult):
    chat = ult.chat_id
    file = await ult.download_media(f"modules/channels/c{chat}/")
    from .addons import load_addons

    load_addons(file)
    if PluginChannel.get(ult.chat_id) is None:
        PluginChannel[ult.chat_id] = {}
    PluginChannel[ult.chat_id][ult.id] = file
    LOGS.debug(f"Loaded new plugin {file} from {ult.chat_id}")


async def onPluginDel(ult):
    chat = ult.chat_id
    for msg in ult.deleted_ids:
        if plugin := PluginChannel[chat].get(msg):
            if unload_plugin(plugin):
                LOGS.info(f"Successfully Unloaded {plugin}!")


async def WasItRestart(key):
    try:
        chat, _id, sender = key
        await (asst if sender == "bot" else ultroid_bot).edit_message(
            chat, _id, "__Restarted Successfully.__"
        )
    except Exception as er:
        LOGS.exception(er)
    udB.del_key("_RESTART")


async def plug(plugin_channels):
    if ultroid_bot._bot:
        LOGS.info("Plugin Channels can't be used in 'BOTMODE'")
        return
    with rm.get("plugin_channel", helper=True, dispose=True) as modl:
        await modl.get_from_channels(plugin_channels)
    ultroid_bot.add_handler(
        onNewPlugin,
        NewMessage(
            chats=plugin_channels, func=lambda e: e.file and e.file.name.endswith(".py")
        ),
    )
    ultroid_bot.add_handler(
        onPluginDel,
        MessageDeleted(
            func=lambda ult: PluginChannel.get(ult.chat_id), chats=plugin_channels
        ),
    )


async def get_notifier(*args):
    with rm.get("notifier", helper=True, dispose=True) as modl:
        await modl.notify(*args)


async def process_main():
    tasks = []
    # Load Plugins
    if plugin_channels := udB.get_key("PLUGIN_CHANNEL"):
        tasks.append(plug(plugin_channels))

    # Update Restart message
    if res := udB.get_key("_RESTART"):
        tasks.append(WasItRestart(res))

    # Notify: send message
    if (init := not udB.get_key("INIT_DEPLOY")) or udB.get_key("NOTIFY"):
        tasks.append(get_notifier(init))

    tz = udB.get_key("TIMEZONE")
    if tz and os.environ.get("TZ") != tz and hasattr(time, "tzset"):
        with rm.get("timezone", helper=True, dispose=True) as modl:
            if modl:
                modl.set_timezone(tz)

    # Run: task in background
    await asyncio.gather(*tasks)


def setup_addons():
    if not os.path.exists("modules/addons"):
        os.mkdir("modules/addons")
        with open("modules/addons/__init__.py", "w") as file:
            file.write("from .. import *")


async def load_plugins():
    # GET: Addons plugins

    plugins = None
    load_path = ["modules/basic", "modules/addons", "modules/assistant"]

    async def _fetch(plugs, folder, **kwargs):
        return await asyncio.gather(
            *[
                rm.async_import(plug, f"modules/{folder}/{plug}.py", **kwargs)
                for plug in plugs
            ]
        )

    async def fetch_all(end="getallplugins", folder="addons", **kwargs):
        plugs = await rm.get_all_plugins(end)
        if folder == "addons":
            excl = udB.get_key("EXCLUDE_PLUGINS")
            if excl and (excl := excl.split(",")):
                [plugs.remove(spl) for spl in excl if spl in plugs]
        await _fetch(plugs, folder, **kwargs)
        load_path.append(f"modules/{folder}")

    if plugins := udB.get_key("PLUGINS"):
        setup_addons()
        plugins = list(filter(lambda e: e, await _fetch(plugins.split(","), "addons")))

    elif udB.get_key("LOAD_ALL"):
        setup_addons()
        await fetch_all()

    if udB.get_config("MANAGER"):
        if not os.path.exists("modules/manager"):
            os.mkdir("modules/manager")
        await fetch_all("getmanager", "manager", manager=True)

    rm.set_status_done()

    load(path=load_path, plugins=plugins)

    if udB.get_config("PMBOT"):
        with rm.get("pmbot", helper=True, dispose=True):
            LOGS.info("Loaded PMBOT.")

    if udB.get_config("VCBOT"):
        try:
            with rm.get("setup_vcbot", helper=True, dispose=True) as mod:
                await mod.setup()
        except Exception as er:
            LOGS.exception(er)

    if not udB.get_key("INIT_DEPLOY"):
        udB.set_key("INIT_DEPLOY", True)
