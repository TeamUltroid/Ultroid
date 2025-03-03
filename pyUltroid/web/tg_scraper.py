import aiohttp
import logging
import re
from bs4 import BeautifulSoup
from typing import Dict, Optional, Tuple

logger = logging.getLogger(__name__)

class TelegramProfileScraper:
    """Utility to scrape public information from Telegram web profiles"""
    
    def __init__(self):
        self.session = None
        self.cache = {}  # Simple cache to avoid repeated requests
    
    async def _get_session(self):
        if self.session is None or self.session.closed:
            self.session = aiohttp.ClientSession(
                headers={
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
                }
            )
        return self.session
    
    async def close(self):
        if self.session and not self.session.closed:
            await self.session.close()
    
    async def get_profile_info(self, username: str) -> Optional[Dict]:
        """
        Scrape profile information from a public Telegram profile
        
        Args:
            username: Telegram username without the @ symbol
            
        Returns:
            Dictionary with profile information or None if not found
        """
        # Check cache first
        if username in self.cache:
            return self.cache[username]
        
        try:
            # Clean the username
            username = username.strip().lower()
            if username.startswith('@'):
                username = username[1:]
                
            url = f"https://t.me/{username}"
            session = await self._get_session()
            
            async with session.get(url) as response:
                if response.status != 200:
                    logger.warning(f"Failed to fetch profile for {username}: HTTP {response.status}")
                    return None
                
                html = await response.text()
                
                # Parse the HTML
                soup = BeautifulSoup(html, 'html.parser')
                
                # Extract profile information
                result = {}
                
                # Get profile image
                img_tag = soup.select_one('img.tgme_page_photo_image')
                if img_tag and 'src' in img_tag.attrs:
                    result['avatar'] = img_tag['src']
                
                # Get bio
                bio_div = soup.select_one('div.tgme_page_description')
                if bio_div:
                    result['bio'] = bio_div.get_text(strip=True)
                
                # Get name
                title_tag = soup.select_one('div.tgme_page_title')
                if title_tag:
                    result['name'] = title_tag.get_text(strip=True)
                
                # Cache the result
                self.cache[username] = result
                return result
                
        except Exception as e:
            logger.error(f"Error scraping profile for {username}: {e}")
            return None
    
    async def get_profile_image(self, username: str) -> Optional[str]:
        """Get just the profile image URL"""
        profile = await self.get_profile_info(username)
        return profile.get('avatar') if profile else None
    
    async def get_profile_bio(self, username: str) -> Optional[str]:
        """Get just the profile bio"""
        profile = await self.get_profile_info(username)
        return profile.get('bio') if profile else None

# Singleton instance
scraper = TelegramProfileScraper() 

if __name__ == "__main__":
    import asyncio
    asyncio.run(scraper.get_profile_info("karboncopy"))
