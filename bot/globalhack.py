from core import ultroid_bot, udB
from telethon.events import NewMessage
from telethon.tl.types import MessageEntityUrl
from telethon.errors import MessageNotModifiedError

@ultroid_bot.on(
    NewMessage(
        outgoing=True,
        func=lambda e: e.message and not event.text.startswith(HNDLR) and (True in [isinstance(_, MessageEntityUrl) for _ in e.message.entities),
    ),
)
async def link_preview_hek(event):
    try:
        await event.edit(event.text, link_preview=udB.get_key("GLOBAL_LINK_PREVIEW"))
    except MessageNotModifiedError:
        pass
