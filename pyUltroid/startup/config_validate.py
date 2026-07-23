# Ultroid - UserBot
# Copyright (C) 2021-2026 TeamUltroid
#
# This file is a part of < https://github.com/TeamUltroid/Ultroid/ >
# PLease read the GNU Affero General Public License in
# <https://github.com/TeamUltroid/pyUltroid/blob/main/LICENSE>.

"""Boot-time config checks with actionable error messages.

Hosted-safe: only hard-fails on truly required auth vars by default.
Set ULTROID_STRICT_CONFIG=1 for stricter checks (recommended for local).
"""

from __future__ import annotations

import os
import re
import sys

# Telegram Android defaults — rejected so users set their own app credentials.
_DEFAULT_API_ID = {6, "6"}
_DEFAULT_API_HASH = {"eb06d4abfb49dc3eeb1aeb98ae0f581e"}

_SESSION_HINT = (
    "Generate one with: bash sessiongen\n"
    "  or: python -m pyUltroid setup"
)
_API_HINT = (
    "Get your own from https://my.telegram.org (API development tools).\n"
    "Do not use shared/public API credentials."
)


def _truthy(val) -> bool:
    if val is None:
        return False
    return str(val).strip().lower() in {"1", "true", "yes", "on", "y"}


def strict_config() -> bool:
    return _truthy(os.getenv("ULTROID_STRICT_CONFIG"))


def auto_pip_enabled() -> bool:
    """Runtime pip install fallback. Default on for back-compat; disable on locked hosts."""
    env = os.getenv("ULTROID_AUTO_PIP")
    if env is None:
        return True
    return _truthy(env)


def _missing(name: str, hint: str) -> str:
    return f"Missing required config: {name}\n  → {hint}"


def _invalid(name: str, detail: str, hint: str | None = None) -> str:
    msg = f"Invalid config: {name} — {detail}"
    if hint:
        msg += f"\n  → {hint}"
    return msg


def validate_redis_uri(uri: str | None) -> list[str]:
    errors = []
    if not uri:
        return errors
    raw = str(uri).strip()
    if raw.lower().startswith(("http://", "https://", "redis://", "rediss://")):
        errors.append(
            _invalid(
                "REDIS_URI",
                "must not include a URL scheme",
                "Use host:port only, e.g. redis-123.example.com:12345 "
                "(password goes in REDIS_PASSWORD).",
            )
        )
        return errors
    if ":" not in raw:
        errors.append(
            _invalid(
                "REDIS_URI",
                "expected host:port",
                "Example: redis-123.example.com:12345",
            )
        )
        return errors
    host, _, port = raw.rpartition(":")
    if not host.strip():
        errors.append(_invalid("REDIS_URI", "host is empty", "Example: 1.2.3.4:6379"))
    if not port.isdigit() or not (1 <= int(port) <= 65535):
        errors.append(
            _invalid("REDIS_URI", f"bad port '{port}'", "Port must be 1–65535")
        )
    return errors


def validate_mongo_uri(uri: str | None) -> list[str]:
    if not uri:
        return []
    if not str(uri).strip().startswith(("mongodb://", "mongodb+srv://")):
        return [
            _invalid(
                "MONGO_URI",
                "should start with mongodb:// or mongodb+srv://",
                "Copy the full URI from your MongoDB provider.",
            )
        ]
    return []


def validate_database_url(url: str | None) -> list[str]:
    if not url:
        return []
    if not re.match(r"^postgres(ql)?://", str(url).strip(), re.I):
        return [
            _invalid(
                "DATABASE_URL",
                "expected a postgres:// or postgresql:// URL",
                "Use the URI from your Postgres provider (e.g. Railway/Heroku/ElephantSQL).",
            )
        ]
    return []


