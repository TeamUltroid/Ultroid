# Ultroid - UserBot
# Copyright (C) 2020-2023 TeamUltroid
#
# This file is a part of < https://github.com/TeamUltroid/Ultroid/ >
# PLease read the GNU Affero General Public License in
# <https://github.com/TeamUltroid/pyUltroid/blob/main/LICENSE>.

import asyncio
import time
import uuid

from telethon import Button
from telethon.errors.rpcerrorlist import UserNotParticipantError
from telethon.tl import functions, types

from core.decorators import get_sudos,owner_and_sudos
try:
    from core import _ult_cache
except ImportError:
    _ult_cache = {}


def ban_time(time_str):
    """Simplify ban time from text"""
    if not any(time_str.endswith(unit) for unit in ("s", "m", "h", "d")):
        time_str += "s"
    unit = time_str[-1]
    time_int = time_str[:-1]
    if not time_int.isdigit():
        raise Exception("Invalid time amount specified.")
    to_return = 0
    if unit == "s":
        to_return = int(time.time() + int(time_int))
    elif unit == "m":
        to_return = int(time.time() + int(time_int) * 60)
    elif unit == "h":
        to_return = int(time.time() + int(time_int) * 60 * 60)
    elif unit == "d":
        to_return = int(time.time() + int(time_int) * 24 * 60 * 60)
    return to_return


# ------------------Admin Check--------------- #


async def _callback_check(event):
    id_ = str(uuid.uuid1()).split("-")[0]
    time.time()
    msg = await event.reply(
        "Click Below Button to prove self as Admin!",
        buttons=Button.inline("Click Me", f"cc_{id_}"),
    )
    if not _ult_cache.get("admin_callback"):
        _ult_cache.update({"admin_callback": {id_: None}})
    else:
        _ult_cache["admin_callback"].update({id_: None})
    while not _ult_cache["admin_callback"].get(id_):
        await asyncio.sleep(1)
    key = _ult_cache.get("admin_callback", {}).get(id_)
    del _ult_cache["admin_callback"][id_]
    return key


async def get_update_linked_chat(event):
    if _ult_cache.get("LINKED_CHATS") and _ult_cache["LINKED_CHATS"].get(event.chat_id):
        _ignore = _ult_cache["LINKED_CHATS"][event.chat_id]["linked_chat"]
    else:
        channel = await event.client(
            functions.channels.GetFullChannelRequest(event.chat_id)
        )
        _ignore = channel.full_chat.linked_chat_id
        if _ult_cache.get("LINKED_CHATS"):
            _ult_cache["LINKED_CHATS"].update({event.chat_id: {"linked_chat": _ignore}})
        else:
            _ult_cache.update(
                {"LINKED_CHATS": {event.chat_id: {"linked_chat": _ignore}}}
            )
    return _ignore


async def admin_check(event, require=None, silent: bool = False):
    if event.sender_id in owner_and_sudos():
        return True
    callback = None

    # for Anonymous Admin Support
    if (
        isinstance(event.sender, (types.Chat, types.Channel))
        and event.sender_id == event.chat_id
    ):
        if not require:
            return True
        callback = True
    if isinstance(event.sender, types.Channel):
        _ignore = await get_update_linked_chat(event)
        if _ignore and event.sender.id == _ignore:
            return False
        callback = True
    if callback:
        if silent:
            # work silently, same check is used for antiflood
            # and should not ask for Button Verification.
            return
        get_ = await _callback_check(event)
        if not get_:
            return
        user, perms = get_
        event._sender_id = user.id
        event._sender = user
    else:
        user = event.sender
        try:
            perms = await event.client.get_permissions(event.chat_id, user.id)
        except UserNotParticipantError:
            if not silent:
                await event.reply("You need to join this chat First!")
            return False
    if not perms.is_admin:
        if not silent:
            await event.eor("Only Admins can use this command!", time=8)
        return
    if require and not getattr(perms, require, False):
        if not silent:
            await event.eor(f"You are missing the right of `{require}`", time=8)
        return False
    return True

