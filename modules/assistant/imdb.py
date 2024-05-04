# Ultroid - UserBot
# Copyright (C) 2021-2024 TeamUltroid
#
# This file is a part of < https://github.com/TeamUltroid/Ultroid/ >
# PLease read the GNU Affero General Public License in
# <https://www.github.com/TeamUltroid/Ultroid/blob/main/LICENSE/>.
import hashlib
import re

import aiohttp
from telethon import Button

try:
    from PIL import Image
except ImportError:
    Image = None

from telethon import Button
from telethon.tl.types import InputWebDocument as wb

from . import callback, in_pattern, udB

# Define your OMDB API key http://www.omdbapi.com
OMDB_API_KEY = udB.get_key("OMDb_API")
imdbp = "https://graph.org/file/4bf06c344feb78b7e58e7.jpg"

LIST = {}
hash_to_url = {}


def generate_unique_id(url):
    hashed_id = hashlib.sha256(url.encode()).hexdigest()[:8]
    hash_to_url[hashed_id] = url
    return hashed_id

def get_original_url(hashed_id):
    return hash_to_url.get(hashed_id)


async def get_movie_data(search_term):
    parts = search_term.split("y=")
    movie_name = parts[0].strip()
    year = parts[1].strip() if len(parts) > 1 else None

    url = f"http://www.omdbapi.com/?apikey={OMDB_API_KEY}&t={movie_name}"
    if year:
        url += f"&y={year}"
    url += "&plot=full"

    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            if response.status == 200:
                data = await response.json()
                if data["Response"] == "True":
                    return data
    return None


@in_pattern("imdb", owner=False)
async def inline_imdb_command(event):
    try:
        movie_name = event.text.split(" ", maxsplit=1)[1]
        movie_data = await get_movie_data(movie_name)
        if movie_data:
            title = movie_data.get("Title", "")
            year = movie_data.get("Year", "")
            rated = movie_data.get("Rated", "")
            released = movie_data.get("Released", "")
            runtime = movie_data.get("Runtime", "")
            ratings = movie_data.get("Ratings", "")
            ratings_str = ", ".join([f"{rating['Source']}: `{rating['Value']}`" for rating in ratings])
            genre = movie_data.get("Genre", "")
            director = movie_data.get("Director", "")
            actors = movie_data.get("Actors", "")
            plot = movie_data.get("Plot", "")
            language = movie_data.get("Language", "")
            country = movie_data.get("Country", "")
            awards = movie_data.get("Awards", "")
            poster_url = movie_data.get("Poster", "")
            imdbRating = movie_data.get("imdbRating", "")
            imdbVotes = movie_data.get("imdbVotes", "")
            BoxOffice = movie_data.get("BoxOffice", "")
            movie_details = (
                f"**Tɪᴛʟᴇ:** {title}\n"
                f"**Yᴇᴀʀ:** {year}\n"
                f"**Rᴀᴛᴇᴅ:** `{rated}`\n"
                f"**Rᴇʟᴇᴀsᴇᴅ:** {released}\n"
                f"**Rᴜɴᴛɪᴍᴇ:** `{runtime}`\n"
                f"**Gᴇɴʀᴇ:** {genre}\n"
                f"**Dɪʀᴇᴄᴛᴏʀ:** {director}\n"
                f"**Aᴄᴛᴏʀs:** {actors}\n"
                f"**Pʟᴏᴛ:** {plot}\n"
                f"**Lᴀɴɢᴜᴀɢᴇ:** {language}\n"
                f"**Cᴏᴜɴᴛʀʏ:** {country}\n"
                f"**Aᴡᴀʀᴅs:** {awards}\n"
                f"**Rᴀᴛɪɴɢs:** {ratings_str}\n"
                f"**IMDʙ Rᴀᴛɪɴɢ:** `{imdbRating}`\n"
                f"**ɪᴍᴅʙVᴏᴛᴇs:** `{imdbVotes}`\n"
                f"**BᴏxOғғɪᴄᴇ:** `{BoxOffice}`"
            )
        else:
            await event.edit("Error: Unable to fetch movie data")
    except IndexError:
        indexarticle = event.builder.article(
            type="photo",
            include_media=True,
            title="Sᴇᴀʀᴄʜ Sᴏᴍᴇᴛʜɪɴɢ",
            thumb=wb(imdbp, 0, "image/jpeg", []),
            content=wb(imdbp, 0, "image/jpeg", []),
            text="**Iᴍᴅʙ Sᴇᴀʀᴄʜ**\n\nʏᴏᴜ ᴅɪᴅɴ'ᴛ sᴇᴀʀᴄʜ ᴀɴʏᴛʜɪɴɢ",
            buttons=[
                Button.switch_inline(
                    "Sᴇᴀʀᴄʜ",
                    query="imdb ",
                    same_peer=True,
                ),
                Button.switch_inline(
                    "Sᴇᴀʀᴄʜ Bʏ Yᴇᴀʀ",
                    query="imdb IF y=2024 ",
                    same_peer=True,
                ),
            ],
        )
        await event.answer([indexarticle])
        return

    plot_id = generate_unique_id(movie_details)

    thumb = wb(poster_url, 0, "image/jpeg", [])
    content = wb(poster_url, 0, "image/jpeg", [])
    txt = f"Title: {title}\nReleased: {released}\nCountry: {country}"
    button = [
        [Button.inline("Fᴜʟʟ Dᴇᴛᴀɪʟs", data=f"plot_button:{plot_id}")],
        [Button.switch_inline("Sᴇᴀʀᴄʜ Aɢᴀɪɴ", query="imdb ", same_peer=True)]
    ]

    article = await event.builder.article(
        type="photo",
        text=txt,
        title=f"Title: {title}",
        include_media=True,
        description=f"{released}\nimDB: {imdbRating}",
        link_preview=False,
        thumb=thumb,
        content=content,
        buttons=button,
    )
    LIST.update({plot_id: {"text": txt, "buttons": button}})
    await event.answer([article])


@callback(re.compile("plot_button:(.*)"), owner=False)
async def plot_button_clicked(event):
    plot_id = event.data.decode().split(":", 1)[1]
    details = get_original_url(plot_id)
    await event.edit(
        details, buttons=[[Button.inline("Back", data=f"imdb_back_button:{plot_id}")]]
    )


@callback(re.compile("imdb_back_button:(.*)"), owner=False)
async def back_button_clicked(event):
    plot_id = event.data.decode().split(":", 1)[1]
    if not LIST.get(plot_id):
        return await event.answer("Query Expired! Search again 🔍")
    await event.edit(**LIST[plot_id])
