from .. import fast_download, fetch, ultroid_cmd

# TODO: Complete


@ultroid_cmd("lexica($| (.*))")
async def search_lexica(event):
    query = event.pattern_match.group(1).strip()
    if not query:
        return await event.eor("`Provide query to search.`")
    limit = 5
    cont = await fetch(
        f"https://lexica.art/api/v1/search?q={query.replace(' ', '+')}", re_json=True
    )
    await event.reply(
        file=[
            (await fast_download(a))[0]
            for a in list(map(lambda d: d["src"], cont["images"][:limit]))
        ]
    )
    await event.try_delete()
