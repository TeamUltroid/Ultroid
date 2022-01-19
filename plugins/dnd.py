# S
# O
# M
# E

# H
# E
# A
# D
# E
# R
# S

from . import ultroid_cmd

# from pyUltroid.functions.dnd_db import chat_in_dnd, add_dnd, rem_dnd, get_dnd_chats


@ultroid_cmd(pattern="dnd$", manager=True, admins_only=True, groups_only=True)
async def _(event):
    if chat_in_dnd(event.chat_id):
        return await event.eor("`Chat already in do not disturb mode.`")
    add_dnd(event.chat_id)
    await event.eor("`Do not disturb mode activated for this chat.`")


@ultroid_cmd(pattern="deldnd$", manager=True, admins_only=True, groups_only=True)
async def _(event):
    if not chat_in_dnd(event.chat_id):
        return await event.eor("`Chat is not in do not disturb mode.`")
    del_dnd(event.chat_id)
    await event.eor("`Do not disturb mode deactivated for this chat.`")
