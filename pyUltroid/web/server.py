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

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Track server start time
start_time = time.time()

class UltroidWebServer:
    def __init__(self):
        self.app = web.Application()
        self.setup_routes()
        self.setup_cors()
        self.user_data: Dict[str, Dict] = {}
        self.port = int(os.getenv('PORT', 8000))
        self.bot = ultroid_bot
        
        # SSL Configuration
        self.ssl_context = None
        self.cert_file = os.path.expanduser("~/myssl/localhost.crt")
        self.key_file = os.path.expanduser("~/myssl/localhost.key")
        
        if os.path.exists(self.cert_file) and os.path.exists(self.key_file):
            self.ssl_context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
            self.ssl_context.load_cert_chain(self.cert_file, self.key_file)
            logger.info("SSL certificates loaded successfully")
        else:
            logger.warning("SSL certificates not found, running without SSL")

    def setup_routes(self):
        self.app.router.add_get("/api/user", self.get_ultroid_owner_info)
        
    def setup_cors(self):
        cors = aiohttp_cors.setup(self.app, defaults={
            "*": aiohttp_cors.ResourceOptions(
                allow_credentials=True,
                expose_headers="*",
                allow_headers="*",
                allow_methods=["GET"]
            )
        })
        
        for route in list(self.app.router.routes()):
            cors.add(route)

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
        """Single endpoint for public user information"""
        
        # Get Telegram user info
        telegram_info = self.bot.me
        
        if not telegram_info:
            return web.json_response({
                "error": "User not found"
            }, status=404)
        
        # Get bot-related stats
        stats = {
            "uptime": time_formatter(time.time() - start_time),
        }
        
        # Initialize public data
        public_data = {
            "name": get_display_name(self.bot.me),
            "bio": "",
            "avatar": "",
            "username": self.bot.me.username,
            "telegram_url": f"https://t.me/{self.bot.me.username}" if self.bot.me.username else None,
            "stats": stats,
            "skills": ["Telegram Bot Management", "Automation", "Python"]
        }
        
        # If user has a username, try to get additional info from public profile
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
        
        return web.json_response(public_data)

    async def cleanup(self):
        """Clean up resources when server shuts down"""
        await scraper.close()

    def run(self, host: str = "0.0.0.0", port: Optional[int] = None):
        """Run the web server with SSL if certificates are available"""
        # Add cleanup on shutdown
        self.app.on_shutdown.append(lambda app: self.cleanup())
        
        if self.ssl_context:
            logger.info(f"Starting HTTPS server on {host}:{port or self.port}")
            web.run_app(
                self.app,
                host=host,
                port=port or self.port,
                ssl_context=self.ssl_context
            )
        else:
            logger.info(f"Starting HTTP server on {host}:{port or self.port}")
            web.run_app(self.app, host=host, port=port or self.port)

ultroid_server = UltroidWebServer()

if __name__ == "__main__":
    ultroid_server.run()
