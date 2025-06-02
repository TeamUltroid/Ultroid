# Ultroid - UserBot
# Copyright (C) 2021-2025 TeamUltroid
#
# This file is a part of < https://github.com/TeamUltroid/Ultroid/ >
# PLease read the GNU Affero General Public License in
# <https://github.com/TeamUltroid/pyUltroid/blob/main/LICENSE>.

from aiohttp import web
import os
import sys
import time
import logging
import asyncio
from typing import Optional
from pathlib import Path
from git import Repo
import json

from ..decorators import route, setup_routes
from ..middleware import telegram_auth_middleware
from ... import ultroid_bot

logger = logging.getLogger(__name__)

try:
    from git import Repo
except ImportError:
    logger.error("admin: 'gitpython' module not found!")
    Repo = None


def is_owner(user_id: Optional[int]) -> bool:
    """Check if the user is the bot owner."""
    try:
        return user_id == ultroid_bot.me.id
    except Exception as e:
        logger.error(f"Failed to check owner status: {e}")
        return False


async def check_owner(request: web.Request) -> bool:
    """Middleware to check if the user is the bot owner."""
    user = request.get("user", {})
    user_id = user.get("id")
    if not user_id or not is_owner(int(user_id)):
        raise web.HTTPForbidden(
            text=json.dumps({"error": "Only bot owner can access this endpoint"}),
            content_type="application/json",
        )
    return True


async def restart_bot() -> None:
    """Restart the bot process."""
    if os.getenv("DYNO"):  # Heroku
        os.system("kill 1")
    else:
        if len(sys.argv) > 1:
            os.execl(sys.executable, sys.executable, "main.py")
        else:
            os.execl(sys.executable, sys.executable, "-m", "pyUltroid")


async def update_bot(fast: bool = False) -> dict:
    """Update the bot from the repository."""
    try:
        repo = Repo()
        branch = repo.active_branch

        if fast:
            stdout, stderr, code = await bash(
                "git pull -f && pip3 install -r requirements.txt"
            )
            if code != 0:
                raise Exception(f"Fast update failed: {stderr}")
            return {
                "status": "success",
                "message": "Fast update completed",
                "restart_required": True,
            }

        # Check for updates
        origin = repo.remotes.origin
        origin.fetch()
        if not repo.is_dirty():
            commits_behind = sum(
                1 for _ in repo.iter_commits(f"{branch.name}..origin/{branch.name}")
            )
            if commits_behind == 0:
                return {
                    "status": "success",
                    "message": "Already up to date!",
                    "update_available": False,
                }

        # Pull changes
        stdout, stderr, code = await bash(
            "git pull && pip3 install -r requirements.txt"
        )
        if code != 0:
            raise Exception(f"Update failed: {stderr}")

        return {
            "status": "success",
            "message": "Update successful",
            "branch": branch.name,
            "update_available": True,
            "restart_required": True,
        }
    except Exception as e:
        logger.error(f"Update failed: {str(e)}", exc_info=True)
        return {"status": "error", "message": f"Update failed: {str(e)}"}


async def bash(cmd: str) -> tuple[str, str, int]:
    """Execute a bash command and return stdout, stderr, and return code."""
    process = await asyncio.create_subprocess_shell(
        cmd,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )
    stdout, stderr = await process.communicate()
    return stdout.decode(), stderr.decode(), process.returncode


# Route handlers
@route(
    "/api/admin/update",
    method="POST",
    owner_only=True,
    description="Update the bot from repository",
)
async def handle_update(request: web.Request) -> web.Response:
    """Handle bot update request.
    Query params:
        fast: bool - Whether to perform a fast update (force pull)
    """
    await check_owner(request)

    try:
        data = await request.json() if request.can_read_body else {}
        fast = data.get("fast", False)
        result = await update_bot(fast)
        return web.json_response(result)
    except json.JSONDecodeError:
        # If no body provided, assume default options
        result = await update_bot(False)
        return web.json_response(result)


@route(
    "/api/admin/restart", method="POST", owner_only=True, description="Restart the bot"
)
async def handle_restart(request: web.Request) -> web.Response:
    """Handle bot restart request."""
    await check_owner(request)

    try:
        # Schedule the restart
        asyncio.create_task(restart_bot())
        return web.json_response({"status": "success", "message": "Restart initiated"})
    except Exception as e:
        logger.error(f"Restart failed: {str(e)}", exc_info=True)
        return web.json_response(
            {"status": "error", "message": f"Restart failed: {str(e)}"}, status=500
        )


# List of all handlers
handlers = [handle_update, handle_restart]


def setup_admin_routes(app: web.Application) -> None:
    """Setup admin routes with authentication middleware."""
    setup_routes(app, handlers)
