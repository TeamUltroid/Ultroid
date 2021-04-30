# Ultroid - UserBot
# Copyright (C) 2020 TeamUltroid
#
# This file is a part of < https://github.com/TeamUltroid/Ultroid/ >
# PLease read the GNU Affero General Public License in
# <https://www.github.com/TeamUltroid/Ultroid/blob/main/LICENSE/>.
"""
✘ Commands Available -
• `{i}update`
    See changelogs if any update is available.
"""

from . import *


@ultroid_cmd(pattern="update$")
async def _(e):
    x = await updater()
    if x is not None:
        await eor(
            e,
            f'<strong><a href="t.me/c/{x.peer_id.channel_id}/{x.id}">[ChangeLogs]</a></strong>',
            parse_mode="html",
            link_preview=False,
        )
    else:
        await eor(
            e,
            '<code>Your BOT is </code><strong>up-to-date</strong> with <strong><a href="https://github.com/TeamUltroid/Ultroid/tree/dev">[Dev]</a></strong>',
            parse_mode="html",
            link_preview=False,
        )


HELP.update({f"{__name__.split('.')[1]}": f"{__doc__.format(i=HNDLR)}"})
