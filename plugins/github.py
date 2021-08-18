# Ultroid - UserBot
# Copyright (C) 2021 TeamUltroid
#
# This file is a part of < https://github.com/TeamUltroid/Ultroid/ >
# PLease read the GNU Affero General Public License in
# <https://www.github.com/TeamUltroid/Ultroid/blob/main/LICENSE/>.
"""
✘ Commands Available -

• `{i}github <username>`
    Get full information of the users github profile.
"""
import requests

from . import *


@ultroid_cmd(
    pattern="github (.*)",
)
async def gitsearch(event):
    xx = await eor(event, get_string("com_2"))
    try:
        usrname = event.pattern_match.group(1)
    except BaseException:
        return await xx.edit("`Search for whom? Give me a user name!!`")
    url = f"https://api.github.com/users/{usrname}"
    ult = requests.get(url).json()
    try:
        uname = ult["login"]
        uid = ult["id"]
        upic = f"https://avatars.githubusercontent.com/u/{uid}"
        ulink = ult["html_url"]
        uacc = ult["name"]
        ucomp = ult["company"]
        ublog = ult["blog"]
        ulocation = ult["location"]
        ubio = ult["bio"]
        urepos = ult["public_repos"]
        ufollowers = ult["followers"]
        ufollowing = ult["following"]
    except BaseException:
        return await xx.edit("`No such user found...`")
    fullusr = f"""
**[GITHUB]({ulink})**

**Name** - {uacc}
**UserName** - {uname}
**ID** - {uid}
**Company** - {ucomp}
**Blog** - {ublog}
**Location** - {ulocation}
**Bio** - {ubio}
**Repos** - {urepos}
**Followers** - {ufollowers}
**Following** - {ufollowing}
"""
    await xx.delete()
    await event.reply(fullusr, file=upic)
