# Ultroid - UserBot
# Copyright (C) 2020 TeamUltroid
#
# This file is a part of < https://github.com/TeamUltroid/Ultroid/ >
# PLease read the GNU Affero General Public License in
# <https://www.github.com/TeamUltroid/Ultroid/blob/main/LICENSE/>.

"""
✘ Commands Available -

• `{i}del <reply to message>`
    Delete the replied message.

• `{i}edit <new message>`
    Edit your last message or replied msg.

• `{i}copy <reply to message>`
    Copy replied message / media.

• `{i}reply`
    Reply the last sent msg to replied user.
"""

from . import *


@ultroid_cmd(
    pattern="del$",
)
async def delete_it(delme):
    msg_src = await delme.get_reply_message()
    if delme.reply_to_msg_id:
        try:
            await msg_src.delete()
            await delme.delete()
        except BaseException:
            await eod(
                delme,
                f"Couldn't delete the message.\n\n**ERROR:**\n`{str(e)}`",
                time=5,
            )


@ultroid_cmd(
    pattern="copy$",
)
async def copy(e):
    reply = await e.get_reply_message()
    if reply:
        if reply.text and not reply.media:
            await eor(e, reply.text)
        else:
            await reply.reply(reply)
            if e.sender_id == ultroid_bot.uid:
                await e.delete()
    else:
        await eod(e, "`Reply To any message`")


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
        async for message in ultroid_bot.iter_messages(chat, ultroid_bot.uid):
            if i == 2:
                await message.edit(string)
                await edit.delete()
                break
            i = i + 1


@ultroid_cmd(
    pattern="reply$",
)
async def _(e):
    repl = await e.get_reply_message()
    if repl:
        async for p in e.client.iter_messages(
            e.chat_id, from_user=ultroid_bot.uid, limit=1
        ):
            await repl.reply(p)
        await e.delete()
        await p.delete()
    else:
        await eod(e, "`Reply To any message`")


HELP.update({f"{__name__.split('.')[1]}": f"{__doc__.format(i=HNDLR)}"})
