from core import HNDLR, udB, ultroid_bot
from telethon.errors import MessageNotModifiedError
from telethon.events import NewMessage
from telethon.tl.types import MessageEntityUrl


@ultroid_bot.on(
    NewMessage(
        outgoing=True,
        func=lambda e: e.message and not e.text.startswith(HNDLR) and (
            any([isinstance(_, MessageEntityUrl) for _ in e.message.entities])),
    ),
)
async def link_preview_hek(event):
    try:
        await event.edit(event.text, link_preview=udB.get_key("GLOBAL_LINK_PREVIEW"))
    except MessageNotModifiedError:
        pass
