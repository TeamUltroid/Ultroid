# Ultroid - UserBot
# Copyright (C) 2021-2025 TeamUltroid
#
# This file is a part of < https://github.com/TeamUltroid/Ultroid/ >
# PLease read the GNU Affero General Public License in
# <https://github.com/TeamUltroid/pyUltroid/blob/main/LICENSE>.

from . import *
from logging import getLogger
from pyUltroid.web.server import ultroid_server

logger = getLogger(__name__)


def main():
    import os
    import sys
    import time

    from .fns.helper import bash, time_formatter, updater
    from .startup.funcs import (
        WasItRestart,
        autopilot,
        customize,
        plug,
        ready,
        startup_stuff,
        user_sync_workflow
    )
    from .startup.loader import load_other_plugins

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

    ultroid_bot.run_in_loop(user_sync_workflow())
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

    # Edit Restarting Message (if It's restarting)
    ultroid_bot.run_in_loop(WasItRestart(udB))

    if Var.START_WEB:
        logger.info("Starting web server as a background task...")
        asst.loop.create_task(ultroid_server.start())

    try:
        cleanup_cache()
    except BaseException:
        pass

    LOGS.info(
        f"Took {time_formatter((time.time() - start_time)*1000)} to start •ULTROID•"
    )
    LOGS.info(suc_msg)


def run_indefinitely(max_wait: int = 3600 * 3): # 3 hours
    """Run the assistant indefinitely with connection error handling and timeout.
    
    Args:
        max_wait: Maximum time in seconds to keep retrying on connection errors.
                 Defaults to 3 hours.
    """
    start_time = 0
    retry_count = 0
    backoff = 10  # Initial backoff time in seconds
    
    while True:
        # Check if max wait time exceeded
        if start_time and (time.time() - start_time) > max_wait:
            logger.error(f"Max wait time of {max_wait} seconds reached, exiting")
            exit(1)

        try:
            # Attempt to run the assistant
            asst.run()
        except ConnectionError as er:
            # Track first connection error
            if not start_time:
                start_time = time.time()
                
            retry_count += 1
            wait_time = min(backoff * retry_count, 300)  # Cap at 5 minutes
            
            logger.error(
                f"ConnectionError: {er}, attempt {retry_count}, "
                f"waiting {wait_time} seconds"
            )
            time.sleep(wait_time)
            continue

        except Exception as er:
            logger.exception(f"Fatal error occurred: {er}")
            exit(1)

if __name__ == "__main__":
    main()

    run_indefinitely()