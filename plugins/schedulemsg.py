# Ultroid - UserBot
# Copyright (C) 2021-2022 TeamUltroid
#
# This file is a part of < https://github.com/TeamUltroid/Ultroid/ >
# PLease read the GNU Affero General Public License in
# <https://www.github.com/TeamUltroid/Ultroid/blob/main/LICENSE/>.
"""
✘ Commands Available -

•`{i}schedule <text/reply to msg> <time>`
    In time u can use second as number, or like 1h or 1m
    eg. `{i}schedule Hello 100` It deliver msg after 100 sec.
    eg. `{i}schedule Hello 1h` It deliver msg after an hour.
"""
from datetime import timedelta

from pyUltroid.fns.admins import ban_time

from . import get_string, ultroid_cmd


@ultroid_cmd(pattern="schedule( (.*)|$)", fullsudo=True)
async def _(e):
    x = e.pattern_match.group(1).strip()
    xx = await e.get_reply_message()
    if x and not xx:
        y = x.split(" ")[-1]
        k = x.replace(y, "")
        if y.isdigit():
            await e.client.send_message(
                e.chat_id, k, schedule=timedelta(seconds=int(y))
            )
            await e.eor(get_string("schdl_1"), time=5)
        else:
            try:
                z = ban_time(y)
                await e.respond( k, schedule=z)
                await e.eor(get_string("schdl_1"), time=5)
            except BaseException:
                await e.eor(get_string("schdl_2"), time=5)
    elif xx and x:
        if x.isdigit():
            await e.client.send_message(
                e.chat_id, xx, schedule=timedelta(seconds=int(x))
            )
            await e.eor(get_string("schdl_1"), time=5)
        else:
            try:
                z = ban_time(x)
                await e.respond( xx, schedule=z)
                await e.eor(get_string("schdl_1"), time=5)
            except BaseException:
                await e.eor(get_string("schdl_2"), time=5)
    else:
        return await e.eor(get_string("schdl_2"), time=5)
