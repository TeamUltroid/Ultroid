# " Made by @e3ris for Ultroid. "
# < https://github.com/TeamUltroid/Ultroid >
# idea: https://t.me/TelethonChat/256160


"""
✘ To Search Messages in chat easily :)

✘ **CMD** :
>> {i}search (some_text)
>> {i}search -r (some_text) : 10
    »» To search in Reverse order.

✘ **Examples** :
   •  `{i}search Ultroid`
   •  `{i}search -r Heroku : 10`
"""

from . import ultroid_cmd


@ultroid_cmd(pattern="search( -r|) ?(.*)")
async def searcher(e):
    eris = await e.eor("`Working..`")
    args = e.pattern_match.group(2)
    limit = 5
    if not args or len(args) < 2:
        await eris.eor("Invalid argument!, Try again")
        return

    if ":" in args:
        args, limit = args.split(":", 1)
    try:
        limit = int(limit)
    except BaseException:
        limit = 5

    limit = 99 if limit > 99 else limit
    text, c = "", 0
    async for msg in e.client.iter_messages(
        e.chat_id,
        search=args.strip(),
        limit=limit,
        reverse=bool(e.pattern_match.group(1)),
    ):
        text += f" [»» {msg.id}](t.me/c/{e.chat.id}/{msg.id})\n"
        c += 1

    txt = (
        f"**Results for :**  `{args}` \n\n{text}"
        if c > 0
        else f"**No Results for :**  `{args}`"
    )
    await eris.edit(txt)
