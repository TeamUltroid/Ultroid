# Ultroid - UserBot
# Copyright (C) 2021-2026 TeamUltroid
#
# This file is a part of < https://github.com/TeamUltroid/Ultroid/ >
# PLease read the GNU Affero General Public License in
# <https://github.com/TeamUltroid/pyUltroid/blob/main/LICENSE>.

import logging
import os
import platform
import re
import sys
from logging import (
    DEBUG,
    ERROR,
    INFO,
    WARNING,
    FileHandler,
    Filter,
    Formatter,
    StreamHandler,
    basicConfig,
    getLogger,
)

from .. import run_as_module
from ._extra import _ask_input

if run_as_module:
    from ..configs import Var
else:
    Var = None

_SECRET_RE = re.compile(
    r"(?i)(api_hash|api_id|session|bot_token|password|token|secret|authorization)"
    r"([\"']?\s*[:=]\s*[\"']?)([^\s,\"']{6,})"
)


class _RedactFilter(Filter):
    """Strip common secret patterns from log records."""

    def filter(self, record: logging.LogRecord) -> bool:
        try:
            msg = record.getMessage()
        except Exception:
            return True
        redacted = _SECRET_RE.sub(r"\1\2***", msg)
        if redacted != msg:
            record.msg = redacted
            record.args = ()
        return True


def _resolve_log_level():
    name = (os.getenv("LOG_LEVEL") or os.getenv("ULTROID_LOG_LEVEL") or "INFO").upper()
    return {
        "DEBUG": DEBUG,
        "INFO": INFO,
        "WARNING": WARNING,
        "WARN": WARNING,
        "ERROR": ERROR,
        "CRITICAL": logging.CRITICAL,
    }.get(name, INFO)


def where_hosted():
    if os.getenv("DYNO"):
        return "heroku"
    if os.getenv("RAILWAY_STATIC_URL"):
        return "railway"
    if os.getenv("OKTETO_TOKEN"):
        return "okteto"
    if os.getenv("KUBERNETES_PORT"):
        return "qovery | kubernetes"
    if os.getenv("RUNNER_USER") or os.getenv("HOSTNAME"):
        if os.getenv("USER") == "codespace":
            return "codespace"
        return "github actions"
    if os.getenv("ANDROID_ROOT"):
        return "termux"
    if os.getenv("FLY_APP_NAME"):
        return "fly.io"
    return "local"


if run_as_module:
    from telethon import __version__
    from telethon.tl.alltlobjects import LAYER

    from ..version import __version__ as __pyUltroid__
    from ..version import ultroid_version

    file = f"ultroid{sys.argv[6]}.log" if len(sys.argv) > 6 else "ultroid.log"

    if os.path.exists(file):
        os.remove(file)

    HOSTED_ON = where_hosted()
    LOGS = getLogger("pyUltLogs")
    TelethonLogger = getLogger("Telethon")
    _level = _resolve_log_level()
    TelethonLogger.setLevel(
        DEBUG if _level <= DEBUG else INFO if _level <= INFO else WARNING
    )

    _, v, __ = platform.python_version_tuple()

    if int(v) < 10:
        from ._extra import _fix_logging

        _fix_logging(FileHandler)

    _ask_input()

    _LOG_FORMAT = "%(asctime)s | %(name)s [%(levelname)s] : %(message)s"
    _redact = _RedactFilter()
    _fh = FileHandler(file)
    _sh = StreamHandler()
    for _h in (_fh, _sh):
        _h.addFilter(_redact)
    try:
        basicConfig(
            format=_LOG_FORMAT,
            level=_level,
            datefmt="%m/%d/%Y, %H:%M:%S",
            handlers=[_fh, _sh],
            force=True,
        )
    except TypeError:
        # Python < 3.8 has no force=
        basicConfig(
            format=_LOG_FORMAT,
            level=_level,
            datefmt="%m/%d/%Y, %H:%M:%S",
            handlers=[_fh, _sh],
        )
    LOGS.setLevel(_level)
    try:

        import coloredlogs

        coloredlogs.install(level=_level, logger=LOGS, fmt=_LOG_FORMAT)
    except ImportError:
        pass

    LOGS.info(
        """
                    -----------------------------------
                            Starting Deployment
                    -----------------------------------
    """
    )

    LOGS.info(f"Python version - {platform.python_version()}")
    LOGS.info(f"py-Ultroid Version - {__pyUltroid__}")
    LOGS.info(f"Telethon Version - {__version__} [Layer: {LAYER}]")
    LOGS.info(f"Ultroid Version - {ultroid_version} [{HOSTED_ON}]")
    LOGS.info(f"Log level - {logging.getLevelName(_level)}")

    try:
        from safety.tools import *
    except ImportError:
        LOGS.error("'safety' package not found!")
