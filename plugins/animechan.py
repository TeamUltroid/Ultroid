# Ultroid - UserBot
#
# This file is a part of < https://github.com/TeamUltroid/UltroidAddons/>

"""
Fetch Random anime quotes

Command : `{i}aniquote`
"""

from . import ultroid_cmd, async_searcher


@ultroid_cmd(pattern="aniquote")
async def _(ult):
    u = await ult.eor("...")
    try:
        resp = await async_searcher(
            "https://animechan.vercel.app/api/random", re_json=True
        )
        results = f"**{resp['quote']}**\n"
        results += f" — __{resp['character']} ({resp['anime']})__"
        return await u.edit(results)
    except Exception:
        await u.edit("`Something went wrong LOL ...`")
