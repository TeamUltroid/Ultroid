# Ultroid - UserBot
# Copyright (C) 2021 TeamUltroid
#
# This file is a part of < https://github.com/TeamUltroid/Ultroid/ >
# PLease read the GNU Affero General Public License in
# <https://www.github.com/TeamUltroid/Ultroid/blob/main/LICENSE/>.

"""
✘ Commands Available -

• `{i}radio <link>`
   Stream Live Radio m3u8 links.

• `{i}ytlive <link>`
   Stream Live YouTube.
"""


from . import *


@vc_asst("radio")
async def radio_mirchi(e):
    xx = await eor(e, get_string("com_1"))
    if not len(e.text.split()) > 1:
        return await eor(xx, "Are You Kidding Me?\nWhat to Play?")
    input = e.text.split()
    if input[1].startswith("-"):
        chat = int(input[1])
        song = e.text.split(maxsplit=2)[2]
    elif input[1].startswith("@"):
        cid = (await vcClient.get_entity(input[1])).id
        chat = int(f"-100{cid}")
        song = e.text.split(maxsplit=2)[2]
    else:
        song = e.text.split(maxsplit=1)[1]
        chat = e.chat_id
    if not is_url_ok(song):
        return await eor(xx, f"`{song}`\n\nNot a playable link.🥱")
    ultSongs = Player(chat, e)
    if not ultSongs.group_call.is_connected:
        if not (await ultSongs.vc_joiner()):
            return
    await ultSongs.group_call.start_audio(song)
    await xx.reply(
        f"• Started Radio 📻\n\n• Station : `{song}`",
        file="https://telegra.ph/file/d09d4461199bdc7786b01.mp4",
    )
    await xx.delete()


@vc_asst("(live|ytlive)")
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
    if not is_url_ok(song):
        return await eor(xx, f"`{song}`\n\nNot a playable link.🥱")
    is_live_vid = False
    if re.search("youtu", song):
        is_live_vid = (await bash(f'youtube-dl -j "{song}" | jq ".is_live"'))[0]
    if is_live_vid != "true":
        return await eor(xx, f"Only Live Youtube Urls supported!\n{song}")
    file, thumb, title, link, duration = await download(song)
    ultSongs = Player(chat, e)
    if not ultSongs.group_call.is_connected:
        if not (await ultSongs.vc_joiner()):
            return
    from_user = inline_mention(e.sender)
    await xx.reply(
        "🎸 **Now playing:** [{}]({})\n⏰ **Duration:** `{}`\n👥 **Chat:** `{}`\n🙋‍♂ **Requested by:** {}".format(
            title, link, duration, chat, from_user
        ),
        file=thumb,
        link_preview=False,
    )
    await xx.delete()
    await ultSongs.group_call.start_audio(file)
