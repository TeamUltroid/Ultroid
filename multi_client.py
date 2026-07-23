# Ultroid - UserBot
# Copyright (C) 2021-2026 TeamUltroid
#
# Launch multiple userbot clients from environment variables:
#
#   API_ID / API_HASH / SESSION       → primary client (log: ultroid1.log)
#   API_ID1 / API_HASH1 / SESSION1    → second client  (log: ultroid2.log)
#   … up to SESSION5                  → sixth client   (log: ultroid6.log)
#
# Shared Redis (optional, passed to every process):
#   REDIS_URI=host:port
#   REDIS_PASSWORD=...
#
# ./startup runs this automatically when SESSION1 is set; otherwise it
# starts a single `python -m pyUltroid` process.

import asyncio
import os
import subprocess
import sys

_AUTH = ("API_ID", "API_HASH", "SESSION")


def _client_env(suffix: str):
    """Return [api_id, api_hash, session] or None if incomplete."""
    values = []
    for key in _AUTH:
        val = os.environ.get(f"{key}{suffix}")
        if not val:
            return None
        values.append(val)
    return values


def _redis_pair():
    uri = os.environ.get("REDIS_URI") or os.environ.get("REDIS_URL") or ""
    password = (
        os.environ.get("REDIS_PASSWORD") or os.environ.get("REDISPASSWORD") or ""
    )
    return uri, password


def main():
    redis_uri, redis_password = _redis_pair()
    launched = 0

    # suffix "" → primary, "1".."5" → extra clients
    for index, suffix in enumerate([""] + [str(i) for i in range(1, 6)]):
        creds = _client_env(suffix)
        if not creds:
            continue
        log_id = str(index + 1)
        cmd = [
            sys.executable,
            "-m",
            "pyUltroid",
            creds[0],
            creds[1],
            creds[2],
            redis_uri,
            redis_password,
            log_id,
        ]
        label = "SESSION" if suffix == "" else f"SESSION{suffix}"
        print(f"Starting client {log_id} from {label}…")
        subprocess.Popen(cmd)
        launched += 1

    if not launched:
        print(
            "No complete client credentials found.\n"
            "Need API_ID, API_HASH, SESSION (and optionally SESSION1..5)."
        )
        sys.exit(1)

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        loop.run_forever()
    except KeyboardInterrupt:
        pass
    except Exception as er:
        print(er)
    finally:
        loop.close()


if __name__ == "__main__":
    main()
