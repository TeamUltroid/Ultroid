# Ultroid - UserBot
# Copyright (C) 2020 TeamUltroid
#
# This file is a part of < https://github.com/TeamUltroid/Ultroid/ >
# PLease read the GNU Affero General Public License in
# <https://www.github.com/TeamUltroid/Ultroid/blob/main/LICENSE/>.

"""
✘ Commands Available -

• `{i}setflood <integer>`
    Set flood limit in a chat.

• `{i}remflood`
    Remove flood limit from a chat.

• `{i}getflood`
    Get flood limit of a chat.
"""


from pyUltroid.functions.antiflood_db import get_flood_limit, rem_flood, set_flood


@ultroid_cmd(
    pattern="setflood ?(.*)",
)
async def set_flood(e):
    input = int(e.pattern_match.group(1))
    if not input:
        return await eor(e, "`What?`")
    m = setflood(e.chat_id, input)
    if m:
        return await eor(
            e, f"`Successfully Updated Antiflood Settings to {input} in this chat.`"
        )


@ultroid_cmd(
    pattern="remflood$",
)
async def remove_flood(e):
    hmm = rem_flood(e.chat_id)
    if hmm is True:
        return await eor(e, "Antiflood Settings Disabled>`")


@ultroid_cmd(
    pattern="getflood$",
)
async def get_flood(e):
    ok = get_flood_limit(e.chat_id)
    if ok:
        return await eor(e, f"`Flood limit for this chat is {ok}.`")
    else:
        await eor(e, "`No flood limits in this chat.`")


HELP.update({f"{__name__.split('.')[1]}": f"{__doc__.format(i=HNDLR)}"})
