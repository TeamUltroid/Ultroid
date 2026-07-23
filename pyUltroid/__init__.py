# Ultroid - UserBot
# Copyright (C) 2021-2026 TeamUltroid
#
# This file is a part of < https://github.com/TeamUltroid/Ultroid/ >
# PLease read the GNU Affero General Public License in
# <https://github.com/TeamUltroid/pyUltroid/blob/main/LICENSE>.

import os
import sys
from logging import INFO, StreamHandler, basicConfig, getLogger

# CLI subcommands (setup/doctor) must not boot the full userbot client stack.
_CLI_COMMANDS = {"setup", "doctor", "-h", "--help", "help"}
_is_cli = len(sys.argv) > 1 and sys.argv[1] in _CLI_COMMANDS

from .version import __version__

run_as_module = (not _is_cli) and (
    __package__ in sys.argv
    or sys.argv[0] == "-m"
    or str(sys.argv[0]).endswith("__main__.py")
    or str(sys.argv[0]).endswith(os.path.join("pyUltroid", "__main__.py"))
)


class ULTConfig:
    lang = "en"
    thumb = "resources/extras/ultroid.jpg"


if run_as_module:
    # Validate config BEFORE heavy imports (telethon / telethonpatch / DB drivers)
    # so missing API_ID/SESSION fail fast with clear messages on any host.
    _boot_log = getLogger("pyUltLogs")
    if not _boot_log.handlers:
        basicConfig(
            format="%(asctime)s | %(name)s [%(levelname)s] : %(message)s",
            level=INFO,
            datefmt="%m/%d/%Y, %H:%M:%S",
            handlers=[StreamHandler()],
        )

    from .configs import Var

    # Load validator by path so we don't import startup/__init__.py (Telethon) yet.
    import importlib.util

    _cv_path = os.path.join(os.path.dirname(__file__), "startup", "config_validate.py")
    _cv_spec = importlib.util.spec_from_file_location(
        "pyUltroid_boot_config_validate", _cv_path
    )
    _cv = importlib.util.module_from_spec(_cv_spec)
    _cv_spec.loader.exec_module(_cv)
    _cv.validate_config_or_exit(Var, _boot_log)

    import time

    import telethonpatch  # noqa: F401

    from .startup import *
    from .startup._database import UltroidDB
    from .startup.BaseClient import UltroidClient
    from .startup.connections import validate_session, vc_connection
    from .startup.funcs import _version_changes, autobot, enable_inline, update_envs
    from .version import ultroid_version

    if not os.path.exists("./plugins"):
        LOGS.error(
            "'plugins' folder not found!\nMake sure that, you are on correct path."
        )
        sys.exit(1)

    start_time = time.time()
    _ult_cache = {}
    _ignore_eval = []

    udB = UltroidDB()
    update_envs()

    LOGS.info(f"Connecting to {udB.name}...")
    if udB.ping():
        LOGS.info(f"Connected to {udB.name} Successfully!")

    BOT_MODE = udB.get_key("BOTMODE")
    DUAL_MODE = udB.get_key("DUAL_MODE")

    USER_MODE = udB.get_key("USER_MODE")
    if USER_MODE:
        DUAL_MODE = False

    if BOT_MODE:
        if DUAL_MODE:
            udB.del_key("DUAL_MODE")
            DUAL_MODE = False
        ultroid_bot = None

        if not udB.get_key("BOT_TOKEN"):
            LOGS.critical(
                '"BOT_TOKEN" not Found! Please add it, in order to use "BOTMODE"\n'
                "  → Create a bot via @BotFather and set BOT_TOKEN in config vars."
            )

            sys.exit(1)
    else:
        ultroid_bot = UltroidClient(
            validate_session(Var.SESSION, LOGS),
            udB=udB,
            app_version=ultroid_version,
            device_model="Ultroid",
        )
        skip_autobot = Var.SKIP_AUTOBOT or udB.get_key("SKIP_AUTOBOT")
        if skip_autobot and not (udB.get_key("BOT_TOKEN") or Var.BOT_TOKEN):
            LOGS.critical(
                "SKIP_AUTOBOT is set but BOT_TOKEN is missing.\n"
                "  → Create a bot at @BotFather and set BOT_TOKEN, or unset SKIP_AUTOBOT."
            )
            sys.exit(1)
        if not skip_autobot:
            ultroid_bot.run_in_loop(autobot())

    if USER_MODE:
        asst = ultroid_bot
    else:
        asst = UltroidClient("asst", bot_token=udB.get_key("BOT_TOKEN"), udB=udB)

    if BOT_MODE:
        ultroid_bot = asst
        if udB.get_key("OWNER_ID"):
            try:
                ultroid_bot.me = ultroid_bot.run_in_loop(
                    ultroid_bot.get_entity(udB.get_key("OWNER_ID"))
                )
            except Exception as er:
                LOGS.exception(er)
    elif not asst.me.bot_inline_placeholder and asst._bot:
        ultroid_bot.run_in_loop(enable_inline(ultroid_bot, asst.me.username))

    vcClient = vc_connection(udB, ultroid_bot)

    _version_changes(udB)

    HNDLR = udB.get_key("HNDLR") or "."
    DUAL_HNDLR = udB.get_key("DUAL_HNDLR") or "/"
    SUDO_HNDLR = udB.get_key("SUDO_HNDLR") or HNDLR
else:
    from logging import getLogger

    LOGS = getLogger("pyUltroid")

    ultroid_bot = asst = udB = vcClient = None
