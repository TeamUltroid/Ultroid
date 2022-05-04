# Ultroid - UserBot
# Copyright (C) 2021-2022 TeamUltroid
#
# This file is a part of < https://github.com/TeamUltroid/Ultroid/ >
# PLease read the GNU Affero General Public License in
# <https://www.github.com/TeamUltroid/Ultroid/blob/main/LICENSE/>.

"""
✘ Commands Available -

• `{i}addrss <rssurl> <optional-reply to custom format>`
   add rss feeds to be send in used chat.

• `{i}getrss`
"""

import feedparser
from apscheduler.asyncio import AsyncIOScheduler
from . import ultroid_cmd, get_string, async_searcher


@ultroid_cmd(pattern="addrss( (.*)|$)")
async def add_rss(ult):
    match = ult.pattern_match.group(1).strip()
    if not match:
        return await ult.eor(get_string("rss_1"))
    msg = await ult.eor(get_string("com_1"))
    try:
        cont = await async_searcher(match)
    except Exception as er:
        return await msg.edit(get_string("rss_2").format(er))

@ultroid_cmd(pattern="getrss$")
async def getrss(ult):
    pass
# TODO