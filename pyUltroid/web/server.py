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
        
        # Add plugin installation routes
        self.app.router.add_post("/api/plugins/install", self.install_plugin)
        self.app.router.add_get("/api/plugins/installed", self.get_installed_plugins)
        logger.info("Plugin installation routes configured at /api/plugins/")
        
        cors = aiohttp_cors.setup(
            self.app,
            defaults={
                "*": aiohttp_cors.ResourceOptions(
                    allow_credentials=True,
                    expose_headers="*",
                    allow_headers="*",
                    allow_methods="*",
                )            },
        )        # Add CORS to all registered routes
        for route in list(self.app.router.routes()):
            cors.add(route)

    async def health_check(self, request: web.Request) -> web.Response:
        """Health check endpoint that doesn't require auth"""
        return web.json_response({"status": "ok"})

    async def save_miniapp_settings(self, request: web.Request) -> web.Response:
        """Save mini app and bot configuration settings to udB"""
        try:
            data = await request.json()
            
            # Handle both single key-value and multiple settings
            settings_to_save = []
            
            if "key" in data and "value" in data:
                # Single key-value pair
                settings_to_save.append({"key": data["key"], "value": data["value"]})
            elif "settings" in data:
                # Multiple settings
                settings_to_save = data["settings"]
            else:
                return web.json_response({"error": "Missing key/value or settings parameter"}, status=400)

            if not settings_to_save:
                return web.json_response({"error": "No settings provided"}, status=400)

            # Bot configuration settings that should be stored directly in udB
            bot_config_keys = [
                "DUAL_MODE", "BOT_MODE", "HNDLR", "DUAL_HNDLR",
                "SUDO", "SUDO_HNDLR", "ADDONS", "PLUGIN_CHANNEL", "EMOJI_IN_HELP",
                "PMSETTING", "INLINE_PM", "PM_TEXT", "PMPIC", "PMWARNS", "AUTOAPPROVE",
                "PMLOG", "PMLOGGROUP", "PMBOT", "STARTMSG", "STARTMEDIA", "BOT_INFO_START",
                "ALIVE_TEXT", "ALIVE_PIC", "INLINE_PIC", "TAG_LOG", "FBAN_GROUP_ID",
                "EXCLUDE_FED", "RMBG_API", "DEEP_AI", "OCR_API", "GDRIVE_FOLDER_ID",
                "VC_SESSION", "PMBOT_FSUB"
            ]
            
            # Get current miniapp settings once
            miniapp_settings = udB.get_key("MINIAPP_SETTINGS") or {}
            miniapp_settings_updated = False
            
            # Process all settings
            for setting in settings_to_save:
                key = setting.get("key")
                value = setting.get("value")
                
                if not key:
                    continue
                    
                if key in bot_config_keys:
                    # Handle special data type conversions based on callbackstuffs.py
                    if key == "PMWARNS":
                        # PMWARNS should be stored as integer
                        try:
                            value = int(value)
                        except (ValueError, TypeError):
                            return web.json_response(
                                {"error": f"PMWARNS must be a valid integer, got: {value}"}, status=400
                            )
                    elif key in ["DUAL_MODE", "BOT_MODE", "SUDO", "ADDONS", "PMSETTING", 
                               "INLINE_PM", "AUTOAPPROVE", "PMLOG", "PMBOT"]:
                        # Boolean settings that should be stored as string "True"/"False"
                        if isinstance(value, bool):
                            value = "True" if value else "False"
                        elif value not in ["True", "False", True, False]:
                            # Convert other truthy/falsy values
                            value = "True" if value else "False"
                    elif key == "PMBOT_FSUB" and isinstance(value, (list, tuple)):
                        # PMBOT_FSUB should be stored as string representation of list
                        value = str(value)
                    elif key == "EXCLUDE_FED" and isinstance(value, str):
                        # EXCLUDE_FED can be space-separated IDs, keep as string
                        pass
                    
                    # Store bot configuration directly in udB
                    udB.set_key(key, value)
                    logger.info(f"Saved Bot config setting: {key}={value}")
                else:
                    # Store mini app settings in MINIAPP_SETTINGS
                    miniapp_settings[key] = value
                    miniapp_settings_updated = True
                    logger.info(f"Saved Mini App setting: {key}={value}")
            
            # Save miniapp settings once if any were updated
            if miniapp_settings_updated:
                udB.set_key("MINIAPP_SETTINGS", miniapp_settings)

            saved_count = len(settings_to_save)
            return web.json_response(
                {"success": True, "message": f"{saved_count} setting(s) saved successfully"}
            )
        except Exception as e:
            logger.error(f"Error saving settings: {str(e)}", exc_info=True)
            return web.json_response(
                {"error": f"Failed to save settings: {str(e)}"}, status=500
            )
    
    async def get_miniapp_settings(self, request: web.Request) -> web.Response:
        """Get mini app and bot configuration settings from udB"""
        try:
            # Get mini app settings
            miniapp_settings = udB.get_key("MINIAPP_SETTINGS") or {}
            
            # Get bot configuration settings
            bot_config_keys = [
                "DUAL_MODE", "BOT_MODE", "HNDLR", "DUAL_HNDLR",
                "SUDO", "SUDO_HNDLR", "ADDONS", "PLUGIN_CHANNEL", "EMOJI_IN_HELP",
                "PMSETTING", "INLINE_PM", "PM_TEXT", "PMPIC", "PMWARNS", "AUTOAPPROVE",
                "PMLOG", "PMLOGGROUP", "PMBOT", "STARTMSG", "STARTMEDIA", "BOT_INFO_START",
                "ALIVE_TEXT", "ALIVE_PIC", "INLINE_PIC", "TAG_LOG", "FBAN_GROUP_ID",
                "EXCLUDE_FED", "RMBG_API", "DEEP_AI", "OCR_API", "GDRIVE_FOLDER_ID",
                "VC_SESSION", "PMBOT_FSUB"
            ]
            bot_settings = {}
            
            for key in bot_config_keys:
                value = udB.get_key(key)
                if value is not None:
                    bot_settings[key] = value
            
            # Merge both settings (only include keys that have values)
            all_settings = {**miniapp_settings, **bot_settings}
            
            return web.json_response(all_settings)
        except Exception as e:
            logger.error(f"Error getting settings: {str(e)}", exc_info=True)
            return web.json_response(
                {"error": f"Failed to get settings: {str(e)}"}, status=500
            )

    async def install_plugin(self, request: web.Request) -> web.Response:
        """Install a plugin by ID and store it in udB INSTALLED_PLUGINS"""
        try:
            # Check if user is authenticated
            if not request.get('user'):
                return web.json_response(
                    {"error": "Authentication required"}, status=401
                )

            data = await request.json()
            plugin_id = data.get("plugin_id")
            
            if not plugin_id:
                return web.json_response(
                    {"error": "Missing plugin_id parameter"}, status=400
                )

            # Import necessary modules for plugin installation
            import aiohttp
            import base64
            from pathlib import Path
            from ..configs import CENTRAL_REPO_URL
            from ..state_config import temp_config_store

            # Get authentication data
            user_data = temp_config_store.get("X-TG-USER")
            if not user_data:
                return web.json_response(
                    {"error": "No authentication data found"}, status=401
                )

            user_id = str(user_data["id"])
            encoded_init_data = temp_config_store.get(f"X-TG-INIT-DATA-{user_id}")
            encoded_hash = temp_config_store.get(f"X-TG-HASH-{user_id}")

            if not encoded_init_data or not encoded_hash:
                return web.json_response(
                    {"error": "Missing authentication tokens"}, status=401
                )

            # Decode authentication data
            init_data = base64.b64decode(encoded_init_data.encode()).decode()
            hash_value = base64.b64decode(encoded_hash.encode()).decode()

            async with aiohttp.ClientSession() as session:
                # First, get plugin details
                api_url = f"{CENTRAL_REPO_URL}/api/v1/plugins/{plugin_id}"
                headers = {
                    "Content-Type": "application/json",
                    "X-Telegram-Init-Data": init_data,
                    "X-Telegram-Hash": hash_value
                }

                async with session.get(api_url, headers=headers) as response:
                    if response.status != 200:
                        error_text = await response.text()
                        return web.json_response(
                            {"error": f"Failed to fetch plugin details: {error_text}"}, 
                            status=response.status
                        )
                    
                    plugin_data = await response.json()

                # Download the plugin file
                download_url = plugin_data.get("download_link")
                if not download_url:
                    return web.json_response(
                        {"error": "Plugin download link not available"}, status=400
                    )

                async with session.get(download_url) as download_response:
                    if download_response.status != 200:
                        return web.json_response(
                            {"error": "Failed to download plugin file"}, 
                            status=download_response.status
                        )
                    
                    plugin_content = await download_response.text()

                # Create addons directory if it doesn't exist
                addons_dir = Path("addons")
                addons_dir.mkdir(exist_ok=True)

                # Generate safe filename
                plugin_title = plugin_data.get("title", "plugin")
                file_path = plugin_data.get("file_path", "")
                if file_path:
                    safe_filename = Path(file_path).name
                else:
                    safe_filename = f"{plugin_title.lower().replace(' ', '_')}_{plugin_id}.py"

                if not safe_filename.endswith('.py'):
                    safe_filename += '.py'

                target_path = addons_dir / safe_filename

                # Write the plugin file
                target_path.write_text(plugin_content, encoding='utf-8')

                # Update installed plugins list in udB
                installed_plugins = udB.get_key("INSTALLED_PLUGINS") or []
                if str(plugin_id) not in installed_plugins:
                    installed_plugins.append(str(plugin_id))
                    udB.set_key("INSTALLED_PLUGINS", installed_plugins)

                # Load the plugin dynamically
                try:
                    from ..loader import Loader
                    from ..startup.utils import load_addons
                    from ..startup.loader import _after_load
                    
                    # Load the specific plugin
                    loader = Loader(path="addons", key="Addons")
                    # Load only the newly installed plugin
                    loader.load_single_plugin(
                        target_path,
                        func=load_addons,
                        after_load=_after_load
                    )
                    
                    logger.info(f"Successfully loaded plugin: {plugin_title}")
                except Exception as load_error:
                    logger.error(f"Error loading plugin {plugin_title}: {str(load_error)}")
                
                return web.json_response({
                    "success": True,
                    "message": f"Plugin '{plugin_title}' installed successfully",
                    "plugin_id": plugin_id,
                    "filename": safe_filename
                })

        except Exception as e:
            logger.error(f"Error installing plugin: {str(e)}", exc_info=True)
            return web.json_response(
                {"error": f"Failed to install plugin: {str(e)}"}, status=500
            )

    async def get_installed_plugins(self, request: web.Request) -> web.Response:
        """Get list of installed plugin IDs including official plugins from INCLUDE_ALL"""
        try:
            # Get manually installed plugins
            installed_plugins = udB.get_key("INSTALLED_PLUGINS") or []
            
            # Get official plugins installed via INCLUDE_ALL
            from ..state_config import temp_config_store
            official_plugins_state = temp_config_store.get("OFFICIAL_PLUGINS_STATE")
            
            if official_plugins_state:
                try:
                    import json
                    official_plugins = json.loads(official_plugins_state)
                    # Add official plugin IDs to installed list
                    for plugin_id in official_plugins.keys():
                        if plugin_id not in installed_plugins:
                            installed_plugins.append(plugin_id)
                except Exception as e:
                    logger.error(f"Error parsing official plugins state: {str(e)}")
            
            return web.json_response({
                "installed_plugins": installed_plugins
            })
        except Exception as e:
            logger.error(f"Error getting installed plugins: {str(e)}", exc_info=True)
            return web.json_response(
                {"error": f"Failed to get installed plugins: {str(e)}"}, status=500
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
