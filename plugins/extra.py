# Ultroid - UserBot
# Copyright (C) 2021-2022 TeamUltroid
#
# This file is a part of < https://github.com/TeamUltroid/Ultroid/ >
# PLease read the GNU Affero General Public License in
# <https://www.github.com/TeamUltroid/Ultroid/blob/main/LICENSE/>.

from . import get_help

__doc__ = get_help("extra")

import asyncio

from . import get_string, ultroid_cmd


@ultroid_cmd(
    pattern="del$",
    manager=True,
)
async def delete_it(delme):
    msg_src = await delme.get_reply_message()
    if not msg_src:
        return
    await msg_src.try_delete()
    await delme.try_delete()


@ultroid_cmd(
    pattern="copy$",
)
async def copy(e):
    reply = await e.get_reply_message()
    if reply:
        await reply.reply(reply)
        return await e.try_delete()
    await e.eor(get_string("ex_1"), time=5)


@ultroid_cmd(
    pattern="edit",
)
async def editer(edit):
    message = edit.text
    chat = await edit.get_input_chat()
    string = str(message[6:])
    reply = await edit.get_reply_message()
    if reply and reply.text:
        try:
            await reply.edit(string)
            await edit.delete()
        except BaseException:
            pass
    else:
        i = 1
        async for message in edit.client.iter_messages(chat, from_user="me", limit=2):
            if i == 2:
                await message.edit(string)
                await edit.delete()
                break
            i += 1


@ultroid_cmd(
    pattern="reply$",
)
async def _(e):
    if e.reply_to_msg_id:
        chat = e.chat_id
        try:
            msg = (await e.client.get_messages(e.chat_id, limit=1, max_id=e.id))[0]
        except IndexError:
            return await e.eor(
                "`You have previously sent no message to reply again...`", time=5
            )
        except BaseException as er:
            return await e.eor(f"**ERROR:** `{er}`")
        await asyncio.wait(
            [
                e.client.delete_messages(chat, [e.id, msg.id]),
                e.client.send_message(chat, msg, reply_to=e.reply_to_msg_id),
            ]
        )
    else:
        await e.try_delete()
