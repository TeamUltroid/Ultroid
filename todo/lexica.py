# Ultroid - UserBot
# Copyright (C) 2020 TeamUltroid
#
# This file is a part of < https://github.com/TeamUltroid/Ultroid/ >
# PLease read the GNU Affero General Public License in
# <https://www.github.com/TeamUltroid/Ultroid/blob/main/LICENSE/>.

"""
✘ Commands Available -

• `{i}lexica <query> ; limit`
    search AI generated images.
   .
"""

import os
from secrets import token_hex

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
    files = [(await fast_download(a, token_hex(6) + ".png"))[0]
             for a in list(map(lambda d: d["src"], cont["images"][:limit]))]
    await event.reply(
        file=files
    )
    for file in files:
        os.remove(file)
    await event.try_delete()
