# Ultroid - UserBot
# Copyright (C) 2021-2025 TeamUltroid
#
# This file is a part of < https://github.com/TeamUltroid/Ultroid/ >
# PLease read the GNU Affero General Public License in
# <https://github.com/TeamUltroid/pyUltroid/blob/main/LICENSE>.

import os
import platform
import sys
from logging import INFO, WARNING, FileHandler, StreamHandler, basicConfig, getLogger

from ._extra import _ask_input
from ..configs import Var



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
TelethonLogger.setLevel(INFO)

_, v, __ = platform.python_version_tuple()

if int(v) < 10:
    from ._extra import _fix_logging

    _fix_logging(FileHandler)

_ask_input()

_LOG_FORMAT = "%(asctime)s | %(name)s [%(levelname)s] : %(message)s"
basicConfig(
        format=_LOG_FORMAT,
        level=INFO,
        datefmt="%m/%d/%Y, %H:%M:%S",
        handlers=[FileHandler(file), StreamHandler()],
    )
try:
    import coloredlogs
    coloredlogs.install(level=None, logger=LOGS, fmt=_LOG_FORMAT)
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

try:
    from safety.tools import *
except ImportError:
    LOGS.error("'safety' package not found!")
