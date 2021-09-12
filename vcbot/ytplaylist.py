# Ultroid - UserBot
# Copyright (C) 2021 TeamUltroid
#
# This file is a part of < https://github.com/TeamUltroid/Ultroid/ >
# PLease read the GNU Affero General Public License in
# <https://www.github.com/TeamUltroid/Ultroid/blob/main/LICENSE/>.

"""
✘ Commands Available -

`{i}ytplaylist <playlist link>`
  play whole playlist in voice chat

"""

import requests

from . import *


@vc_asst("ytplaylist")
async def live_stream(e):
    xx = await eor(e, get_string("com_1"))
    if not len(e.text.split()) > 1:
        return await eor(xx, "Are You Kidding Me?\nWhat to Play?")
    input = e.text.split()
    if input[1].startswith("-"):
        chat = int(input[1])
        song = e.text.split(maxsplit=2)[2]
    elif input[1].startswith("@"):
        cid_moosa = (await vcClient.get_entity(input[1])).id
        chat = int("-100" + str(cid_moosa))
        song = e.text.split(maxsplit=2)[2]
    else:
        song = e.text.split(maxsplit=1)[1]
        chat = e.chat_id
    if not (re.search("youtu", song) and re.search("playlist\\?list", song)):
        return await eor(xx, "Give only youtube playlist")
    try:
        requests.get(song)
    except BaseException:
        return await eor(xx, f"`Only Youtube Playlist please.`")
    await xx.edit("`Keep patience... It'll take some time.`")
    file, thumb, title, link, duration = await dl_playlist(chat, from_user, song)
    ultSongs = Player(chat, e)
    if not ultSongs.group_call.is_connected:
        if not (await ultSongs.vc_joiner()):
            return
        from_user = inline_mention(e.sender)
        await xx.reply(
            "🎸 **Now playing:** [{}]({})\n⏰ **Duration:** `{}`\n👥 **Chat:** `{}`\n🙋‍♂ **Requested by:** {}".format(
                title[:30] + "...", link, duration, chat, from_user
            ),
            file=thumb,
            link_preview=False,
        )
        await xx.delete()
        await ultSongs.group_call.start_audio(file)
    else:
        from_user = html_mention(e.sender)
        add_to_queue(chat, file, title, link, thumb, from_user, duration)
        return await eor(
            xx,
            f"▶ Added 🎵 **[{title}]({link})** to queue at #{list(VC_QUEUE[chat].keys())[-1]}.",
        )
