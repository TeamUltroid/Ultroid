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
"""


from . import *


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
    await eor(xx, "`Downloading and converting...`", parse_mode="md")
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
        await xx.reply(
            "🎸 <strong>Now playing: <a href={}>{}</a>\n⏰ Duration:</strong> <code>{}</code>\n👥 <strong>Chat:</strong> <code>{}</code>\n🙋‍♂ <strong>Requested by: {}</strong>".format(
                link, song_name, duration, chat, from_user
            ),
            file=thumb,
            link_preview=False,
            parse_mode="html",
        )
        await xx.delete()
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
    if not len(event.text.split()) > 1:
        return await msg.edit(
            "Use in Proper Format\n`.playfrom <channel username> ; <limit>`"
        )
    input = event.text.split(maxsplit=1)[1]
    if ";" in input:
        try:
            limit = input.split(";")
            input = limit[0]
            limit = int(limit[1])
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
            await msg.reply(
                "🎸 <strong>Now playing: <a href={}>{}</a>\n⏰ Duration:</strong> <code>{}</code>\n👥 <strong>Chat:</strong> <code>{}</code>\n🙋‍♂ <strong>Requested by: {}</strong>".format(
                    link, song_name, duration, chat, from_user
                ),
                file=thumb,
                link_preview=False,
                parse_mode="html",
            )
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