def collect_config_issues(Var) -> tuple[list[str], list[str]]:
    """Return (errors, warnings). Errors should abort boot."""
    errors: list[str] = []
    warnings: list[str] = []

    api_id = getattr(Var, "API_ID", None)
    api_hash = getattr(Var, "API_HASH", None)
    session = getattr(Var, "SESSION", None)

    if api_id in (None, "", 0) or api_hash in (None, ""):
        errors.append(_missing("API_ID / API_HASH", _API_HINT))
    else:
        try:
            api_id_int = int(api_id)
        except (TypeError, ValueError):
            errors.append(_invalid("API_ID", f"not an integer ({api_id!r})", _API_HINT))
            api_id_int = None
        if api_id_int in _DEFAULT_API_ID or str(api_hash).lower() in _DEFAULT_API_HASH:
            errors.append(
                _invalid(
                    "API_ID / API_HASH",
                    "Telegram Android defaults are not allowed",
                    _API_HINT,
                )
            )

    bot_mode = _truthy(os.getenv("BOTMODE"))
    if not session and not bot_mode:
        # BOTMODE can run on BOT_TOKEN alone; normal userbot needs SESSION.
        if not getattr(Var, "BOT_TOKEN", None):
            errors.append(_missing("SESSION", _SESSION_HINT))
        else:
            warnings.append(
                "SESSION is unset. Without BOTMODE this will fail after DB connect. "
                + _SESSION_HINT
            )

    errors.extend(validate_redis_uri(getattr(Var, "REDIS_URI", None)))
    if getattr(Var, "REDISHOST", None) and not getattr(Var, "REDIS_URI", None):
        # Railway-style split vars — port required when host set
        port = getattr(Var, "REDISPORT", None)
        if not port:
            warnings.append(
                "REDISHOST is set but REDISPORT is empty. "
                "Set REDISPORT or use REDIS_URI=host:port."
            )

    errors.extend(validate_mongo_uri(getattr(Var, "MONGO_URI", None)))
    errors.extend(validate_database_url(getattr(Var, "DATABASE_URL", None)))

    has_db = any(
        [
            getattr(Var, "REDIS_URI", None),
            getattr(Var, "REDISHOST", None),
            getattr(Var, "MONGO_URI", None),
            getattr(Var, "DATABASE_URL", None),
        ]
    )
    if not has_db:
        msg = (
            "No remote database configured (REDIS_URI / MONGO_URI / DATABASE_URL). "
            "Falling back to LocalDB (file). Fine for trials; use Redis/Mongo/Postgres in production."
        )
        if strict_config():
            errors.append(msg + "\n  → Strict mode (ULTROID_STRICT_CONFIG=1) requires a remote DB.")
        else:
            warnings.append(msg)

    return errors, warnings


def validate_config_or_exit(Var, logger=None) -> None:
    """Log warnings; exit process if hard errors are present."""
    errors, warnings = collect_config_issues(Var)
    log = logger
    if log is None:
        import logging

        log = logging.getLogger("pyUltLogs")

    for w in warnings:
        log.warning("[config] %s", w)

    if not errors:
        return

    log.error(
        "Configuration check failed (%s issue%s). Fix the following and restart:",
        len(errors),
        "s" if len(errors) != 1 else "",
    )
    for i, err in enumerate(errors, 1):
        lines = err.splitlines() or [err]
        for idx, line in enumerate(lines):
            prefix = f"{i}. " if idx == 0 else "   "
            log.error("  %s%s", prefix, line)

    log.error(
        "Docs: https://ultroid.tech | Sample env: .env.sample | Guided setup: python -m pyUltroid setup"
    )
    sys.exit(1)


def pip_install_hint(packages: str) -> str:
    return (
        f"Missing Python package(s): {packages}\n"
        f"  → Install: {sys.executable} -m pip install {packages}\n"
        f"  → Or use a requirements profile (see requirements-db-*.txt / requirements-full.txt)\n"
        f"  → Temporary auto-install: set ULTROID_AUTO_PIP=1 (not recommended on locked hosts)"
    )
