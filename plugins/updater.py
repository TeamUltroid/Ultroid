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

from git import Repo
from telethon.tl.functions.channels import ExportMessageLinkRequest as GetLink

from . import *


@ultroid_cmd(pattern="update$")
async def _(e):
    m = await updater()
    branch = (Repo.init()).active_branch
    if m:
        x = await ultroid_bot.asst.send_file(
            int(udB.get("LOG_CHANNEL")),
            "resources/extras/ultroid.jpg",
            caption="**Update Available**",
            force_document=True,
            buttons=Button.inline("Changelogs", data="changes"),
        )
        Link = (await ultroid_bot(GetLink(x.peer_id.channel_id, x.id))).link
        await eor(
            e,
            f'<strong><a href="{Link}">[ChangeLogs]</a></strong>',
            parse_mode="html",
            link_preview=False,
        )
    else:
        await eor(
            e,
            f'<code>Your BOT is </code><strong>up-to-date</strong><code> with </code><strong><a href="https://github.com/TeamUltroid/Ultroid/tree/{branch}">[{branch}]</a></strong>',
            parse_mode="html",
            link_preview=False,
        )


@callback("updtavail")
@owner
async def updava(event):
    await event.delete()
    await ultroid_bot.asst.send_file(
        int(udB.get("LOG_CHANNEL")),
        "resources/extras/inline.jpg",
        caption="**Update Available**\n👇👇👇👇👇👇",
        force_document=False,
        buttons=Button.inline("Changelogs", data="changes"),
    )


HELP.update({f"{__name__.split('.')[1]}": f"{__doc__.format(i=HNDLR)}"})
