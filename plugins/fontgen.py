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


from . import HNDLR, eod, eor, ultroid_cmd

fonts = ["small caps", "monospace", "double stroke", "script royal"]
_default = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"
_small_caps = "ᴀʙᴄᴅᴇғɢʜɪᴊᴋʟᴍɴᴏᴘϙʀsᴛᴜᴠᴡxʏᴢABCDEFGHIJKLMNOPQRSTUVWXYZ"
_monospace = "𝚊𝚋𝚌𝚍𝚎𝚏𝚐𝚑𝚒𝚓𝚔𝚕𝚖𝚗𝚘𝚙𝚚𝚛𝚜𝚝𝚞𝚟𝚠𝚡𝚢𝚣𝙰𝙱𝙲𝙳𝙴𝙵𝙶𝙷𝙸𝙹𝙺𝙻𝙼𝙽𝙾𝙿𝚀𝚁𝚂𝚃𝚄𝚅𝚆𝚇𝚈𝚉"
_double_stroke = "𝕒𝕓𝕔𝕕𝕖𝕗𝕘𝕙𝕚𝕛𝕜𝕝𝕞𝕟𝕠𝕡𝕢𝕣𝕤𝕥𝕦𝕧𝕨𝕩𝕪𝕫𝔸𝔹ℂ𝔻𝔼𝔽𝔾ℍ𝕀𝕁𝕂𝕃𝕄ℕ𝕆ℙℚℝ𝕊𝕋𝕌𝕍𝕎𝕏𝕐ℤ"
_script_royal = "𝒶𝒷𝒸𝒹𝑒𝒻𝑔𝒽𝒾𝒿𝓀𝓁𝓂𝓃𝑜𝓅𝓆𝓇𝓈𝓉𝓊𝓋𝓌𝓍𝓎𝓏𝒜ℬ𝒞𝒟ℰℱ𝒢ℋℐ𝒥𝒦ℒℳ𝒩𝒪𝒫𝒬ℛ𝒮𝒯𝒰𝒱𝒲𝒳𝒴𝒵"


@ultroid_cmd(
    pattern="font ?(.*)",
)
async def _(e):
    input = e.pattern_match.group(1)
    reply = await e.get_reply_message()
    help = __doc__.format(i=HNDLR)
    if not input:
        m = "**Available Fonts**\n\n"
        for x in fonts:
            m += f"• `{x}`\n"
        return await eor(e, m, time=5)
    if not input and not reply:
        return await eor(e, help)
    if input and not reply:
        try:
            _ = input.split(":", maxsplit=1)
            font = _[0][:-1]
            text = _[1]
        except IndexError:
            return await eod(e, help)
    elif reply and not input:
        return await eod(e, "`Give font dude :/`")
    else:
        font = input
        text = reply.message
    if font not in fonts:
        return await eor(e, f"`{font} not in font list`.", time=5)
    if font == "small caps":
        msg = gen_font(text, _small_caps)
    elif font == "monospace":
        msg = gen_font(text, _monospace)
    elif font == "double stroke":
        msg = gen_font(text, _double_stroke)
    elif font == "script royal":
        msg = gen_font(text, _script_royal)
    await eor(e, msg)


def gen_font(text, new_font):
    new_font = " ".join(new_font).split()
    for q in text:
        if q in _default:
            new = new_font[_default.index(q)]
            text = text.replace(q, new)
    return text
