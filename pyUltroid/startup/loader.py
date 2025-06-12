# Ultroid - UserBot
# Copyright (C) 2021-2025 TeamUltroid
#
# This file is a part of < https://github.com/TeamUltroid/Ultroid/ >
# PLease read the GNU Affero General Public License in
# <https://github.com/TeamUltroid/pyUltroid/blob/main/LICENSE>.

import os
import subprocess
import sys
from shutil import rmtree

from decouple import config
from git import Repo

from .. import *
from ..dB._core import HELP
from ..loader import Loader
from . import *
from .utils import load_addons


def _after_load(loader, module, plugin_name=""):
    if not module or plugin_name.startswith("_"):
        return
    from strings import get_help

    if doc_ := get_help(plugin_name) or module.__doc__:
        try:
            doc = doc_.format(i=HNDLR)
        except Exception as er:
            loader._logger.exception(er)
            loader._logger.info(f"Error in {plugin_name}: {module}")
            return
        if loader.key in HELP.keys():
            update_cmd = HELP[loader.key]
            try:
                update_cmd.update({plugin_name: doc})
            except BaseException as er:
                loader._logger.exception(er)
        else:
            try:
                HELP.update({loader.key: {plugin_name: doc}})
            except BaseException as em:
                loader._logger.exception(em)


def load_other_plugins(addons=None, pmbot=None, manager=None, vcbot=None):
    import asyncio

    # for official
    _exclude = udB.get_key("EXCLUDE_OFFICIAL") or config("EXCLUDE_OFFICIAL", None)
    _exclude = _exclude.split() if _exclude else []

    # "INCLUDE_ONLY" was added to reduce Big List in "EXCLUDE_OFFICIAL" Plugin
    _in_only = udB.get_key("INCLUDE_ONLY") or config("INCLUDE_ONLY", None)
    _in_only = _in_only.split() if _in_only else []

    # Load official plugins first - these are critical for core functionality
    Loader().load(include=_in_only, exclude=_exclude, after_load=_after_load)

    # List to collect all background tasks
    background_tasks = []

    # for assistant - load in background
    if not USER_MODE and not udB.get_key("DISABLE_AST_PLUGINS"):
        _ast_exc = ["pmbot"]
        if _in_only and "games" not in _in_only:
            _ast_exc.append("games")

        # Create an async function that can be used with create_task
        async def load_assistant():
            Loader(path="assistant").load(
                log=False, exclude=_ast_exc, after_load=_after_load
            )

        # Add to background tasks
        loop = asyncio.get_event_loop()
        background_tasks.append(loop.create_task(load_assistant()))

    # for addons - prepare in background but don't block startup
    if addons:
        # Create async function for addons loading
        async def setup_addons():
            if url := udB.get_key("ADDONS_URL"):
                subprocess.run(f"git clone -q {url} addons", shell=True)
            if os.path.exists("addons") and not os.path.exists("addons/.git"):
                rmtree("addons")
            if not os.path.exists("addons"):
                subprocess.run(
                    f"git clone -q -b {Repo().active_branch} https://github.com/TeamUltroid/UltroidAddons.git addons",
                    shell=True,
                )
            else:
                subprocess.run("cd addons && git pull -q && cd ..", shell=True)

            if not os.path.exists("addons"):
                subprocess.run(
                    "git clone -q https://github.com/TeamUltroid/UltroidAddons.git addons",
                    shell=True,
                )
            if os.path.exists("addons/addons.txt"):
                subprocess.run(
                    f"{sys.executable} -m pip install --no-cache-dir -q -r ./addons/addons.txt",
                    shell=True,
                )

            _exclude = udB.get_key("EXCLUDE_ADDONS")
            _exclude = _exclude.split() if _exclude else []
            _in_only = udB.get_key("INCLUDE_ADDONS")
            _in_only = _in_only.split() if _in_only else []

            Loader(path="addons", key="Addons").load(
                func=load_addons,
                include=_in_only,
                exclude=_exclude,
                after_load=_after_load,
                load_all=True,
            )

        # Add to background tasks
        background_tasks.append(asyncio.create_task(setup_addons()))

    if not USER_MODE:
        # Load these in background as they're not critical
        async def load_extra_modules():
            # group manager
            if manager:
                Loader(path="assistant/manager", key="Group Manager").load()

            # chat via assistant
            if pmbot:
                Loader(path="assistant/pmbot.py").load(log=False)

        # Add to background tasks
        loop = asyncio.get_event_loop()
        background_tasks.append(loop.create_task(load_extra_modules()))

    # vc bot - load in background
    if vcbot and (vcClient and not vcClient.me.bot):

        async def setup_vcbot():
            try:
                import pytgcalls  # ignore: pylint

                if os.path.exists("vcbot"):
                    if os.path.exists("vcbot/.git"):
                        subprocess.run("cd vcbot && git pull", shell=True)
                    else:
                        rmtree("vcbot")
                if not os.path.exists("vcbot"):
                    subprocess.run(
                        "git clone https://github.com/TeamUltroid/VcBot vcbot",
                        shell=True,
                    )
                try:
                    if not os.path.exists("vcbot/downloads"):
                        os.mkdir("vcbot/downloads")
                    Loader(path="vcbot", key="VCBot").load(after_load=_after_load)
                except FileNotFoundError as e:
                    LOGS.error(f"{e} Skipping VCBot Installation.")
            except ModuleNotFoundError:
                LOGS.error("'pytgcalls' not installed!\nSkipping loading of VCBOT.")

        # Add to background tasks
        background_tasks.append(asyncio.create_task(setup_vcbot()))

    # Return the list of background tasks in case the caller wants to await them
    return background_tasks
