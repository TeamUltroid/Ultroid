# Ultroid Userbot
# <https://github.com/TeamUltroid/UltroidAddons/tree/main/imdb.py>

"""
Search movie details from IMDB

✘ Commands Available
• `{i}imdb <keyword>`
"""

from . import *


@ultroid_cmd(pattern="imdb ?(.*)")
async def imdb(e):
    m = await e.eor("`...`")
    movie_name = e.pattern_match.group(1)
    if not movie_name:
        return await m.eor("`Provide a movie name too`")
    try:
        mk = await e.client.inline_query("imdb", movie_name)
        await mk[0].click(e.chat_id)
        await m.delete()
    except IndexError:
        return await eor(m, "No Results Found...")
    except Exception as er:
        return await eor(m, str(er))
