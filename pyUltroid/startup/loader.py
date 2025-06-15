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
import json
from pathlib import Path
import aiohttp
import base64

from decouple import config
from git import Repo

from .. import *
from ..dB._core import HELP
from ..loader import Loader
from . import *
from .utils import load_addons
from ..configs import CENTRAL_REPO_URL

def _after_load(loader, module, plugin_name=""):
    if not module or plugin_name.startswith("_"):
        return
    from strings import get_help

    # Normalize Addons plugin names by stripping last two hashes
    normalized_name = plugin_name
    if loader.key == "Addons" and plugin_name.count("_") >= 2:
        normalized_name = "_".join(plugin_name.rsplit("_", 2)[:-2])
    else:
        normalized_name = plugin_name

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
                update_cmd.update({normalized_name: doc})
            except BaseException as er:
                loader._logger.exception(er)
        else:
            try:
                HELP.update({loader.key: {normalized_name: doc}})
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
        loop = asyncio.get_event_loop()
        background_tasks.append(loop.create_task(setup_addons()))

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

async def check_for_updates():
    """Check for updates to official plugins using compute_diff endpoint."""
    try:
        from ..state_config import temp_config_store
        stored_states = json.loads(temp_config_store.get("OFFICIAL_PLUGINS_STATE") or "{}")
        
        if not stored_states:
            LOGS.info("No stored plugin states found. Skipping update check.")
            return []

        # Get authentication data
        user_data = temp_config_store.get("X-TG-USER")
        if not user_data:
            LOGS.error("No authentication data found. Please authenticate first.")
            return []

        user_id = str(user_data["id"])
        encoded_init_data = temp_config_store.get(f"X-TG-INIT-DATA-{user_id}")
        encoded_hash = temp_config_store.get(f"X-TG-HASH-{user_id}")

        if not encoded_init_data or not encoded_hash:
            LOGS.error("Missing authentication tokens. Please authenticate first.")
            return []

        # Decode authentication data
        init_data = base64.b64decode(encoded_init_data.encode()).decode()
        hash_value = base64.b64decode(encoded_hash.encode()).decode()
            
        async with aiohttp.ClientSession() as session:
            api_url = f"{CENTRAL_REPO_URL}/api/v1/plugins/compute_diff"
            
            headers = {
                "Content-Type": "application/json",
                "X-Telegram-Init-Data": init_data,
                "X-Telegram-Hash": hash_value
            }
            
            async with session.post(
                api_url,
                json=stored_states,
                headers=headers
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    updates = data.get("updates_available", [])
                    
                    if updates:
                        LOGS.info(f"Found {len(updates)} plugin updates available")
                        return updates
                    else:
                        LOGS.info("All plugins are up to date")
                        return []
                else:
                    LOGS.error(f"Failed to check for updates. Status: {response.status}")
                    return []
    except Exception as e:
        LOGS.error(f"Error checking for plugin updates: {str(e)}")
        return []

async def setup_addons():
    """Setup and load addons/plugins."""
    if url := udB.get_key("ADDONS_URL"):
        subprocess.run(f"git clone -q {url} addons", shell=True)

    if not os.path.exists("addons/__init__.py"):
        with open("addons/__init__.py", "w") as f:
            f.write("from plugins import *")

    if udB.get_key("INCLUDE_ALL"):
        # Query official plugins and sync them
        try:
            # Get authentication data
            from ..state_config import temp_config_store
            user_data = temp_config_store.get("X-TG-USER")
            if not user_data:
                LOGS.error("No authentication data found. Please authenticate first.")
                return

            user_id = str(user_data["id"])
            encoded_init_data = temp_config_store.get(f"X-TG-INIT-DATA-{user_id}")
            encoded_hash = temp_config_store.get(f"X-TG-HASH-{user_id}")

            if not encoded_init_data or not encoded_hash:
                LOGS.error("Missing authentication tokens. Please authenticate first.")
                return

            # Decode authentication data
            init_data = base64.b64decode(encoded_init_data.encode()).decode()
            hash_value = base64.b64decode(encoded_hash.encode()).decode()

            async with aiohttp.ClientSession() as session:
                headers = {
                    "Content-Type": "application/json",
                    "X-Telegram-Init-Data": init_data,
                    "X-Telegram-Hash": hash_value
                }

                # Get all official plugins with offset-based pagination
                api_url = f"{CENTRAL_REPO_URL}/api/v1/plugins/official"
                limit = 100
                offset = 0
                all_plugins = []
                while True:
                    params = {
                        "limit": limit,
                        "offset": offset,
                        "sort_by": "updated_at",
                        "sort_order": "desc"
                    }
                    async with session.get(api_url, params=params, headers=headers) as response:
                        if response.status == 200:
                            data = await response.json()
                            plugins = data.get("plugins", [])
                            all_plugins.extend(plugins)
                            pagination = data.get("pagination", {})
                            if not pagination.get("has_next_page"):
                                break
                            offset += limit
                        else:
                            error_text = await response.text()
                            LOGS.error(f"Failed to fetch official plugins. Status: {response.status}, Error: {error_text}")
                            break

                if not all_plugins:
                    LOGS.warning("No official plugins found")
                    return

                # Create addons directory if it doesn't exist
                addons_dir = Path(__file__).parent.parent.parent / "addons"
                addons_dir.mkdir(exist_ok=True)

                # Track plugin states for compute_diff
                plugin_states = {}

                # Async function to download a single plugin
                async def download_plugin(plugin):
                    try:
                        plugin_id = str(plugin["id"])
                        plugin_title = plugin["title"]
                        download_url = plugin["download_link"]
                        updated_at = plugin["updated_at"]
                        file_path = plugin.get("file_path")

                        if not file_path:
                            LOGS.warning(f"Missing file_path for plugin {plugin_title}, skipping")
                            return None

                        # Generate safe filename from file_path
                        safe_filename = os.path.basename(file_path)
                        if not safe_filename.endswith('.py'):
                            safe_filename += '.py'

                        target_path = addons_dir / safe_filename

                        # Download the plugin
                        async with session.get(download_url) as plugin_response:
                            if plugin_response.status == 200:
                                plugin_content = await plugin_response.text()
                                # Write file with explicit UTF-8 encoding
                                target_path.write_text(plugin_content, encoding='utf-8')
                                # No per-plugin success log
                                return (plugin_id, updated_at)
                            else:
                                LOGS.error(f"Failed to download plugin {plugin_title}. Status: {plugin_response.status}")
                                return None
                    except Exception as e:
                        LOGS.error(f"Error processing plugin {plugin.get('title', 'unknown')}: {str(e)}")
                        return None

                # Download plugins in batches using asyncio.gather
                batch_size = 10
                plugin_results = []
                for i in range(0, len(all_plugins), batch_size):
                    batch = all_plugins[i:i+batch_size]
                    results = await asyncio.gather(*(download_plugin(plugin) for plugin in batch))
                    plugin_results.extend(results)

                # Store plugin states in temp config
                for result in plugin_results:
                    if result:
                        plugin_id, updated_at = result
                        plugin_states[plugin_id] = updated_at

                if plugin_states:
                    LOGS.info(f"Successfully downloaded {len(plugin_states)} official plugins")
                    temp_config_store.set("OFFICIAL_PLUGINS_STATE", json.dumps(plugin_states))
                    LOGS.info(f"Successfully synced {len(plugin_states)} official plugins")
                else:
                    LOGS.warning("No plugins were successfully processed")
        except Exception as e:
            LOGS.error(f"Error syncing official plugins: {str(e)}")

        # Fallback to UltroidAddons if official plugins sync fails
        if not os.path.exists("addons"):
            try:
                repo = Repo()
                branch = repo.active_branch.name
                subprocess.run(
                    f"git clone -q -b {branch} https://github.com/TeamUltroid/UltroidAddons.git addons",
                    shell=True,
                    check=True
                )
            except Exception as e:
                LOGS.error(f"Failed to clone UltroidAddons: {str(e)}")
                # Try master branch as fallback
                subprocess.run(
                    "git clone -q https://github.com/TeamUltroid/UltroidAddons.git addons",
                    shell=True
                )
        else:
            subprocess.run("cd addons && git pull -q && cd ..", shell=True)

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
