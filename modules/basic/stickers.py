# Ultroid - UserBot
# Copyright (C) 2021-2022 TeamUltroid
#
# This file is a part of < https://github.com/TeamUltroid/Ultroid/ >
# PLease read the GNU Affero General Public License in
# <https://www.github.com/TeamUltroid/Ultroid/blob/main/LICENSE/>.

import contextlib
import random
from secrets import token_urlsafe

from telethon import errors
from telethon.errors.rpcerrorlist import StickersetInvalidError
from telethon.tl.functions.messages import GetStickerSetRequest as GetSticker
from telethon.tl.functions.messages import UploadMediaRequest
from telethon.tl.functions.stickers import AddStickerToSetRequest as AddSticker
from telethon.tl.functions.stickers import CreateStickerSetRequest
from telethon.tl.types import (
    DocumentAttributeSticker,
    InputPeerSelf,
    InputStickerSetEmpty,
)
from telethon.errors import StickersetInvalidError
from telethon.tl.types import InputStickerSetItem as SetItem
from telethon.tl.types import InputStickerSetShortName, User
from telethon.utils import get_display_name, get_extension, get_input_document

from core.remote import rm
from utilities.converter import resize_photo_sticker

from .. import LOGS, asst, fetch, udB, ultroid_cmd


async def packExists(packId):
    source = await fetch(f"https://t.me/addstickers/{packId}")
    return (
        not b"""<div class="tgme_page_description">
  A <strong>Telegram</strong> user has created the <strong>Sticker&nbsp;Set</strong>.
</div>"""
        in source
    )


async def GetUniquePackName():
    packName = f"{token_urlsafe(random.randint(4, 6))}_by_{asst.me.username}"
    return await GetUniquePackName() if await packExists(packName) else packName


# TODO: simplify if possible


def getName(sender, packType: str):
    title = f"{get_display_name(sender)}'s Kang Pack"
    if packType != "static":
        title += f" ({packType.capitalize()})"
    return title


async def AddToNewPack(packType, file, emoji, sender_id, title: str):
    sn = await GetUniquePackName()
    return await asst(
        CreateStickerSetRequest(
            user_id=sender_id,
            title=title,
            short_name=sn,
            stickers=[SetItem(file, emoji=emoji)],
            videos=packType == "video",
            animated=packType == "animated",
            software="@TeamUltroid",
        )
    )


@ultroid_cmd(pattern="kang", manager=True)
async def kang_func(ult):
    sender = await ult.get_sender()
    if not isinstance(sender, User):
        return
    if not ult.is_reply:
        return await ult.eor("`Reply to a message..`", time=5)
    reply = await ult.get_reply_message()
    type_, dl = "static", None
    try:
        emoji = ult.text.split(maxsplit=1)[1]
    except IndexError:
        emoji = None
    if reply.sticker:
        file = get_input_document(reply.sticker)
        if not emoji:
            emoji = reply.file.emoji
        name = reply.file.name
        ext = get_extension(reply.media)
        attr = list(
            filter(
                lambda prop: isinstance(prop, DocumentAttributeSticker),
                reply.document.attributes,
            )
        )
        inPack = attr and not isinstance(attr[0].stickerset, InputStickerSetEmpty)
        with contextlib.suppress(KeyError):
            type_ = {".webm": "video", ".tgs": "animated"}[ext]
        if type_ or not inPack:
            dl = await reply.download_media()
    elif reply.photo:
        dl = await reply.download_media()
        name = "sticker.webp"
        image = resize_photo_sticker(dl)
        image.save(name, "WEBP")
    elif reply.text:
        with rm.get("quotly", helper=True, dispose=True) as quotly:
            dl = await quotly.create_quotly(reply)
    else:
        return await ult.eor("`Reply to sticker or text to add it in your pack...`")
    if not emoji:
        emoji = "🏵"
    if dl:
        upl = await asst.upload_file(dl)
        file = get_input_document(await asst(UploadMediaRequest(InputPeerSelf(), upl)))
    get_ = udB.get_key("STICKERS") or {}
    title = getName(sender, type_)
    if not get_.get(ult.sender_id) or not get_.get(ult.sender_id, {}).get(type_):
        try:
            pack = await AddToNewPack(type_, file, emoji, sender.id, title)
        except Exception as er:
            return await ult.eor(str(er))
        sn = pack.set.short_name
        if not get_.get(ult.sender_id):
            get_.update({ult.sender_id: {type_: [sn]}})
        else:
            get_[ult.sender_id].update({type_: [sn]})
        udB.set_key("STICKERS", get_)
        return await ult.reply(
            f"**Kanged Successfully!\nEmoji :** {emoji}\n**Link :** [Click Here](https://t.me/addstickers/{sn})"
        )
    name = get_[ult.sender_id][type_][-1]
    try:
        await asst(GetSticker(InputStickerSetShortName(name), hash=0))
    except StickersetInvalidError:
        get_[ult.sender_id][type_].remove(name)
    try:
        await asst(
            AddSticker(InputStickerSetShortName(name), SetItem(file, emoji=emoji))
        )
    except (errors.StickerpackStickersTooMuchError, errors.StickersTooMuchError):
        try:
            pack = await AddToNewPack(type_, file, emoji, sender.id, title)
        except Exception as er:
            return await ult.eor(str(er))
        get_[ult.sender_id][type_].append(pack.set.short_name)
        udB.set_key("STICKERS", get_)
        return await ult.reply(
            f"**Created New Kang Pack!\nEmoji :** {emoji}\n**Link :** [Click Here](https://t.me/addstickers/{sn})"
        )
    except Exception as er:
        LOGS.exception(er)
        return await ult.reply(str(er))
    await ult.reply(
        f"Sticker Added to Pack Successfully\n**Link :** [Click Here](https://t.me/addstickers/{name})"
    )


@ultroid_cmd(pattern="listpack", manager=True)
async def do_magic(ult):
    ko = udB.get_key("STICKERS") or {}
    if not ko.get(ult.sender_id):
        return await ult.reply("No Sticker Pack Found!")
    al_ = []
    ul = ko[ult.sender_id]
    for _ in ul.keys():
        al_.extend(ul[_])
    msg = "• **Stickers Owned by You!**\n\n"
    for _ in al_:
        try:
            pack = await ult.client(GetSticker(InputStickerSetShortName(_), hash=0))
            msg += f"• [{pack.set.title}](https://t.me/addstickers/{_})\n"
        except StickersetInvalidError:
            for type_ in ["animated", "video", "static"]:
                if ul.get(type_) and _ in ul[type_]:
                    ul[type_].remove(_)
            udB.set_key("STICKERS", ko)
    await ult.reply(msg)
