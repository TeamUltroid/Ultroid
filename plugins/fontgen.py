# Ultroid - UserBot
# Copyright (C) 2021 TeamUltroid
#
# This file is a part of < https://github.com/TeamUltroid/Ultroid/ >
# PLease read the GNU Affero General Public License in
# <https://www.github.com/TeamUltroid/Ultroid/blob/main/LICENSE/>.

"""
• `{i}font <font name> : <text>`
    Generate different fonts for the text.

• `{i}font`
    To get list of fonts
"""

from resources.extras.fonts import (
    _default,
    _double_stroke,
    _monospace,
    _script_royal,
    _small_caps,
)

fonts = ["small caps ", "monospace ", "double stroke ", "script royal "]


@ultroid_cmd(
    pattern="font ?(.*)",
)
async def _(e):
    input = e.pattern_match.group(1)
    reply = await e.get_reply_message()
    if not input:
        m = "**Available Fonts**\n\n"
        for x in fonts:
            m += f"• `{x}`\n"
        return await eor(e, m, time=5)
    try:
        font = input.split(":", maxsplit=1)[0]
    except IndexError:
        return await eor(e, "`fonts small caps : Your Message`", time=5)
    if reply:
        text = reply.message
    else:
        try:
            text = input.split(":", maxsplit=1)[1]
        except IndexError:
            return await eor(e, "`fonts small caps : Your Message`", time=5)
    if font not in fonts:
        return await eor(e, f"`{font} not in font list`.", time=5)
    if font == "small caps ":
        msg = gen_font(text, _small_caps)
    elif font == "monospace ":
        msg = gen_font(text, _monospace)
    elif font == "double stroke ":
        msg = gen_font(text, _double_stroke)
    elif font == "script royal ":
        msg = gen_font(text, _script_royal)
    await eor(e, msg)


def gen_font(text, new_font):
    for q in text:
        if q in _default:
            new = new_font[_default.index(q)]
            text = text.replace(q, new)
    return text
