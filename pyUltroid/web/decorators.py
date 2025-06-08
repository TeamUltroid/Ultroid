# Ultroid - UserBot
# Copyright (C) 2021-2025 TeamUltroid
#
# This file is a part of < https://github.com/TeamUltroid/Ultroid/ >
# PLease read the GNU Affero General Public License in
# <https://github.com/TeamUltroid/pyUltroid/blob/main/LICENSE>.

from functools import wraps
from typing import Callable, Optional, Any
import json
import os
from aiohttp import web
import logging
from .. import ultroid_bot

logger = logging.getLogger(__name__)


def is_owner(user_id: Optional[int]) -> bool:
    """Check if the user is the bot owner by comparing with ultroid_bot.me.id."""
    try:
        return user_id == ultroid_bot.me.id
    except Exception as e:
        logger.error(f"Failed to check owner status: {e}")
        return False


def route(
    path: str,
    method: str = "GET",
    *,
    authenticated: bool = True,
    owner_only: bool = False,
    description: Optional[str] = None,
) -> Callable:
    """
    Route decorator with authentication and owner-only options.

    Args:
        path: URL path for the route
        method: HTTP method (GET, POST, etc.)
        authenticated: Whether route requires TMA authentication
        owner_only: Whether route is restricted to bot owner (checks against ultroid_bot.me.id)
        description: Route description for documentation

    Example:
        @route("/api/test", method="POST", authenticated=True, owner_only=True)
        async def handler(request):
            return web.json_response({"status": "ok"})
    """

    def decorator(handler: Callable) -> Callable:
        @wraps(handler)
        async def wrapped(request: web.Request) -> web.Response:
            try:
                # Skip auth checks for unauthenticated routes
                if not authenticated:
                    return await handler(request)

                # Get user from request (set by telegram_auth_middleware)
                user = request.get("user", {})

                # Check owner access if required
                if owner_only:
                    user_id = user.get("id")
                    if not user_id or not is_owner(int(user_id)):
                        raise web.HTTPForbidden(
                            text=json.dumps(
                                {"error": "This endpoint is restricted to bot owner"}
                            ),
                            content_type="application/json",
                        )

                return await handler(request)

            except web.HTTPException:
                raise
            except Exception as e:
                logger.error(f"Error in route handler: {str(e)}", exc_info=True)
                return web.json_response({"error": "Internal server error"}, status=500)

        # Store route metadata
        wrapped._route = {
            "path": path,
            "method": method.upper(),
            "authenticated": authenticated,
            "owner_only": owner_only,
            "description": description,
        }

        return wrapped

    return decorator


def setup_routes(app: web.Application, handlers: list[Callable]) -> None:
    """
    Setup routes from a list of handler functions decorated with @route.

    Args:
        app: aiohttp Application instance
        handlers: List of handler functions with route decorators
    """
    for handler in handlers:
        if hasattr(handler, "_route"):
            route_info = handler._route
            method = route_info["method"]
            path = route_info["path"]

            # Add route to app
            app.router.add_route(method, path, handler)

            logger.debug(
                f"Added route: {method} {path} "
                f"(auth: {route_info['authenticated']}, "
                f"owner: {route_info['owner_only']})"
            )
