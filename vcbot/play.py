import datetime

from . import *


@vc_asst("play")
async def play_music_(event):

    # TODO - file, cplay, radio

    xx = await eor(event, "`Processing...`")

    args = event.text.split(" ", 1)
    chat = event.chat_id

    done = await vc_joiner(event, event.chat_id)
    if not done:
        return

    try:
        song = args[1]
    except IndexError:
        return await eod(xx, "Please specify a song name !", time=10)
    await eor(xx, "`Downloading and converting...`")
    TS = datetime.datetime.now().strftime("%H:%M:%S")
    song, thumb, song_name, duration = await download(event, song, chat, TS)

    await xx.reply(
        "Now playing **{}**\nDuration: **{}**".format(
            song_name, time_formatter(duration * 1000)
        ),
        file=thumb,
    )

    ultSongs.group_call.input_filename = song
    await xx.delete()
