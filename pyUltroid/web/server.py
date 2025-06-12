# Ultroid - UserBot
# Copyright (C) 2021-2025 TeamUltroid
#
# This file is a part of < https://github.com/TeamUltroid/Ultroid/ >
# PLease read the GNU Affero General Public License in
# <https://github.com/TeamUltroid/pyUltroid/blob/main/LICENSE>.

from aiohttp import web
import json
from typing import Dict, Optional
import logging
import os
from .. import ultroid_bot, udB
from pyUltroid.fns.helper import time_formatter
from telethon.utils import get_display_name
import time
import ssl
from pathlib import Path
from .tg_scraper import scraper
from .middleware import telegram_auth_middleware
import aiohttp_cors
from .routers.admin import setup_admin_routes
from .routers.plugins import setup_plugin_routes
from .routers.miniapp import setup_miniapp_routes
from .cache import owner_cache
from ..configs import Var

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Track server start time
start_time = time.time()


class UltroidWebServer:
    def __init__(self):
        # Check for BOT_TOKEN
        bot_token = os.getenv("BOT_TOKEN")
        if not bot_token:
            logger.error(
                "BOT_TOKEN environment variable is not set! Authentication will fail."
            )
        else:
            logger.info("BOT_TOKEN is properly configured.")

        # Important: telegram_auth_middleware must come before no_cors_middleware
        self.app = web.Application(middlewares=[telegram_auth_middleware])
        self.setup_routes()
        self.port = Var.PORT
        self.bot = ultroid_bot
        self.ssl_context = None

    def setup_routes(self):
        """Setup basic API routes"""
        # Add routes
        self.app.router.add_get("/api/user", self.get_ultroid_owner_info)
        self.app.router.add_get("/health", self.health_check)
        self.app.router.add_post("/api/settings/miniapp", self.save_miniapp_settings)
        self.app.router.add_get("/api/settings/miniapp", self.get_miniapp_settings)

        # Setup admin, plugin, and miniapp routes
        setup_admin_routes(self.app)
        logger.info("Admin routes configured at /api/admin/")

        setup_plugin_routes(self.app)
        logger.info("Plugin routes configured at /api/v1/plugins/")

        setup_miniapp_routes(self.app)
        logger.info("MiniApp routes configured at /api/miniapp/")

        # Configure CORS and apply to all routes
        cors = aiohttp_cors.setup(
            self.app,
            defaults={
                "*": aiohttp_cors.ResourceOptions(
                    allow_credentials=True,
                    expose_headers="*",
                    allow_headers="*",
                    allow_methods="*",
                )
            },
        )

        # Add CORS to all registered routes
        for route in list(self.app.router.routes()):
            cors.add(route)

    async def health_check(self, request: web.Request) -> web.Response:
        """Health check endpoint that doesn't require auth"""
        return web.json_response({"status": "ok"})

    async def save_miniapp_settings(self, request: web.Request) -> web.Response:
        """Save mini app settings to udB"""
        try:
            data = await request.json()
            key = data.get("key")
            value = data.get("value")

            if not key:
                return web.json_response({"error": "Missing key parameter"}, status=400)

            # Create the miniapp settings key if it doesn't exist
            if not udB.get_key("MINIAPP_SETTINGS"):
                udB.set_key("MINIAPP_SETTINGS", {})

            # Get current settings
            settings = udB.get_key("MINIAPP_SETTINGS") or {}

            # Update with new value
            settings[key] = value

            # Save back to database
            udB.set_key("MINIAPP_SETTINGS", settings)

            logger.info(f"Saved Mini App setting: {key}={value}")
            return web.json_response(
                {"success": True, "message": "Settings saved successfully"}
            )
        except Exception as e:
            logger.error(f"Error saving Mini App settings: {str(e)}", exc_info=True)
            return web.json_response(
                {"error": f"Failed to save settings: {str(e)}"}, status=500
            )

    async def get_miniapp_settings(self, request: web.Request) -> web.Response:
        """Get mini app settings from udB"""
        try:
            settings = udB.get_key("MINIAPP_SETTINGS") or {}
            return web.json_response(settings)
        except Exception as e:
            logger.error(f"Error getting Mini App settings: {str(e)}", exc_info=True)
            return web.json_response(
                {"error": f"Failed to get settings: {str(e)}"}, status=500
            )

    async def get_ultroid_owner_info(self, request: web.Request) -> web.Response:
        cache_key = f"owner_info_{self.bot.me.id}"
        cached_data = owner_cache.get(cache_key)

        if cached_data:
            logger.debug("Returning cached owner info")
            return web.json_response(cached_data)

        try:
            stats = {
                "uptime": time_formatter(time.time() - start_time),
            }

            public_data = {
                "name": get_display_name(self.bot.me),
                "bio": "",
                "avatar": "",
                "username": self.bot.me.username,
                "telegram_url": (
                    f"https://t.me/{self.bot.me.username}"
                    if self.bot.me.username
                    else None
                ),
                "stats": stats,
                "skills": ["Telegram Bot Management", "Automation", "Python"],
                "user_id": self.bot.me.id,
                "authenticated_user": request.get("user", {}),
                "start_param": request.get("start_param"),
                "auth_date": request.get("auth_date"),
            }

            if self.bot.me.username:
                try:
                    profile_info = await scraper.get_profile_info(self.bot.me.username)
                    if profile_info:
                        if "bio" in profile_info and profile_info["bio"]:
                            public_data["bio"] = profile_info["bio"]
                        if "avatar" in profile_info and profile_info["avatar"]:
                            public_data["avatar"] = profile_info["avatar"]
                except Exception as e:
                    logger.error(f"Error fetching profile info: {e}")

            owner_cache.set(cache_key, public_data)
            return web.json_response(public_data)

        except Exception as e:
            logger.error(f"Error in get_ultroid_owner_info: {e}", exc_info=True)
            return web.json_response(
                {"error": "Failed to fetch owner info"}, status=500
            )

    async def _setup_web_app_build(self):
        """Setup web app build directory if it exists"""
        from pyUltroid.scripts.webapp import fetch_recent_release

        # Download and extract the latest webapp release
        success = await fetch_recent_release()

        # First try using the downloaded webapp from resources
        webapp_path = Path("resources/webapp")
        if success and webapp_path.exists():
            logger.info(f"Setting up webapp at {webapp_path.absolute()}")
            if Var.MINIAPP_URL:
                with open(webapp_path / "config.json", "w") as f:
                    config_data = {
                        "apiUrl": Var.MINIAPP_URL,
                    }
                    json.dump(config_data, f, indent=4)

            # Add specific handler for root path to serve index.html
            index_file = webapp_path / "index.html"
            if index_file.exists():

                async def root_handler(request):
                    logger.debug("Serving index.html for root path /")
                    return web.FileResponse(index_file)

                # Add root handler first to ensure it has priority
                self.app.router.add_get("/", root_handler)
                logger.info(f"Added specific route for / to serve {index_file}")

            try:
                self.app.router.add_static("/", path=webapp_path)
                logger.info(f"Serving static files from {webapp_path}")
            except Exception as e:
                logger.error(f"Failed to add static route: {e}", exc_info=True)
                return

            async def handle_index(request):
                index_file = webapp_path / "index.html"
                if index_file.exists():
                    logger.debug(f"Serving index.html for route: {request.path}")
                    return web.FileResponse(index_file)
                else:
                    logger.warning(f"index.html not found at {index_file}")
                    return web.Response(
                        text="Web application is being setup...",
                        content_type="text/html",
                    )

            # Add fallback route for SPA navigation
            self.app.router.add_get("/{tail:.*}", handle_index)
            logger.info("Added SPA fallback handler")
        else:
            logger.info("Web app build is disabled!")

    async def cleanup(self):
        """Clean up resources when server shuts down"""
        await scraper.close()
        owner_cache.clear()

    async def start(self, host: str = "0.0.0.0", port: Optional[int] = None):
        """Asynchronously starts the web server."""
        if Var.RENDER_WEB:
            logger.info("Setting up web app build...")
            await self._setup_web_app_build()

        self.app.on_shutdown.append(self.cleanup)

        runner = web.AppRunner(self.app)
        await runner.setup()

        _port = port or self.port
        site = web.TCPSite(runner, host, _port, ssl_context=self.ssl_context)
        await site.start()

        logger.info(
            f"Starting {'HTTPS' if self.ssl_context else 'HTTP'} server on {host}:{_port}"
        )


ultroid_server = UltroidWebServer()
