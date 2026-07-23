# Ultroid - UserBot
# Copyright (C) 2021-2026 TeamUltroid
#
# This file is a part of < https://github.com/TeamUltroid/Ultroid/ >
# PLease read the GNU Affero General Public License in
# <https://github.com/TeamUltroid/pyUltroid/blob/main/LICENSE>.

import sys

_CLI = {"setup", "doctor", "-h", "--help", "help"}


def _run_cli():
    from .startup.setup_cli import main as setup_main

    raise SystemExit(setup_main(sys.argv[1:]))


def main():
    import os
    import time

    # Full boot only when not a CLI command (import * must stay at function scope
    # carefully — pull symbols explicitly after package init).
    import pyUltroid as _pkg
    from pyUltroid import (
        HOSTED_ON,
        LOGS,
        Var,
        asst,
        start_time,
        udB,
        ultroid_bot,
    )
    from pyUltroid.fns.helper import bash, time_formatter, updater
    from pyUltroid.startup.funcs import (
        WasItRestart,
        autopilot,
        customize,
        keep_redis_alive,
        plug,
        ready,
        startup_stuff,
    )
    from pyUltroid.startup.loader import load_other_plugins

    try:
        from apscheduler.schedulers.asyncio import AsyncIOScheduler
    except ImportError:
        AsyncIOScheduler = None

    # Option to Auto Update On Restarts..
    if (
        udB.get_key("UPDATE_ON_RESTART")
        and os.path.exists(".git")
        and ultroid_bot.run_in_loop(updater())
    ):
        ultroid_bot.run_in_loop(bash("bash installer.sh"))

        os.execl(sys.executable, sys.executable, "-m", "pyUltroid")

    ultroid_bot.run_in_loop(startup_stuff())

    ultroid_bot.me.phone = None

    if not ultroid_bot.me.bot:
        udB.set_key("OWNER_ID", ultroid_bot.uid)

    LOGS.info("Initialising...")

    skip_autopilot = Var.SKIP_AUTOPILOT or udB.get_key("SKIP_AUTOPILOT")
    if skip_autopilot:
        if not (udB.get_key("LOG_CHANNEL") or Var.LOG_CHANNEL):
            LOGS.critical(
                "SKIP_AUTOPILOT is set but LOG_CHANNEL is missing.\n"
                "  → Create a private group, add your assistant, set LOG_CHANNEL to its id."
            )
            sys.exit(1)
        LOGS.info("SKIP_AUTOPILOT set — not auto-creating log channel.")
    else:
        ultroid_bot.run_in_loop(autopilot())

    ultroid_bot.loop.create_task(keep_redis_alive())

    pmbot = udB.get_key("PMBOT")
    manager = udB.get_key("MANAGER")
    addons = udB.get_key("ADDONS") or Var.ADDONS
    vcbot = udB.get_key("VCBOT") or Var.VCBOT
    if HOSTED_ON == "okteto":
        vcbot = False

    if (HOSTED_ON == "termux" or udB.get_key("LITE_DEPLOY")) and udB.get_key(
        "EXCLUDE_OFFICIAL"
    ) is None:
        _plugins = "autocorrect autopic audiotools compressor forcesubscribe fedutils gdrive glitch instagram nsfwfilter nightmode pdftools profanityfilter writer youtube"
        udB.set_key("EXCLUDE_OFFICIAL", _plugins)

    load_other_plugins(addons=addons, pmbot=pmbot, manager=manager, vcbot=vcbot)

    suc_msg = """
            ----------------------------------------------------------------------
                Ultroid has been deployed! Visit @TheUltroid for updates!!
            ----------------------------------------------------------------------
    """

    # for channel plugins
    plugin_channels = udB.get_key("PLUGIN_CHANNEL")

    # Customize Ultroid Assistant...
    skip_customize = Var.SKIP_ASSISTANT_CUSTOMIZE or udB.get_key(
        "SKIP_ASSISTANT_CUSTOMIZE"
    )
    if skip_customize:
        LOGS.info("SKIP_ASSISTANT_CUSTOMIZE set — skipping BotFather customisation.")
    else:
        ultroid_bot.run_in_loop(customize())

    # Load Addons from Plugin Channels.
    if plugin_channels:
        ultroid_bot.run_in_loop(plug(plugin_channels))

    # Send/Ignore Deploy Message..
    if not udB.get_key("LOG_OFF"):
        ultroid_bot.run_in_loop(ready())

    # Edit Restarting Message (if It's restarting)
    ultroid_bot.run_in_loop(WasItRestart(udB))

    try:
        udB.re_cache()
    except Exception:
        pass

    # Container / orchestrator friendly ready marker (K8s/Railway probes can check this).
    try:
        from pyUltroid.loader import LOAD_REPORT

        ready_path = os.getenv("ULTROID_READY_FILE", "ultroid.ready")
        with open(ready_path, "w", encoding="utf-8") as rf:
            rf.write(
                "ok\n"
                f"version={os.getenv('ULTROID_VERSION', '')}\n"
                f"host={HOSTED_ON}\n"
                f"plugins_loaded={len(LOAD_REPORT.get('loaded') or [])}\n"
                f"plugins_failed={len(LOAD_REPORT.get('failed') or [])}\n"
            )
        LOGS.info("Ready file written: %s", ready_path)
    except Exception as er:
        LOGS.debug("Could not write ready file: %s", er)

    LOGS.info(
        f"Took {time_formatter((time.time() - start_time)*1000)} to start •ULTROID•"
    )
    LOGS.info(suc_msg)
    return asst


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] in _CLI:
        _run_cli()
    else:
        _asst = main()
        _asst.run()
