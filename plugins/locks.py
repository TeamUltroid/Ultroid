from telethon import events, functions, types

from . import *

locks = [
    "sticker",
    "msgs",
    "media",
    "gif",
    "games",
    "inlines",
    "polls",
    "invites",
    "pin",
    "changeinfo",
]


@ultroid_cmd(
    pattern="(unl|l)ock",
    groups_only=True,
)
async def _(event):
    peer_id = event.chat_id
    ll = event.text.split(" ", maxsplit=1)
    cmd = ll[0]
    try:
        input = ll[1]
    except IndexError:
        return await eod(
            event, f"What do you want to {cmd}.\nDo `{HNDLR}listlocks`", time=5
        )
    if input not in locks:
        return await eod(event, f"Wrong type.\nDo `{HNDLR}listlocks`")
    if cmd == f"{hndlr}lock":
        lul = lucks(input)
        try:
            result = await event.client(
                functions.messages.EditChatDefaultBannedRightsRequest(
                    peer=peer_id, banned_rights=lul
                )
            )
            await eod(event, f"Locked {input}", time=5)
        except Exception as e:
            await eod(event, str(e), time=5)
    if cmd == f"{hndlr}unlock":
        lul = unlucks(input)
        try:
            result = await event.client(
                functions.messages.EditChatDefaultBannedRightsRequest(
                    peer=peer_id, banned_rights=lul
                )
            )
            await eod(event, f"Unocked {input}", time=5)
        except Exception as e:
            await eod(event, str(e), time=5)


@ultroid_cmd(
    pattern="listlocks$",
    groups_only=True,
)
async def _(event):
    res = "**•• Following is the API status of this group.**\n"
    current_chat = await event.get_chat()
    try:
        current_api_locks = current_chat.default_banned_rights
    except AttributeError as e:
        await eod(event, str(e))
    else:
        res += "    **msgs**:    `{}`\n".format(current_api_locks.send_messages)
        res += "    **media**:    `{}`\n".format(current_api_locks.send_media)
        res += "    **sticker**:    `{}`\n".format(current_api_locks.send_stickers)
        res += "    **gif**:    `{}`\n".format(current_api_locks.send_gifs)
        res += "    **games**:    `{}`\n".format(current_api_locks.send_games)
        res += "    **inlines**:    `{}`\n".format(current_api_locks.send_inline)
        res += "    **polls**:    `{}`\n".format(current_api_locks.send_polls)
        res += "    **invites**:    `{}`\n".format(current_api_locks.invite_users)
        res += "    **pins**:    `{}`\n".format(current_api_locks.pin_messages)
        res += "    **changeinfo**:    `{}`\n".format(current_api_locks.change_info)
        xx = res.replace("True", "Locked").replace("False", "Unlocked")
    await eor(event, xx)
