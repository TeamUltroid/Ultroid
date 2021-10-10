# Ultroid - UserBot
# Copyright (C) 2021 TeamUltroid
#
# This file is a part of < https://github.com/TeamUltroid/Ultroid/ >
# PLease read the GNU Affero General Public License in
# <https://www.github.com/TeamUltroid/Ultroid/blob/main/LICENSE/>.

"""
✘ Commands Available -

• `{i}play <song name/song url/reply to file>`
   Play the song in voice chat, or add the song to queue.

• `{i}playfrom <channel username> ; <limit>`
   Play music from channel files at current chat..

• `{i}radio <link>`
   Stream Live Radio m3u8 links.

• `{i}ytlive <link>`
   Stream Live YouTube
"""


from . import *
from telethon.errors.rpcerrorlist import ChatSendMediaForbiddenError


@vc_asst("play")
async def play_music_(event):
    if "playfrom" in event.text.split()[0]:
        return  # For PlayFrom Conflict
    xx = await eor(event, get_string("com_1"), parse_mode="md")
    chat = event.chat_id
    from_user = html_mention(event)
    reply, song = None, None
    if event.reply_to:
        reply = await event.get_reply_message()
    if len(event.text.split()) > 1:
        input = event.text.split(maxsplit=1)[1]
        tiny_input = input.split()[0]
        if tiny_input.startswith("@"):
            try:
                chat = int("-100" + str(await get_user_id(tiny_input, client=vcClient)))
                song = input.split(maxsplit=1)[1]
            except IndexError:
                pass
            except Exception as e:
                return await eor(event, str(e))
        elif tiny_input.startswith("-"):
            chat = int(
                "-100" + str(await get_user_id(int(tiny_input), client=vcClient))
            )
            try:
                song = input.split(maxsplit=1)[1]
            except BaseException:
                pass
        else:
            song = input
    if not (reply or song):
        return await eor(
            xx, "Please specify a song name or reply to a audio file !", time=5
        )
    await eor(xx, get_string('vcbot_20'), parse_mode="md")
    if reply and reply.media and mediainfo(reply.media).startswith(("audio", "video")):
        song, thumb, song_name, link, duration = await file_download(xx, reply)
    else:
        song, thumb, song_name, link, duration = await download(song)
    ultSongs = Player(chat, event)
    song_name = song_name[:30] + "..."
    if not ultSongs.group_call.is_connected:
        if not (await ultSongs.vc_joiner()):
            return
        await ultSongs.group_call.start_audio(song)
        text = "🎸 <strong>Now playing: <a href={}>{}</a>\n⏰ Duration:</strong> <code>{}</code>\n👥 <strong>Chat:</strong> <code>{}</code>\n🙋‍♂ <strong>Requested by: {}</strong>".format(
                link, song_name, duration, chat, from_user
        )
        try:
            await xx.reply(
            text,
            file=thumb,
            link_preview=False,
            parse_mode="html",
            )
            await xx.delete()
        except ChatSendMediaForbiddenError:
            await eor(xx, text, link_preview=False)
        if thumb and os.path.exists(thumb):
            os.remove(thumb)
    else:
        if not (
            reply
            and reply.media
            and mediainfo(reply.media).startswith(("audio", "video"))
        ):
            song = None
        add_to_queue(chat, song, song_name, link, thumb, from_user, duration)
        return await eor(
            xx,
            f"▶ Added 🎵 <a href={link}>{song_name}</a> to queue at #{list(VC_QUEUE[chat].keys())[-1]}.",
            parse_mode="html",
        )


@vc_asst("playfrom")
async def play_music_(event):
    msg = await eor(event, get_string("com_1"))
    chat = event.chat_id
    limit = 10
    from_user = html_mention(event)
    if len(event.text.split()) <= 1:
        return await msg.edit(
            "Use in Proper Format\n`.playfrom <channel username> ; <limit>`"
        )
    input = event.text.split(maxsplit=1)[1]
    if ";" in input:
        try:
            limit = input.split(";")
            input = limit[0].strip()
            if input.startswith("-") or input.isdigit():
                input = int(input)
            limit = int(limit[1].strip()) if limit[1].strip().isdigit() else 10
            input = await get_user_id(input)
        except (IndexError, ValueError):
            pass
    try:
        fromchat = (await event.client.get_entity(input)).id
    except Exception as er:
        return await eor(msg, str(er))
    await eor(msg, "`• Started Playing from Channel....`")
    send_message = True
    ultSongs = Player(chat, event)
    count = 0
    async for song in event.client.iter_messages(
        fromchat, limit=limit, wait_time=5, filter=types.InputMessagesFilterMusic
    ):
        count += 1
        song, thumb, song_name, link, duration = await file_download(
            msg, song, fast_download=False
        )
        song_name = song_name[:30] + "..."
        if not ultSongs.group_call.is_connected:
            if not (await ultSongs.vc_joiner()):
                return
            await ultSongs.group_call.start_audio(song)
            text = "🎸 <strong>Now playing: <a href={}>{}</a>\n⏰ Duration:</strong> <code>{}</code>\n👥 <strong>Chat:</strong> <code>{}</code>\n🙋‍♂ <strong>Requested by: {}</strong>".format(
                    link, song_name, duration, chat, from_user
            )
            try:
                await msg.reply(
                text,
                file=thumb,
                link_preview=False,
                parse_mode="html",
                )
            except ChatSendMediaForbiddenError:
                await msg.reply(text, link_preview=False,
                    parse_mode="html")
            if thumb and os.path.exists(thumb):
                os.remove(thumb)
        else:
            add_to_queue(chat, song, song_name, link, thumb, from_user, duration)
            if send_message and count == 1:
                await eor(
                    msg,
                    f"▶ Added 🎵 <strong><a href={link}>{song_name}</a></strong> to queue at <strong>#{list(VC_QUEUE[chat].keys())[-1]}.</strong>",
                    parse_mode="html",
                )
                send_message = False


@vc_asst("radio")
async def radio_mirchi(e):
    xx = await eor(e, get_string("com_1"))
    if len(e.text.split()) <= 1:
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
    if not ultSongs.group_call.is_connected and not (
        await ultSongs.vc_joiner()
    ):
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
    if not ultSongs.group_call.is_connected and not (
        await ultSongs.vc_joiner()
    ):
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
