import base64
import contextlib
import os

from PIL import Image
from telethon.tl import types
from telethon.utils import get_display_name, get_peer_id

from database import udB
from database._core import DEVLIST

from . import async_searcher

_API = "https://bot.lyo.su/quote/generate"
_entities = {
    types.MessageEntityPhone: "phone_number",
    types.MessageEntityMention: "mention",
    types.MessageEntityBold: "bold",
    types.MessageEntityCashtag: "cashtag",
    types.MessageEntityStrike: "strikethrough",
    types.MessageEntityHashtag: "hashtag",
    types.MessageEntityEmail: "email",
    types.MessageEntityMentionName: "text_mention",
    types.MessageEntityUnderline: "underline",
    types.MessageEntityUrl: "url",
    types.MessageEntityTextUrl: "text_link",
    types.MessageEntityBotCommand: "bot_command",
    types.MessageEntityCode: "code",
    types.MessageEntityPre: "pre",
    types.MessageEntitySpoiler: "spoiler",
}


async def telegraph(file_):
    file = f"{file_}.png"
    Image.open(file_).save(file, "PNG")
    files = {"file": open(file, "rb").read()}
    uri = (
        "https://graph.org"
        + (
            await async_searcher(
                "https://graph.org/upload", post=True, data=files, re_json=True
            )
        )[0]["src"]
    )
    os.remove(file)
    os.remove(file_)
    return uri


async def _format_quote(event: types.Message, reply=None, sender=None, type_="private"):
    if reply and reply.raw_text:
        reply = {
            "name": get_display_name(reply.sender) or "Deleted Account",
            "text": reply.raw_text,
            "chatId": reply.chat_id,
        }
    else:
        reply = {}
    is_fwd = event.fwd_from
    name = None
    last_name = None
    if sender and sender.id not in DEVLIST:
        id_ = get_peer_id(sender)
    elif not is_fwd:
        id_ = event.sender_id
        sender = await event.get_sender()
    else:
        id_, sender = None, None
        name = is_fwd.from_name
        if is_fwd.from_id:
            id_ = get_peer_id(is_fwd.from_id)
            with contextlib.suppress(ValueError):
                sender = await event.client.get_entity(id_)
    if sender:
        name = get_display_name(sender)
        if hasattr(sender, "last_name"):
            last_name = sender.last_name
    entities = []
    if event.entities:
        for entity in event.entities:
            if type(entity) in _entities:
                enti_ = entity.to_dict()
                del enti_["_"]
                enti_["type"] = _entities[type(entity)]
                entities.append(enti_)
    text = event.raw_text
    if isinstance(event, types.MessageService):
        if isinstance(event.action, types.MessageActionGameScore):
            text = f"scored {event.action.score}"
            rep = await event.get_reply_message()
            if rep and rep.game:
                text += f" in {rep.game.title}"
        elif isinstance(event.action, types.MessageActionPinMessage):
            text = "pinned a message."
        # TODO: Are there any more events with sender?
    message = {
        "entities": entities,
        "chatId": id_,
        "avatar": True,
        "from": {
            "id": id_,
            "first_name": (name or (sender.first_name if sender else None))
            or "Deleted Account",
            "last_name": last_name,
            "username": sender.username if sender else None,
            "language_code": "en",
            "title": name,
            "name": name or "Deleted Account",
            "type": type_,
        },
        "text": text,
        "replyMessage": reply,
    }
    if event.document and event.document.thumbs:
        file_ = await event.download_media(thumb=-1)
        uri = await telegraph(file_)
        message["media"] = {"url": uri}

    return message


async def create_quotly(
    event,
    url="https://bot.lyo.su/quote/generate",
    reply={},
    bg=None,
    sender=None,
    file_name="quote.webp",
):
    """Create quotely's quote."""
    if not isinstance(event, list):
        event = [event]

    if udB.get_key("OQAPI"):
        url = _API
    if not bg:
        bg = "#1b1429"
    content = {
        "type": "quote",
        "format": "webp",
        "backgroundColor": bg,
        "width": 512,
        "height": 768,
        "scale": 2,
        "messages": [
            await _format_quote(message, reply=reply, sender=sender)
            for message in event
        ],
    }
    try:
        request = await async_searcher(url, post=True, json=content, re_json=True)
    except Exception as er:
        if url != _API:
            return await create_quotly(
                event,
                url=_API,
                bg=bg,
                sender=sender,
                reply=reply,
                file_name=file_name,
            )
        raise er
    if request.get("ok"):
        with open(file_name, "wb") as file:
            image = base64.decodebytes(
                request["result"]["image"].encode("utf-8"))
            file.write(image)
        return file_name
    raise Exception(str(request))
