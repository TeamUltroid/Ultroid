# Ultroid - UserBot
# Copyright (C) 2021-2026 TeamUltroid
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

# Accumulated across all Loader instances for the process lifetime (reset each boot).
LOAD_REPORT = {
    "loaded": [],  # list of (group, name)
    "failed": [],  # list of (group, name, reason)
    "skipped_missing_dep": [],  # list of (group, name, dep)
}


def reset_load_report():
    LOAD_REPORT["loaded"].clear()
    LOAD_REPORT["failed"].clear()
    LOAD_REPORT["skipped_missing_dep"].clear()


def summarize_load_report(logger=None):
    log = logger or LOGS
    loaded = LOAD_REPORT["loaded"]
    failed = LOAD_REPORT["failed"]
    missing = LOAD_REPORT["skipped_missing_dep"]
    lines = [
        "Plugin load report: {} loaded, {} missing-dep, {} failed".format(
            len(loaded), len(missing), len(failed)
        )
    ]
    if missing:
        lines.append("Missing dependencies:")
        for group, name, dep in missing[:20]:
            lines.append("  • [{}] {} → package '{}'".format(group, name, dep))
        if len(missing) > 20:
            lines.append("  … and {} more".format(len(missing) - 20))
    if failed:
        lines.append("Failed:")
        for group, name, reason in failed[:20]:
            short = reason.splitlines()[0][:120]
            lines.append("  • [{}] {}: {}".format(group, name, short))
        if len(failed) > 20:
            lines.append("  … and {} more".format(len(failed) - 20))
    text = "\n".join(lines)
    if log:
        for line in lines:
            log.info(line)
    return text


class Loader:
    def __init__(self, path="plugins", key="Official", logger: Logger = LOGS):
        self.path = path
        self.key = key
        self._logger = logger
        self.loaded = []
        self.failed = []
        self.missing_deps = []

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
            plugin_path = plugin
            if func == import_module:
                plugin = plugin.replace(".py", "").replace("/", ".").replace("\\", ".")
            display = (
                plugin.split(".")[-1]
                if func == import_module
                else os.path.splitext(os.path.basename(str(plugin_path)))[0]
            )
            try:
                modl = func(plugin)
            except ModuleNotFoundError as er:
                modl = None
                dep = getattr(er, "name", None) or str(er)
                self._logger.error(f"{plugin}: '{dep}' not installed!")
                self.missing_deps.append((display, dep))
                LOAD_REPORT["skipped_missing_dep"].append((self.key, display, dep))
                continue
            except Exception as exc:
                modl = None
                self._logger.error(f"pyUltroid - {self.key} - ERROR - {plugin}")
                self._logger.exception(exc)
                reason = f"{type(exc).__name__}: {exc}"
                self.failed.append((display, reason))
                LOAD_REPORT["failed"].append((self.key, display, reason))
                continue
            if _single and log:
                self._logger.info(f"Successfully Loaded {plugin}!")
            self.loaded.append(display)
            LOAD_REPORT["loaded"].append((self.key, display))
            if callable(after_load):
                if func == import_module:
                    plugin = plugin.split(".")[-1]
                after_load(self, modl, plugin_name=plugin)
        return {
            "key": self.key,
            "loaded": list(self.loaded),
            "failed": list(self.failed),
            "missing_deps": list(self.missing_deps),
        }
