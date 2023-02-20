import re
from random import shuffle

from bs4 import BeautifulSoup
from utilities.helper import async_searcher


async def unsplash(query, limit=None, shuf=True):
    query = query.replace(" ", "-")
    link = f"https://unsplash.com/s/photos/{query}"
    extra = await async_searcher(link, re_content=True)
    res = BeautifulSoup(extra, "html.parser", from_encoding="utf-8")
    all_ = res.find_all("img", srcset=re.compile("images.unsplash.com/photo"))
    if shuf:
        shuffle(all_)
    return list(map(lambda e: e["src"], all_[:limit]))
