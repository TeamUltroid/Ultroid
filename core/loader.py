# Ultroid - UserBot
# Copyright (C) 2020-2023 TeamUltroid
#
# This file is a part of < https://github.com/TeamUltroid/Ultroid/ >
# PLease read the GNU Affero General Public License in
# <https://github.com/TeamUltroid/pyUltroid/blob/main/LICENSE>.

import contextlib
import glob
import os
from importlib import import_module
from typing import Union, List
from . import LOGS
from collections import deque
from utilities.helper import get_all_files

PLUGINS = {}

def __load(func, plugin, key, single):
    if func == import_module:
        plugin = plugin.replace(".py", "").replace("/", ".").replace("\\", ".")
    try:
        modl = func(plugin)
    except ModuleNotFoundError as er:
        LOGS.error(f"{plugin}: '{er.name}' not installed!")
        return
    except Exception as exc:
        LOGS.error(f"pyUltroid - {key} - ERROR - {plugin}")
        LOGS.exception(exc)
        return
    PLUGINS[modl.__name__] = modl
    if single:
        LOGS.info(f"Successfully loaded {modl.__name__}")


def load(
    log=True,
    func=import_module,
    include=None,
    exclude=None,
    plugins=None,
    key="Official",
    path: Union[str, List[str]]="modules",
):
    _single = isinstance(path, str) and os.path.isfile(path)
    if include:
        if log:
            LOGS.info(f'Including: {"• ".join(include)}')
        files = glob.glob(f"{path}/_*.py")
        files.extend(
            list(filter(lambda file: os.path.exists(f"{path}/{file}.py"), include))
        )
    elif _single:
        files = [path]
    elif isinstance(path, list):
        files = []
        for path in path:
            files.extend(get_all_files(path, ".py"))
    else:
        files = get_all_files(path, ".py")
        if exclude:
            for path_ in filter(lambda e: not e.startswith("_"), exclude):
                with contextlib.suppress(ValueError):
                    files.remove(f"{path}/{path_}.py")
    if plugins:
        files.extend(plugins)
    if log and not _single:
        LOGS.info(
            f"• Installing %s Plugins || Count : {len(files)} •",
            key,
        )
    deque(map(lambda e: __load(func, e, key, _single), files), 0)