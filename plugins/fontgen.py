"""
{i}
"""

from . import _double_stroke, _monospace, _small_caps

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
        font = _small_caps
    if font == "monospace ":
        font = _monospace
    if font == "double stroke ":
        font = _double_stroke
    await eor(e, str(font))
    # todo tmrw
