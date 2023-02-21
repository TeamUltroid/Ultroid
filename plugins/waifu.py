# Ported Plugin

"""
✘ Commands Available -

• `{i}waifu <text>`
    paste text on random stickers.
"""

import re

from . import *

EMOJI_PATTERN = re.compile(
    "["
    "\U0001F1E0-\U0001F1FF"  # flags (iOS)
    "\U0001F300-\U0001F5FF"  # symbols & pictographs
    "\U0001F600-\U0001F64F"  # emoticons
    "\U0001F680-\U0001F6FF"  # transport & map symbols
    "\U0001F700-\U0001F77F"  # alchemical symbols
    "\U0001F780-\U0001F7FF"  # Geometric Shapes Extended
    "\U0001F800-\U0001F8FF"  # Supplemental Arrows-C
    "\U0001F900-\U0001F9FF"  # Supplemental Symbols and Pictographs
    "\U0001FA00-\U0001FA6F"  # Chess Symbols
    "\U0001FA70-\U0001FAFF"  # Symbols and Pictographs Extended-A
    "\U00002702-\U000027B0"  # Dingbats
    "]+",
)


def deEmojify(inputString: str) -> str:
    """Remove emojis and other non-safe characters from string"""
    return re.sub(EMOJI_PATTERN, "", inputString)


@ultroid_cmd(
    pattern="waifu ?(.*)",
)
async def waifu(animu):
    xx = await eor(animu, get_string("com_1"))
    # """Creates random anime sticker!"""
    text = animu.pattern_match.group(1)
    if not text:
        if animu.is_reply:
            text = (await animu.get_reply_message()).message
        else:
            await xx.edit(get_string("sts_1"))
            return
    waifus = [32, 33, 37, 40, 41, 42, 58, 20]
    finalcall = "#" + (str(random.choice(waifus)))
    sticcers = await animu.client.inline_query(
        "stickerizerbot",
        f"{finalcall}{(deEmojify(text))}",
    )
    await sticcers[0].click(
        animu.chat_id,
        reply_to=animu.reply_to_msg_id,
        silent=bool(animu.is_reply),
        hide_via=True,
    )
    await xx.delete()
