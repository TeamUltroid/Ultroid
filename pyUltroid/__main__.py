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
    import asyncio

    from .fns.helper import bash, time_formatter, updater
    from .startup.funcs import (
        WasItRestart,
        autopilot,
        customize,
        plug,
        ready,
        startup_stuff,
        user_sync_workflow,
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

    # Execute critical startup functions immediately
    ultroid_bot.run_in_loop(user_sync_workflow())

    # Load plugins first to ensure core functionality is available
    # Store background tasks for later handling
    background_tasks = load_other_plugins(
        addons=udB.get_key("ADDONS") or Var.ADDONS,
        pmbot=udB.get_key("PMBOT"),
        manager=udB.get_key("MANAGER"),
        vcbot=udB.get_key("VCBOT") or Var.VCBOT,
    )

    suc_msg = """
            ----------------------------------------------------------------------
                Ultroid has been deployed! Visit @TheUltroid for updates!!
            ----------------------------------------------------------------------
    """

    # Schedule non-critical tasks as background tasks to improve startup time
    plugin_channels = udB.get_key("PLUGIN_CHANNEL")

    # These operations are moved to background tasks to reduce startup time
    asst.loop.create_task(autopilot())
    if not USER_MODE and not udB.get_key("DISABLE_AST_PLUGINS"):
        asst.loop.create_task(customize())
    if plugin_channels:
        asst.loop.create_task(plug(plugin_channels))
    if not udB.get_key("LOG_OFF"):
        asst.loop.create_task(ready())
    asst.loop.create_task(WasItRestart(udB))

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


def run_indefinitely(max_wait: int = 3600 * 3):  # 3 hours
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
