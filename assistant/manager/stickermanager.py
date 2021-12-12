from io import BytesIO
from pyUltroid.functions.tools import resize_photo
from pyUltroid.functions.misc import create_quotly
from . import asst_cmd, udB
from telethon.utils import get_input_document, get_display_name
from telethon.tl.functions.messages import UploadMediaRequest
from telethon.tl.types import InputStickerSetItem as SetItem
from telethon.tl.functions.stickers import CreateStickerSetRequest

@asst_cmd(
    pattern="kang",
)
async def kang_cmd(ult):
    if not ult.is_reply:
        return await ult.eor("`Reply to a sticker/photo..`", time=5)
    reply = await ult.get_reply_message()
    animated, dl = None, None
    emoji = "🏵"
    if reply.sticker:
        file = reply.sticker
        emoji = reply.file.emoji
        if reply.file.name.endswith(".tgs"):
            animated = True
            dl = await reply.download_media()
    elif reply.photo:
        dl = BytesIO()
        await reply.download_media(dl)
        image = await resize_photo(dl)
        dl.name = "sticker.png"
        image.save(dl, "PNG")
        dl = "sticker.png"
    elif reply.text:
        dl = await create_quotly(reply)
    else:
        return await ult.eor("`Reply to sticker or text to add it in your pack...`")
    if dl:
        upl = await ult.client.upload_file(dl)
        file = await ult.client(UploadMediaRequest(types.InputPeerSelf(), upl))
    get_ = udB.get_key("STICKERS") or {}
    sender = await ult.get_sender()
    if not get_.get(ult.sender_id):
        sn = f"ult_{ult.sender_id}"
        title = f"{get_display_name(sender)}'s Kang Pack"
        if animated:
          sn += "_anim"
          title += " (Animated)"
        sn += f"_by_{asst.me.username}"
        
      # ait ult.client(CreateStickerSetRequest(user_id=sender.id, title=title, short_name=sn, stickers=[SetItem(file)], animated=animated))
        
