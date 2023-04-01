from . import in_pattern, get_string, async_searcher, asst, Button
from telethon.tl.types import InputWebDocument as wb

PISTON_URI = "https://emkc.org/api/v2/piston/"
PISTON_LANGS = {}


@in_pattern("run", owner=True, button={"Piston Eval": "run javascript console.log('Hello Ultroid');"})
async def piston_run(event):
    try:
        lang = event.text.split()[1]
        code = event.text.split(maxsplit=2)[2]
    except IndexError:
        result = await event.builder.article(
            title="Bad Query",
            description="Usage: [Language] [code]",
            thumb=wb(
                "https://graph.org/file/e33c57fc5f1044547e4d8.jpg", 0, "image/jpeg", []
            ),
            text=f'**Inline Usage**\n\n`@{asst.me.username} run python print("hello world")`\n\n[Language List](https://graph.org/Ultroid-09-01-6)',
        )
        return await event.answer([result])
    if not PISTON_LANGS:
        se = await async_searcher(f"{PISTON_URI}runtimes", re_json=True)
        PISTON_LANGS.update({lang.pop("language"): lang for lang in se})
    if lang in PISTON_LANGS.keys():
        version = PISTON_LANGS[lang]["version"]
    else:
        result = await event.builder.article(
            title="Unsupported Language",
            description="Usage: [Language] [code]",
            thumb=wb(
                "https://graph.org/file/e33c57fc5f1044547e4d8.jpg", 0, "image/jpeg", []
            ),
            text=f'**Inline Usage**\n\n`@{asst.me.username} run python print("hello world")`\n\n[Language List](https://graph.org/Ultroid-09-01-6)',
        )
        return await event.answer([result])
    output = await async_searcher(
        f"{PISTON_URI}execute",
        post=True,
        json={
            "language": lang,
            "version": version,
            "files": [{"content": code}],
        },
        re_json=True,
    )

    output = output["run"]["output"] or get_string("instu_4")
    if len(output) > 3000:
        output = f"{output[:3000]}..."
    result = await event.builder.article(
        title="Result",
        description=output,
        text=f"• **Language:**\n`{lang}`\n\n• **Code:**\n`{code}`\n\n• **Result:**\n`{output}`",
        thumb=wb(
            "https://graph.org/file/871ee4a481f58117dccc4.jpg", 0, "image/jpeg", []
        ),
        buttons=Button.switch_inline("Fork", query=event.text, same_peer=True),
    )
    await event.answer([result], switch_pm="• Piston •", switch_pm_param="start")