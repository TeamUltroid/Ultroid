# Ultroid Userbot
#
# This file is a part of < https://github.com/TeamUltroid/Ultroid/ >
# PLease read the GNU Affero General Public License in
# <https://www.github.com/TeamUltroid/Ultroid/blob/main/LICENSE/>.

"""

✘ Commands Available -

• `{i}wiki <search query>``
    Wikipedia search from telegram.

"""

import wikipedia

from . import *


@ultroid_cmd(pattern="wiki ?(.*)")
async def wiki(e):
    srch = e.pattern_match.group(1)
    if not srch:
        return await e.eor("`Give some text to search on wikipedia !`")
    msg = await e.eor(f"`Searching {srch} on wikipedia..`")
    try:
        mk = wikipedia.summary(srch)
        te = f"**Search Query :** {srch}\n\n**Results :** {mk}"
        await msg.edit(te)
    except Exception as err:
        await msg.edit(f"**ERROR** : {str(err)}")
