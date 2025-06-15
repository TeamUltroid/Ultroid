# Ultroid - UserBot
# Copyright (C) 2021-2025 TeamUltroid
#
# This file is a part of < https://github.com/TeamUltroid/Ultroid/ >
# PLease read the GNU Affero General Public License in
# <https://github.com/TeamUltroid/pyUltroid/blob/main/LICENSE>.

import contextlib
import glob
import os
from importlib import import_module
from logging import Logger

from . import LOGS
from .fns.tools import get_all_files


class Loader:
    def __init__(self, path="plugins", key="Official", logger: Logger = LOGS):
        self.path = path
        self.key = key
        self._logger = logger

    def load(
        self,
        log=True,
        func=import_module,
        include=None,
        exclude=None,
        after_load=None,
        load_all=False,
    ):
        _single = os.path.isfile(self.path)
        if include:
            if log:
                self._logger.info("Including: {}".format("• ".join(include)))
            files = glob.glob(f"{self.path}/_*.py")
            for file in include:
                path = f"{self.path}/{file}.py"
                if os.path.exists(path):
                    files.append(path)
        elif _single:
            files = [self.path]
        else:
            if load_all:
                files = get_all_files(self.path, ".py")
            else:
                files = glob.glob(f"{self.path}/*.py")
            if exclude:
                for path in exclude:
                    if not path.startswith("_"):
                        with contextlib.suppress(ValueError):
                            files.remove(f"{self.path}/{path}.py")
        if log and not _single:
            self._logger.info(
                f"• Installing {self.key} Plugins || Count : {len(files)} •"
            )
        for plugin in sorted(files):
            if func == import_module:
                plugin = plugin.replace(".py", "").replace("/", ".").replace("\\", ".")
            try:
                modl = func(plugin)
            except ModuleNotFoundError as er:
                modl = None
                self._logger.error(f"{plugin}: '{er.name}' not installed!")
                continue
            except Exception as exc:
                modl = None
                self._logger.error(f"pyUltroid - {self.key} - ERROR - {plugin}")
                self._logger.exception(exc)
                continue
            if _single and log:
                self._logger.info(f"Successfully Loaded {plugin}!")
            if callable(after_load):
                if func == import_module:
                    plugin = plugin.split(".")[-1]
                after_load(self, modl, plugin_name=plugin)

    def load_single_plugin(self, plugin_path, func=import_module, after_load=None):
        """Load a single plugin file"""
        try:
            if not os.path.exists(plugin_path):
                self._logger.error(f"Plugin file not found: {plugin_path}")
                return False

            plugin_name = os.path.basename(plugin_path).replace(".py", "")

            if func == import_module:
                # Convert file path to module path
                plugin_module = str(plugin_path).replace(".py", "").replace("/", ".").replace("\\", ".")
                modl = func(plugin_module)
            else:
                modl = func(plugin_path)

            self._logger.info(f"Successfully loaded plugin: {plugin_name}")

            if callable(after_load):
                after_load(self, modl, plugin_name=plugin_name)

            return True

        except ModuleNotFoundError as er:
            self._logger.error(f"{plugin_path}: '{er.name}' not installed!")
            return False
        except Exception as exc:
            self._logger.error(f"pyUltroid - {self.key} - ERROR - {plugin_path}")
            self._logger.exception(exc)
            return False
