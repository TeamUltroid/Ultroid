from aiohttp import web
import aiohttp_cors
import json
from typing import Dict, Optional
import logging
import os
from .. import ultroid_bot
from pyUltroid.fns.helper import time_formatter
from telethon.utils import get_display_name
import time
import ssl
from pathlib import Path
from .tg_scraper import scraper
from .middleware import telegram_auth_middleware
from .routers.admin import setup_admin_routes
from .cache import owner_cache

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Track server start time
start_time = time.time()

class UltroidWebServer:
    def __init__(self):
        # Check for BOT_TOKEN
        bot_token = os.getenv('BOT_TOKEN')
        if not bot_token:
            logger.error("BOT_TOKEN environment variable is not set! Authentication will fail.")
        else:
            logger.info("BOT_TOKEN is properly configured.")
            
        self.app = web.Application(middlewares=[telegram_auth_middleware])
        self.setup_routes()
        self.setup_cors()
        self.setup_admin()
        self.user_data: Dict[str, Dict] = {}
        self.port = int(os.getenv('PORT', 8000))
        self.bot = ultroid_bot
        
        # SSL Configuration
        self.ssl_context = None

    def setup_routes(self):
        self.app.router.add_get("/api/user", self.get_ultroid_owner_info)
        self.app.router.add_get("/health", self.health_check)
        
    def setup_cors(self):
        cors = aiohttp_cors.setup(self.app, defaults={
            "*": aiohttp_cors.ResourceOptions(
                allow_credentials=True,
                expose_headers="*",
                allow_headers="*",
                allow_methods=["GET", "POST", "OPTIONS"]  # Added POST for admin endpoints
            )
        })
        
        for route in list(self.app.router.routes()):
            cors.add(route)

    def setup_admin(self):
        """Setup admin routes with authentication."""
        setup_admin_routes(self.app)
        logger.info("Admin routes configured at /api/admin/")

    async def health_check(self, request: web.Request) -> web.Response:
        """Health check endpoint that doesn't require auth"""
        return web.json_response({"status": "ok"})

    async def get_telegram_user_info(self, user_id: str):
        """Get user info from Telegram"""
        try:
            user = await self.bot.get_entity(int(user_id))
            return {
                "name": get_display_name(user),
                "bio": user.about if hasattr(user, 'about') else "",
                "username": user.username if hasattr(user, 'username') else None,
                "photo": user.photo if hasattr(user, 'photo') else None
            }
        except Exception as e:
            logger.error(f"Error fetching Telegram user info: {e}")
            return None

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
                "telegram_url": f"https://t.me/{self.bot.me.username}" if self.bot.me.username else None,
                "stats": stats,
                "skills": ["Telegram Bot Management", "Automation", "Python"],
                "user_id": self.bot.me.id,
                "authenticated_user": request.get('user', {}),
                "start_param": request.get('start_param'),
                "auth_date": request.get('auth_date')
            }
            
            if self.bot.me.username:
                try:
                    profile_info = await scraper.get_profile_info(self.bot.me.username)
                    if profile_info:
                        if 'bio' in profile_info and profile_info['bio']:
                            public_data['bio'] = profile_info['bio']
                        if 'avatar' in profile_info and profile_info['avatar']:
                            public_data['avatar'] = profile_info['avatar']
                except Exception as e:
                    logger.error(f"Error fetching profile info: {e}")
            
            owner_cache.set(cache_key, public_data)
            return web.json_response(public_data)
            
        except Exception as e:
            logger.error(f"Error in get_ultroid_owner_info: {e}", exc_info=True)
            return web.json_response({"error": "Failed to fetch owner info"}, status=500)

    async def cleanup(self):
        """Clean up resources when server shuts down"""
        await scraper.close()
        owner_cache.clear()

    def run(self, host: str = "0.0.0.0", port: Optional[int] = None):
        """Run the web server with SSL if certificates are available"""
        import asyncio
        
        async def _run_app():
            # Add cleanup on shutdown
            self.app.on_shutdown.append(lambda app: self.cleanup())
            
            runner = web.AppRunner(self.app)
            await runner.setup()
            
            if self.ssl_context:
                site = web.TCPSite(runner, host, port or self.port, ssl_context=self.ssl_context)
                logger.info(f"Starting HTTPS server on {host}:{port or self.port}")
            else:
                site = web.TCPSite(runner, host, port or self.port)
                logger.info(f"Starting HTTP server on {host}:{port or self.port}")
                
            await site.start()
            
            # Keep the server running
            while True:
                await asyncio.sleep(3600)  # Sleep for an hour
                
        # Create new event loop for this thread
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        try:
            loop.run_until_complete(_run_app())
        except KeyboardInterrupt:
            pass
        finally:
            loop.close()

ultroid_server = UltroidWebServer()
