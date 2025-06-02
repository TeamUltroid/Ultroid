# Ultroid - UserBot
# Copyright (C) 2021-2025 TeamUltroid
#
# This file is a part of <https://github.com/TeamUltroid/Ultroid/ >
# PLease read the GNU Affero General Public License in
# <https://github.com/TeamUltroid/pyUltroid/blob/main/LICENSE>.

import asyncio
from . import *
from ..configs import Var


async def UltroidDB():
    from .. import HOSTED_ON

    # Try Redis first if configured
    if Var.REDIS_URI or Var.REDISHOST:
        try:
            from ..database.redis import RedisDB

            return RedisDB(
                host=Var.REDIS_URI or Var.REDISHOST,
                password=Var.REDIS_PASSWORD or Var.REDISPASSWORD,
                port=Var.REDISPORT,
                platform=HOSTED_ON,
                decode_responses=True,
                socket_timeout=5,
                retry_on_timeout=True,
            )
        except Exception as e:
            LOGS.warning(f"Redis connection failed: {e}")

    # Try MongoDB if configured
    if Var.MONGO_URI:
        try:
            from ..database.mongo import MongoDB

            return MongoDB(Var.MONGO_URI)
        except Exception as e:
            LOGS.warning(f"MongoDB connection failed: {e}")

    # Try local Redis server
    try:
        from ..database.redis import RedisDB

        from ..scripts.redis import (
            is_redis_server_installed,
            connect_localhost_redis,
            start_redis_server,
        )

        # Check for running Redis instance first
        if redis := connect_localhost_redis():
            LOGS.info("Connected to running Redis server")
            return RedisDB(client=redis)

        # Try to start Redis if not running
        if not await is_redis_server_installed():
            raise ConnectionError("Redis server is not installed")

        if await start_redis_server():
            LOGS.info("Started new Redis server")
            if redis := connect_localhost_redis():
                return RedisDB(client=redis)
            raise ConnectionError("Failed to connect to newly started Redis server")

        raise ConnectionError("Failed to start Redis server")

    except Exception as e:
        LOGS.warning(f"Local Redis setup failed: {e}")

    # Fallback to memory database
    try:
        from ..database.base import BaseDatabase

        LOGS.critical(
            "No database requirements fulfilled! Using memory database as fallback. "
            "Please install Redis, MongoDB or SQL dependencies for persistent storage."
        )
        return BaseDatabase()
    except Exception as e:
        LOGS.critical(f"Failed to initialize memory database: {e}")
        exit(1)


# --------------------------------------------------------------------------------------------- #
