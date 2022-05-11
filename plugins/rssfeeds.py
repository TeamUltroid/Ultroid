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
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from pyUltroid.dB.rssdb import add_rss, remove_rss

from . import async_searcher, get_string, udB, ultroid_cmd

cacheRss = {}


@ultroid_cmd(pattern="addrss( (.*)|$)")
async def Add_rss(ult):
    match = ult.pattern_match.group(1).strip()
    if not match:
        return await ult.eor(get_string("rss_1"))
    msg = await ult.eor(get_string("com_1"))
    try:
        cont = await async_searcher(match, re_content=True)
        parsed = feedparser.parse(cont)
        cacheRss.update({match: parsed.entries})
    except Exception as er:
        return await msg.edit(get_string("rss_2").format(er))
    format = None
    if ult.is_reply:
        reply = await ult.get_reply_message()
        if reply.text:
            format = reply.text
    add_rss(ult.chat_id, match, format)
    await msg.edit(get_string("rss_5"))


@ultroid_cmd(pattern="getrss$")
async def getrss(ult):
    get_ = get_rss_url(ult.chat_id)
    if not get_:
        return await ult.eor(get_string("rss_3"))
    form = "**RSS Urls added in this chat**\n"
    for url in get_:
        form += "\n" + url
    await ult.eor(form)


@ultroid_cmd(pattern="delrss$")
async def remove(ult):
    if not get_rss_url(ult.chat_id):
        return await ult.eor(get_string("rss_3"))
    remove_rss(ult.chat_id)
    await ult.eor(get_string("rss_4"))


async def PostRss():
    data = udB.get_key("RSSFEEDS")
    if not data:
        return
    for chat in data.keys():
        for url in data[chat].keys():
            data[chat][url]
            try:
                content = await async_searcher(url, re_content=True)
                parsed = feedparser.parse(content).entries
                cacheRss[url] = parsed
            #  for parse in parsed:
            #      await ultroid_bot.send_message(chat, )
            except Exception as er:
                LOGS.exception(er)


if udB.get_key("RSSFEEDS"):
    sched = AsyncIOScheduler()
    sched.add_job(PostRss, "interval", minutes=udB.get_key("RSSDELAY") or 30)
