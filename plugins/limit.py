# SADBOY

"""
✘ Commands Available -

• `{i}limit`
   Periksa Anda terbatas atau tidak!
"""

from telethon import events
from telethon.errors.rpcerrorlist import YouBlockedUserError

from . import ultroid_cmd


@ultroid_cmd(pattern="limit$")
async def demn(ult):
    chat = "@SpamBot"
    msg = await ult.eor("Memeriksa Apakah Anda Terbatas...")
    async with ult.client.conversation(chat) as conv:
        try:
            response = conv.wait_event(
                events.NewMessage(incoming=True, from_users=178220800)
            )
            await conv.send_message("/start")
            response = await response
            await ult.client.send_read_acknowledge(chat)
        except YouBlockedUserError:
            await msg.edit("Silahkan Buka Blokir @SpamBot ")
            return
        await msg.edit(f"~ {response.message.message}")
