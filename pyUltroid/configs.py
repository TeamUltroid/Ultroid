# Ultroid - UserBot
# Copyright (C) 2021-2026 TeamUltroid
#
# This file is a part of < https://github.com/TeamUltroid/Ultroid/ >
# PLease read the GNU Affero General Public License in
# <https://github.com/TeamUltroid/pyUltroid/blob/main/LICENSE>.

import os
import sys

from decouple import config

try:
    from dotenv import load_dotenv

    load_dotenv()
except ImportError:
    pass

# CLI subcommands must not be parsed as API_ID (multi_client still uses argv slots).
_CLI_COMMANDS = {"setup", "doctor", "-h", "--help", "help"}


def _argv_is_cli():
    return len(sys.argv) > 1 and sys.argv[1] in _CLI_COMMANDS


def _argv_val(index):
    if _argv_is_cli():
        return None
    if len(sys.argv) > index:
        return sys.argv[index]
    return None


def _as_int(value, default=None):
    if value in (None, ""):
        return default
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


class Var:
    # mandatory — no silent Telegram Android defaults (see config_validate)
    API_ID = _as_int(_argv_val(1), default=_as_int(config("API_ID", default=None)))
    API_HASH = _argv_val(2) or config("API_HASH", default=None)
    SESSION = _argv_val(3) or config("SESSION", default=None)
    REDIS_URI = _argv_val(4) or (
        config("REDIS_URI", default=None) or config("REDIS_URL", default=None)
    )
    REDIS_PASSWORD = _argv_val(5) or config("REDIS_PASSWORD", default=None)
    # extras
    BOT_TOKEN = config("BOT_TOKEN", default=None)
    LOG_CHANNEL = _as_int(config("LOG_CHANNEL", default=0), default=0) or 0
    HEROKU_APP_NAME = config("HEROKU_APP_NAME", default=None)
    HEROKU_API = config("HEROKU_API", default=None)
    VC_SESSION = config("VC_SESSION", default=None)
    ADDONS = config("ADDONS", default=False, cast=bool)
    VCBOT = config("VCBOT", default=False, cast=bool)
    # for railway
    REDISPASSWORD = config("REDISPASSWORD", default=None)
    REDISHOST = config("REDISHOST", default=None)
    REDISPORT = config("REDISPORT", default=None)
    REDISUSER = config("REDISUSER", default=None)
    # for sql
    DATABASE_URL = config("DATABASE_URL", default=None)
    # for MONGODB users
    MONGO_URI = config("MONGO_URI", default=None)
    # for local Telegram DB backup
    TGDB_URL = config("TGDB_URL", default=None)
    # QoL / hosted-safe toggles
    # ULTROID_AUTO_PIP: runtime pip fallback (default on for back-compat)
    # ULTROID_STRICT_CONFIG: fail boot without remote DB
    # SKIP_AUTOPILOT / SKIP_AUTOJOIN / SKIP_AUTOBOT: opt out of side effects
    AUTO_PIP = config("ULTROID_AUTO_PIP", default=None)
    STRICT_CONFIG = config("ULTROID_STRICT_CONFIG", default=False, cast=bool)
    SKIP_AUTOPILOT = config("SKIP_AUTOPILOT", default=False, cast=bool)
    SKIP_AUTOJOIN = config("SKIP_AUTOJOIN", default=False, cast=bool)
    SKIP_AUTOBOT = config("SKIP_AUTOBOT", default=False, cast=bool)
    SKIP_ASSISTANT_CUSTOMIZE = config(
        "SKIP_ASSISTANT_CUSTOMIZE", default=False, cast=bool
    )
