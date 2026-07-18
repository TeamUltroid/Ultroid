# Ultroid - UserBot
# Copyright (C) 2021-2026 TeamUltroid
#
# This file is a part of < https://github.com/TeamUltroid/Ultroid/ >
# PLease read the GNU Affero General Public License in
# <https://www.github.com/TeamUltroid/Ultroid/blob/main/LICENSE/>.

"""
✘ Commands Available -

• `{i}delayspam <count> <delay> <message>`
    Spam a message `count` times with `delay` seconds between each.
    Reply to a message to spam that message instead.

• `{i}stopspam`
    Stop an ongoing delayspam.

Examples:
  `{i}delayspam 5 2 Hello!`  — sends "Hello!" 5 times with 2s delay
  `{i}delayspam 10 1` (reply to a message) — forwards replied msg 10 times with 1s delay
"""

import asyncio

from . import HNDLR, eod, get_string, udB, ultroid_bot, ultroid_cmd

_spam_tasks = {}


@ultroid_cmd(pattern=r"delayspam( (.*)|$)")
async def delayspam_cmd(ult):
    args = ult.pattern_match.group(1).strip().split(None, 2)
    reply = await ult.get_reply_message()

    if len(args) < 2:
        return await ult.eor(
            f"`Usage: {HNDLR}delayspam <count> <delay> [message]\n"
            f"Or reply to a message: {HNDLR}delayspam <count> <delay>`",
            time=10,
        )

    try:
        count = int(args[0])
        delay = float(args[1])
    except ValueError:
        return await ult.eor("`count and delay must be numbers.`", time=5)

    if count > 200:
        return await ult.eor("`Max 200 repetitions allowed.`", time=5)
    if delay < 0.5:
        return await ult.eor("`Minimum delay is 0.5 seconds.`", time=5)

    text = args[2] if len(args) > 2 else None
    chat_id = ult.chat_id

    if not text and not reply:
        return await ult.eor(
            f"`Provide a message or reply to one.\nUsage: {HNDLR}delayspam <count> <delay> <text>`",
            time=8,
        )

    await ult.delete()

    task_key = f"{ult.sender_id}_{chat_id}"
    if task_key in _spam_tasks:
        _spam_tasks[task_key].cancel()

    async def _do_spam():
        for i in range(count):
            if task_key not in _spam_tasks:
                break
            try:
                if reply:
                    await ultroid_bot.send_message(
                        chat_id, reply.text or "", file=reply.media
                    )
                else:
                    await ultroid_bot.send_message(chat_id, text)
            except Exception:
                break
            await asyncio.sleep(delay)
        _spam_tasks.pop(task_key, None)

    task = asyncio.get_event_loop().create_task(_do_spam())
    _spam_tasks[task_key] = task


@ultroid_cmd(pattern="stopspam$")
async def stopspam_cmd(ult):
    task_key = f"{ult.sender_id}_{ult.chat_id}"
    if task_key in _spam_tasks:
        _spam_tasks.pop(task_key).cancel()
        await ult.eor("`Spam stopped.`", time=3)
    else:
        await ult.eor("`No active spam in this chat.`", time=3)
