# Ultroid - UserBot
# Copyright (C) 2021-2022 TeamUltroid
#
# This file is a part of < https://github.com/TeamUltroid/Ultroid/ >
# PLease read the GNU Affero General Public License in
# <https://www.github.com/TeamUltroid/Ultroid/blob/main/LICENSE/>.

"""
✘ Commands Available -

`{i}ytplaylist <playlist link>`
  play whole playlist in voice chat

"""

import re
from . import vc_asst, get_string, inline_mention, Player, dl_playlist, add_to_queue, is_url_ok, VC_QUEUE


@vc_asst("ytplaylist")
async def live_stream(e):
    xx = await e.eor(get_string("com_1"))
    if len(e.text.split()) <= 1:
        return await xx.eor("Are You Kidding Me?\nWhat to Play?")
    input = e.text.split()
    if input[1].startswith("-"):
        chat = int(input[1])
        song = e.text.split(maxsplit=2)[2]
    elif input[1].startswith("@"):
        cid_moosa = (await e.client.get_entity(input[1])).id
        chat = int("-100" + str(cid_moosa))
        song = e.text.split(maxsplit=2)[2]
    else:
        song = e.text.split(maxsplit=1)[1]
        chat = e.chat_id
    if not (re.search("youtu", song) and re.search("playlist\\?list", song)):
        return await xx.eor(get_string("vcbot_8"))
    if not is_url_ok(song):
        return await xx.eor("`Only Youtube Playlist please.`")
    await xx.edit(get_string("vcbot_7"))
    file, thumb, title, link, duration = await dl_playlist(
        chat, inline_mention(e), song
    )
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
        from_user = inline_mention(e)
        add_to_queue(chat, file, title, link, thumb, from_user, duration)
        return await xx.eor(
            f"▶ Added 🎵 **[{title}]({link})** to queue at #{list(VC_QUEUE[chat].keys())[-1]}.",
        )
