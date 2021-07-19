# Ultroid - UserBot
# Copyright (C) 2021 TeamUltroid
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

ULTPIC = "resources/extras/inline.jpg"
CL = udB.get("INLINE_PIC")
if CL:
    ULTPIC = CL


@ultroid_cmd(pattern="update$")
async def _(e):
    xx = await eor(e, "`Checking for updates...`")
    m = await updater()
    branch = (Repo.init()).active_branch
    if m:
        x = await asst.send_file(
            int(udB.get("LOG_CHANNEL")),
            ULTPIC,
            caption="• **Update Available** •",
            force_document=False,
            buttons=Button.inline("Changelogs", data="changes"),
        )
        if not e.client._bot:
            Link = (await e.client(GetLink(x.chat_id, x.id))).link
        else:
            Link = f"https://t.me/c/{x.chat.id}/{x.id}"
        await xx.edit(
            f'<strong><a href="{Link}">[ChangeLogs]</a></strong>',
            parse_mode="html",
            link_preview=False,
        )
    else:
        await xx.edit(
            f'<code>Your BOT is </code><strong>up-to-date</strong><code> with </code><strong><a href="https://github.com/TeamUltroid/Ultroid/tree/{branch}">[{branch}]</a></strong>',
            parse_mode="html",
            link_preview=False,
        )


@callback("updtavail")
@owner
async def updava(event):
    await event.delete()
    await asst.send_file(
        int(udB.get("LOG_CHANNEL")),
        ULTPIC,
        caption="• **Update Available** •",
        force_document=False,
        buttons=Button.inline("Changelogs", data="changes"),
    )
