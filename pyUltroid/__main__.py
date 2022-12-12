# Ultroid - UserBot
# Copyright (C) 2021-2022 TeamUltroid
#
# This file is a part of < https://github.com/TeamUltroid/Ultroid/ >
# PLease read the GNU Affero General Public License in
# <https://github.com/TeamUltroid/pyUltroid/blob/main/LICENSE>.

from . import *


def main():
    import os
    import sys
    import time

    from .fns.helper import time_formatter, updater, bash
    from .startup.funcs import (
        WasItRestart,
        autopilot,
        customize,
        plug,
        ready,
        fetch_ann,
        startup_stuff,
    )
    from .startup.loader import load_other_plugins
    try:
        from apscheduler.schedulers.asyncio import AsyncIOScheduler
    except ImportError:
        AsyncIOScheduler = None
    # Do not save session while bot is running. (Fixes session generator)
    # [delattr(sess, "save") for sess in [asst.session, ultroid_bot.session] if hasattr(sess, "save")]

    # Option to Auto Update On Restarts..
    if (
        udB.get_key("UPDATE_ON_RESTART")
        and os.path.exists(".git")
        and ultroid_bot.run_in_loop(updater())
    ):
        ultroid_bot.run_in_loop(bash("bash installer.sh"))

        os.execl(sys.executable, "python3", "-m", "pyUltroid")

    ultroid_bot.run_in_loop(startup_stuff())

    ultroid_bot.me.phone = None

    if not ultroid_bot.me.bot:
        udB.set_key("OWNER_ID", ultroid_bot.uid)

    LOGS.info("Initialising...")

    ultroid_bot.run_in_loop(autopilot())

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
    ultroid_bot.run_in_loop(customize())

    # Load Addons from Plugin Channels.
    if plugin_channels:
        ultroid_bot.run_in_loop(plug(plugin_channels))

    # Send/Ignore Deploy Message..
    if not udB.get_key("LOG_OFF"):
        ultroid_bot.run_in_loop(ready())
    if AsyncIOScheduler:
        scheduler = AsyncIOScheduler()
        scheduler.add_job(fetch_ann, "interval", minutes=12*60)
        scheduler.start()

    # Edit Restarting Message (if It's restarting)
    ultroid_bot.run_in_loop(WasItRestart(udB))

    try:
        cleanup_cache()
    except BaseException:
        pass

    LOGS.info(
        f"Took {time_formatter((time.time() - start_time)*1000)} to start •ULTROID•"
    )
    LOGS.info(suc_msg)


if __name__ == "__main__":
    main()

    asst.run()
