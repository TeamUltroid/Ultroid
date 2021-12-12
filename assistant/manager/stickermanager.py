from PIL import Image
from pyUltroid.functions.misc import create_quotly
from telethon import errors
from telethon.tl.functions.messages import UploadMediaRequest
from telethon.tl.functions.stickers import AddStickerToSetRequest as AddSticker
from telethon.tl.functions.stickers import CreateStickerSetRequest
from telethon.tl.types import InputPeerSelf
from telethon.tl.types import InputStickerSetItem as SetItem
from telethon.tl.types import InputStickerSetShortName, User
from telethon.utils import get_display_name, get_input_document

from . import LOGS, asst, asst_cmd, udB


@asst_cmd(
    pattern="kang",
)
async def kang_cmd(ult):
    sender = await ult.get_sender()
    if not isinstance(sender, User):
        return
    if not ult.is_reply:
        return await ult.eor("`Reply to a sticker/photo..`", time=5)
    reply = await ult.get_reply_message()
    animated, dl = None, None
    emoji = "🏵"
    if reply.sticker:
        file = get_input_document(reply.sticker)
        emoji = reply.file.emoji
        if reply.file.name.endswith(".tgs"):
            animated = True
            dl = await reply.download_media()
    elif reply.photo:
        file = await reply.download_media()
        name = "sticker.webp"
        image = Image.open(file)
        image.save(name, "WEBP")
    elif reply.text:
        dl = await create_quotly(reply)
    else:
        return await ult.eor("`Reply to sticker or text to add it in your pack...`")
    if dl:
        upl = await ult.client.upload_file(dl)
        file = get_input_document(
            await ult.client(UploadMediaRequest(InputPeerSelf(), upl))
        )
    get_ = udB.get_key("STICKERS") or {}
    type_ = "static" if not animated else "anim"
    if not get_.get(ult.sender_id) or not get_.get(ult.sender_id, {}).get(type_):
        sn = f"ult_{ult.sender_id}"
        title = f"{get_display_name(sender)}'s Kang Pack"
        if animated:
            type_ = "anim"
            sn += "_anim"
            title += " (Animated)"
        sn += f"_by_{asst.me.username}"
        try:
            pack = await ult.client(
                CreateStickerSetRequest(
                    user_id=sender.id,
                    title=title,
                    short_name=sn,
                    stickers=[SetItem(file, emoji=emoji)],
                    animated=animated,
                )
            )
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
        await asst(
            AddSticker(InputStickerSetShortName(name), SetItem(file, emoji=emoji))
        )
    except (errors.StickerpackStickersTooMuchError, errors.StickersTooMuchError):
        sn = f"ult{ult.sender_id}_{ult.id}"
        title = f"{get_display_name(sender)}'s Kang Pack"
        if animated:
            sn += "_anim"
            title += " (Animated)"
        sn += f"_by_{asst.me.username}"
        try:
            pack = await ult.client(
                CreateStickerSetRequest(
                    user_id=sender.id,
                    title=title,
                    short_name=sn,
                    stickers=[SetItem(file, emoji=emoji)],
                    animated=animated,
                )
            )
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
