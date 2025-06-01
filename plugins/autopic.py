# Ultroid - UserBot
# Copyright (C) 2021-2025 TeamUltroid
#
# This file is a part of < https://github.com/TeamUltroid/Ultroid/ >
# PLease read the GNU Affero General Public License in
# <https://www.github.com/TeamUltroid/Ultroid/blob/main/LICENSE/>.


import asyncio
import os
import random
from random import shuffle
import aiohttp
import re
from telethon.tl.functions.photos import UploadProfilePhotoRequest
from PIL import Image

from pyUltroid.fns.helper import download_file, fast_download

from . import LOGS, get_help, get_string, udB, ultroid_bot, ultroid_cmd

__doc__ = get_help("help_autopic")


async def get_google_images(query: str):
    """Extract image URLs from Google Images search results with fallbacks"""
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    
    search_url = f"https://www.google.com/search?q={query}&tbm=isch"
    
    # Domains to exclude
    excluded_domains = [
        'gstatic.com',
        'google.com',
        'googleusercontent.com',
        'ssl.google.com'
    ]
    
    def is_valid_url(url):
        return not any(domain in url.lower() for domain in excluded_domains)
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(search_url, headers=headers) as response:
                html = await response.text()

        # Try to extract from search results div first
        img_urls = []
        search_pattern = r'<div id="search".*?>(.*?)</div>'
        search_match = re.search(search_pattern, html, re.DOTALL)
        if search_match:
            search_content = search_match.group(1)
            url_pattern = r'https://[^\"]*?\.(?:jpg|jpeg|png|webp)'
            url_matches = re.finditer(url_pattern, search_content, re.IGNORECASE)
            for url_match in url_matches:
                url = url_match.group(0)
                if url not in img_urls and is_valid_url(url):
                    img_urls.append(url)

        # Fallback to tdeeNb div if no results
        if not img_urls:
            pattern = r'<div jsname="tdeeNb"[^>]*>(.*?)</div>'
            matches = re.finditer(pattern, html, re.DOTALL)
            for match in matches:
                div_content = match.group(1)
                url_pattern = r'https://[^\"]*?\.(?:jpg|jpeg|png|webp)'
                url_matches = re.finditer(url_pattern, div_content, re.IGNORECASE)
                for url_match in url_matches:
                    url = url_match.group(0)
                    if url not in img_urls and is_valid_url(url):
                        img_urls.append(url)

        # Fallback to general image search if still no results
        if not img_urls:
            pattern = r"https://[^\"]*?\.(?:jpg|jpeg|png|webp)"
            matches = re.finditer(pattern, html, re.IGNORECASE)
            for match in matches:
                url = match.group(0)
                if url not in img_urls and is_valid_url(url):
                    img_urls.append(url)

        # Final fallback to data URLs if still no results
        if not img_urls:
            pattern = r'data:image/(?:jpeg|png|webp);base64,[^\"]*'
            matches = re.finditer(pattern, html, re.IGNORECASE)
            for match in matches:
                url = match.group(0)
                if url not in img_urls:
                    img_urls.append(url)

        return img_urls
                
    except Exception as e:
        print(f"Error fetching Google images: {e}")
        return []


@ultroid_cmd(pattern="autopic( (.*)|$)")
async def autopic(e):
    search = e.pattern_match.group(1).strip()
    if udB.get_key("AUTOPIC") and not search:
        udB.del_key("AUTOPIC")
        return await e.eor(get_string("autopic_5"))
    if not search:
        return await e.eor(get_string("autopic_1"), time=5)
    e = await e.eor(get_string("com_1"))
    images = await get_google_images(search)
    if not images:
        return await e.eor(get_string("autopic_2").format(search), time=5)
    await e.eor(get_string("autopic_3").format(search))
    udB.set_key("AUTOPIC", search)
    SLEEP_TIME = udB.get_key("SLEEP_TIME") or 1221
    while True:
        for lie in images:
            if udB.get_key("AUTOPIC") != search:
                return
            download_path, stime = await fast_download(lie, "resources/downloads/autopic.jpg")
            img = Image.open(download_path)
            img.save("resources/downloads/autopic.jpg")
            file = await e.client.upload_file("resources/downloads/autopic.jpg")
            await e.client(UploadProfilePhotoRequest(file=file))
            os.remove("resources/downloads/autopic.jpg")
            await asyncio.sleep(SLEEP_TIME)

        shuffle(images)


if search := udB.get_key("AUTOPIC"):
    images = {}
    sleep = udB.get_key("SLEEP_TIME") or 1221

    async def autopic_func():
        search = udB.get_key("AUTOPIC")
        if images.get(search) is None:
            images[search] = await get_google_images(search)
        if not images.get(search):
            return
        img = random.choice(images[search])
        filee, stime = await fast_download(img, "resources/downloads/autopic.jpg")
        img = Image.open(filee)
        img.save("resources/downloads/autopic.jpg")
        file = await ultroid_bot.upload_file("resources/downloads/autopic.jpg")
        await ultroid_bot(UploadProfilePhotoRequest(file=file))
        os.remove(filee)

    try:
        from apscheduler.schedulers.asyncio import AsyncIOScheduler

        schedule = AsyncIOScheduler()
        schedule.add_job(autopic_func, "interval", seconds=sleep)
        schedule.start()
    except ModuleNotFoundError as er:
        LOGS.error(f"autopic: '{er.name}' not installed.")
