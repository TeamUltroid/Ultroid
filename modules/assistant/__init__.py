from telethon.tl.types import InputWebDocument

from core import asst
from core.decorators._assistant import asst_cmd, callback, in_pattern

from .. import Button, inline_pic

def get_back_button(name):
    return [Button.inline("« Bᴀᴄᴋ", data=f"{name}")]


@in_pattern(owner=True, func=lambda x: not x.text)
async def inline_alive(o):
    TLINK = inline_pic() or "https://graph.org/file/74d6259983e0642923fdb.jpg"
    MSG = "• **Ultroid Userbot •**"
    WEB0 = InputWebDocument(
        "https://graph.org/file/acd4f5d61369f74c5e7a7.jpg", 0, "image/jpg", []
    )
    RES = [
        await o.builder.article(
            type="photo",
            text=MSG,
            include_media=True,
            buttons=[
                [
                    Button.url(
                        "• Repo •", url="https://github.com/TeamUltroid/Ultroid"
                    ),
                    Button.url("• Support •", url="t.me/UltroidSupportChat"),
                ],
            ],
            title="Ultroid Userbot",
            description="Userbot | Telethon",
            url=TLINK,
            thumb=WEB0,
            content=InputWebDocument(TLINK, 0, "image/jpg", []),
        )
    ]
    await o.answer(
        RES,
        private=True,
        cache_time=300,
        switch_pm="👥 ULTROID PORTAL",
        switch_pm_param="start",
    )
