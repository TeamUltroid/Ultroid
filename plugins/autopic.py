
from . import *
import urllib
import os 
import re
import random
import asyncio
from telethon import functions
from requests import get
from bs4 import BeautifulSoup as bs
from pyUltroid.functions.autopic import returnpage, animepp

@ultroid_cmd(pattern="autopic ?(.*)")
async def autopic(e):
    search = e.pattern_match.group(1)
    if not search:
        return await eor(e,'Heya Give me some Text ..')
    clls = returnpage(search)
    if len(clls)==0:
        return await eor(e,f'No Results found for `{search}`')
    num = random.randrange(0,len(clls)-1)
    page = clls[num]
    title = page['title']
    a = await eor(e,f' Got a Collection `{title}` related to your search !\nStarting Autopic !!')
    while True:
        animepp(page['href'])
        file = await ultroid_bot.upload_file("autopic.jpg")
        await ultroid_bot(functions.photos.UploadProfilePhotoRequest( file))
        os.system("rm -rf autopic.jpg")
        await asyncio.sleep(1100)
