import asyncio
from redis import Redis
from redis.exceptions import ConnectionError


def connect_localhost_redis():
    try:
        redis = Redis(host="localhost", port=6379, db=0, decode_responses=True)
        redis.ping()
        return redis
    except ConnectionError as er:
        return False


async def is_redis_server_installed():
    proc = await asyncio.create_subprocess_exec("redis-server", "--version")
    stdout, stderr = await proc.communicate()
    return proc.returncode == 0


async def start_redis_server():
    proc = await asyncio.create_subprocess_exec("redis-server", "--daemonize yes")
    stdout, stderr = await proc.communicate()
    await asyncio.sleep(2)  # Wait for server to start
    return proc.returncode == 0


async def stop_redis_server():
    proc = await asyncio.create_subprocess_exec("redis-cli", "shutdown")
    stdout, stderr = await proc.communicate()
    return proc.returncode == 0
