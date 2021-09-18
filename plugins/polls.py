# Ultroid - UserBot
# Copyright (C) 2021 TeamUltroid
#
# This file is a part of < https://github.com/TeamUltroid/Ultroid/ >
# PLease read the GNU Affero General Public License in
# <https://www.github.com/TeamUltroid/Ultroid/blob/main/LICENSE/>.
"""
✘ Commands Available -

• `{i}poll <question> ; <option> ; <option>`
    Get the Anonymous Poll with Given Options

• `{i}poll <question> ; <option> ; <option> | <type>`
    Get the poll specified with desired type!
    type should be any of  `public`,  `multiple` or `quiz`

• `{i}poll <question> ; <option> ; <option> | quiz_<answerno>`
    Get the quiz poll where answerno is the number of option which is correct

"""
from telethon.tl.types import InputMediaPoll, Poll, PollAnswer

from . import *


@ultroid_cmd(
    pattern="poll ?(.*)",
)
async def uri_poll(e):
    if not e.client._bot and e.is_private:
        return await eor(e, "`Use this in Group/Channel.`", time=15)
    match = e.pattern_match.group(1)
    if not match:
        return await eor(e, "`Give Proper Input...`", time=5)
    if ";" not in match:
        return await eor(e, "`Unable to Determine Options.`.", time=5)
    ques = match.split(";")[0]
    option = match.split(";")[1::]
    publ = None
    quizo = None
    karzo = None
    mpp = None
    if "|" in match:
        ptype = match.split(" | ")[1]
        option = match.split("|")[0].split(";")[1::]
        if "_" in ptype:
            karzo = [str(int(ptype.split("_")[1]) - 1).encode()]
            ptype = ptype.split("_")[0]
        if ptype not in ["public", "quiz", "multiple"]:
            return await eor(e, "`Invalid Poll Type...`", time=5)
        if ptype == "multiple":
            mpp = True
        elif ptype == "public":
            publ = True
        elif ptype == "quiz":
            quizo = True
    if len(option) <= 1:
        return await eor(e, "`Options Should be More than 1..`", time=5)
    m = await eor(e, "`Processing... `")
    OUT = [PollAnswer(option[on], str(on).encode()) for on in range(len(option))]
    await e.client.send_file(
        e.chat_id,
        InputMediaPoll(
            Poll(20, ques, OUT, multiple_choice=mpp, public_voters=publ, quiz=quizo),
            correct_answers=karzo,
        ),
    )
    await m.delete()
