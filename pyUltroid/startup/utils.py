# Ultroid - UserBot
# Copyright (C) 2021-2022 TeamUltroid
#
# This file is a part of < https://github.com/TeamUltroid/Ultroid/ >
# PLease read the GNU Affero General Public License in
# <https://github.com/TeamUltroid/pyUltroid/blob/main/LICENSE>.

from importlib import util
from sys import modules

# for addons


def load_addons(plugin_name):
    base_name = plugin_name.split("/")[-1].split("\\")[-1].replace(".py", "")
    if base_name.startswith("__"):
        return
    from .. import HNDLR, LOGS, asst, udB, ultroid_bot
    from .._misc import _supporter as xxx
    from .._misc._assistant import asst_cmd, callback, in_pattern
    from .._misc._decorators import ultroid_cmd
    from .._misc._supporter import Config, admin_cmd, sudo_cmd
    from .._misc._wrappers import eod, eor
    from ..configs import Var
    from ..dB._core import HELP

    name = plugin_name.replace("/", ".").replace("\\", ".")
    spec = util.spec_from_file_location(name, plugin_name)
    mod = util.module_from_spec(spec)
    mod.LOG_CHANNEL = udB.get_key("LOG_CHANNEL")
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
    mod.HELP = HELP.get("Addons", {})
    mod.CMD_HELP = HELP.get("Addons", {})
    modules["ub"] = xxx
    modules["var"] = xxx
    modules["jarvis"] = xxx
    modules["support"] = xxx
    modules["userbot"] = xxx
    modules["telebot"] = xxx
    modules["fridaybot"] = xxx
    modules["jarvis.utils"] = xxx
    modules["uniborg.util"] = xxx
    modules["telebot.utils"] = xxx
    modules["userbot.utils"] = xxx
    modules["userbot.events"] = xxx
    modules["jarvis.jconfig"] = xxx
    modules["userbot.config"] = xxx
    modules["fridaybot.utils"] = xxx
    modules["fridaybot.Config"] = xxx
    modules["userbot.uniborgConfig"] = xxx
    spec.loader.exec_module(mod)
    modules[name] = mod
    doc = modules[name].__doc__.format(i=HNDLR) if modules[name].__doc__ else ""
    if "Addons" in HELP.keys():
        update_cmd = HELP["Addons"]
        try:
            update_cmd.update({base_name: doc})
        except BaseException:
            pass
    else:
        try:
            HELP.update({"Addons": {base_name: doc}})
        except BaseException as em:
            pass
