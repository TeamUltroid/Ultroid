# Ultroid - UserBot
# Copyright (C) 2020-2023 TeamUltroid
#
# This file is a part of < https://github.com/TeamUltroid/Ultroid/ >
# PLease read the GNU Affero General Public License in
# <https://github.com/TeamUltroid/pyUltroid/blob/main/LICENSE>.

from importlib import util
from sys import modules

from core import HNDLR, LOGS, asst, udB, ultroid_bot
from core.config import Var
from core.decorators import _supporter as config
from core.decorators._assistant import asst_cmd, callback, in_pattern
from core.decorators._decorators import ultroid_cmd
from core.decorators._supporter import Config, admin_cmd, sudo_cmd
from core.decorators._wrappers import eod, eor
from database._core import CMD_HELP as HELP

# for addons

configPaths = [
    "ub",
    "var",
    "support",
    "userbot",
    "telebot",
    "fridaybot",
    "uniborg.util",
    "telebot.utils",
    "userbot.utils",
    "userbot.events",
    "userbot.config",
    "fridaybot.utils",
    "fridaybot.Config",
    "userbot.uniborgConfig",
]


def load_addons(plugin_name):
    import core
    import modules as m

    base_name = plugin_name.split("/")[-1].split("\\")[-1].replace(".py", "")
    if base_name.startswith("__"):
        return
    name = plugin_name.replace("/", ".").replace("\\", ".").replace(".py", "")
    spec = util.spec_from_file_location(name, plugin_name)
    mod = util.module_from_spec(spec)
    for path in configPaths:
        modules[path] = config
    modules["pyUltroid"] = core
    modules["plugins"] = m
    mod.LOG_CHANNEL = udB.get_config("LOG_CHANNEL")
    mod.udB = udB
    mod.asst = asst
    mod.tgbot = asst
    mod.ultroid_bot = ultroid_bot
    mod.ub = ultroid_bot
    mod.bot = ultroid_bot
    mod.ultroid = ultroid_bot
    mod.borg = ultroid_bot
    mod.telebot = ultroid_bot
    mod.jarvis = ultroid_bot
    mod.friday = ultroid_bot
    mod.eod = eod
    mod.edit_delete = eod
    mod.LOGS = LOGS
    mod.in_pattern = in_pattern
    mod.hndlr = HNDLR
    mod.handler = HNDLR
    mod.HNDLR = HNDLR
    mod.CMD_HNDLR = HNDLR
    mod.Config = Config
    mod.Var = Var
    mod.eor = eor
    mod.edit_or_reply = eor
    mod.asst_cmd = asst_cmd
    mod.ultroid_cmd = ultroid_cmd
    mod.on_cmd = ultroid_cmd
    mod.callback = callback
    mod.Redis = udB.get_key
    mod.admin_cmd = admin_cmd
    mod.sudo_cmd = sudo_cmd
    mod.HELP = HELP
    mod.CMD_HELP = HELP

    spec.loader.exec_module(mod)
    modules[name] = mod
    doc = modules[name].__doc__.format(i=HNDLR) if modules[name].__doc__ else ""
    if "Addons" in HELP.keys():
        update_cmd = HELP
        try:
            update_cmd.update({base_name: doc})
        except BaseException:
            pass
    else:
        try:
            HELP[base_name] = doc
        except BaseException:
            pass
