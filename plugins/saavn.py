import os

from telethon.tl.types import DocumentAttributeAudio, InputWebDocument as wb

from database._core import InlinePlugin
from .. import fetch, fast_download, ultroid_cmd, in_pattern, Button, DocumentAttributeAudio as Audio


@ultroid_cmd(
    pattern="saavn( (.*)|$)",
)
async def siesace(e):
    song = e.pattern_match.group(1).strip()
    if not song:
        return await e.eor("`Give me Something to Search", time=5)
    eve = await e.eor(f"`Searching for {song} on Saavn...`")
    try:
        data = (await saavn_search(song))[0]
    except IndexError:
        return await eve.eor(f"`{song} not found on saavn.`")
    try:
        title = data["title"]
        url = data["url"]
        img = data["image"]
        duration = data["duration"]
        performer = data["artists"]
    except KeyError:
        return await eve.eor("`Something went wrong.`")
    song, _ = await fast_download(url, filename=f"{title}.m4a")
    thumb, _ = await fast_download(img, filename=f"{title}.jpg")
    song, _ = await e.client.fast_uploader(song, to_delete=True)
    await eve.eor(
        file=song,
        text=f"`{title}`\n`From Saavn`",
        attributes=[
            DocumentAttributeAudio(
                duration=int(duration),
                title=title,
                performer=performer,
            )
        ],
        supports_streaming=True,
        thumb=thumb,
    )
    await eve.delete()
    os.remove(thumb)


async def saavn_search(query: str):
    try:
        data = await fetch(
            url=f"https://saavn-api.vercel.app/search/{query.replace(' ', '%20')}",
            re_json=True,
        )
    except BaseException:
        data = None
    return data


_savn_cache = {}


@in_pattern("saavn", owner=True)
async def savn_s(event):
    try:
        query = event.text.split(maxsplit=1)[1].lower()
    except IndexError:
        return await event.answer(
            [], switch_pm="Enter Query to search 🔍", switch_pm_param="start"
        )
    if query in _savn_cache:
        return await event.answer(
            _savn_cache[query],
            switch_pm=f"Showing Results for {query}",
            switch_pm_param="start",
        )
    results = await saavn_search(query)
    swi = "🎵 Saavn Search" if results else "No Results Found!"
    res = []
    for song in results:
        thumb = wb(song["image"], 0, "image/jpeg", [])
        text = f"• **Title :** {song['title']}"
        text += f"\n• **Year :** {song['year']}"
        text += f"\n• **Lang :** {song['language']}"
        text += f"\n• **Artist :** {song['artists']}"
        text += f"\n• **Release Date :** {song['release_date']}"
        res.append(
            await event.builder.article(
                title=song["title"],
                description=song["artists"],
                type="audio",
                text=text,
                include_media=True,
                buttons=Button.switch_inline(
                    "Search Again 🔍", query="saavn", same_peer=True
                ),
                thumb=thumb,
                content=wb(
                    song["url"],
                    0,
                    "audio/mp4",
                    [
                        Audio(
                            title=song["title"],
                            duration=int(song["duration"]),
                            performer=song["artists"],
                        )
                    ],
                ),
            )
        )
    await event.answer(res, switch_pm=swi, switch_pm_param="start")
    _savn_cache.update({query: res})

InlinePlugin.update({"Sᴀᴀᴠɴ sᴇᴀʀᴄʜ": "saavn"})
