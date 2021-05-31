"""
{i}
"""

from . import _double_stroke, _monospace, _small_caps, _default

fonts = ["small caps ", "monospace ", "double stroke "]


@ultroid_cmd(
    pattern="font ?(.*)",
)
async def _(e):
    input = e.pattern_match.group(1)
    try:
        font = input.split(":", maxsplit=1)[0]
        text = input.split(":", maxsplit=1)[1]
    except BaseException:
        pass  # todo
    if font not in fonts:
        return  # todo
    if font == "small caps ":
        msg = gen_font(text, _small_caps)
    if font == "monospace ":
        msg = gen_font(text, _monospace)
    if font == "double stroke ":
        msg = gen_font(text, _double_stroke)
    await eor(e, msg)
    # todo tmrw


def gen_font(text, new_font):
    for q in text:
        if q in _default:
            new = new_font[_default.index(q)]
            msg = text.replace(q, new)
    return msg
