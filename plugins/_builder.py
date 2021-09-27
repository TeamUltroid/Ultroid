from . import *
from telethon.utils import resolve_bot_file_id

@in_pattern("stf(.*)", owner=True)
async def ibuild(e):
    n = e.pattern_match.group(1)
    builder = e.builder
    ok = STUFF.get(int(n))
    txt = ok.get("msg") or None
    pic = ok.get("media") or None
    btn = ok.get("button") or None
    if pic:
        try:
            if ".jpg" in pic:
                results = [await builder.photo(pic, text=txt, buttons=btn, link_preview=False)]
            else:
                _pic = resolve_bot_file_id(pic)
                results = [
                    await builder.document(
                        _pic,
                        title="Ultroid Op",
                        text=txt,
                        description="@TheUltroid",
                        buttons=btn,
                        link_preview=False
                    )
                ]
            return await e.answer(results)
        except Exception as er:
            LOGS.exception(er)
    result = [
        await builder.article("Ultroid Op", text=txt, link_preview=False, buttons=btn)
    ]
    await e.answer(result)

async def something(e, msg, media, button):
    num = len(STUFF) +1 
    STUFF.update({num: {"msg": msg, "media": media, "button": button}})
    try:
        res = await e.client.inline_query(asst.me.username, f"stf{num}")
        return await res[0].click(e.chat_id, reply_to=e, hide_via=True, silent=True)
    except Exception as er:
        LOGS.info(er)
