# Ultroid - UserBot
#
# This file is a part of < https://github.com/TeamUltroid/UltroidAddons/ >
# PLease read the GNU Affero General Public License in
# <https://www.github.com/TeamUltroid/Ultroid/blob/main/LICENSE/>.

"""
✘ Commands Available -

• `{i}mencode <text>`
   Encode the given text to Morse Code.

• `{i}mdecode <text>`
   Decode the given text from Morse Code.
"""

from . import async_searcher, ultroid_cmd


@ultroid_cmd(pattern="mencode ?(.*)")
async def mencode(event):
    msg = await event.eor(get_string("com_1"))
    text = event.pattern_match.group(1)
    if not text:
        return msg.edit("Please give a text!")
    base_url = "https://apis.xditya.me/morse/encode?text=" + text
    encoded = await async_searcher(base_url, re_content=False)
    await msg.edit("**Encoded.**\n\n**Morse Code:** `{}`".format(encoded))


@ultroid_cmd(pattern="mdecode ?(.*)")
async def mencode(event):
    msg = await event.eor(get_string("com_1"))
    text = event.pattern_match.group(1)
    if not text:
        return await msg.edit("Please give a text!")
    base_url = "https://apis.xditya.me/morse/decode?text=" + text
    encoded = await async_searcher(base_url, re_content=False)
    await msg.edit("**Decoded.**\n\n**Message:** `{}`".format(encoded))
