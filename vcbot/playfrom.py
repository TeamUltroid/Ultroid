# Ultroid - UserBot
# Copyright (C) 2021 TeamUltroid
#
# This file is a part of < https://github.com/TeamUltroid/Ultroid/ >
# PLease read the GNU Affero General Public License in
# <https://www.github.com/TeamUltroid/Ultroid/blob/main/LICENSE/>.

from . import *


@asst.on_message(
    filters.command(["playfrom", f"playfrom@{vcusername}"])
    & filters.user(VC_AUTHS())
    & ~filters.edited
)
async def PlayFrom(client, message):
    chat = message.text
    spl = chat.split(" ", maxsplit=1)
    limit = 100
    PlayAT = message.chat
    CHN_PLAY = udB.get("CHN_PLAY")
    if CHN_PLAY:
        PlayAT = await Client.get_chat(CHN_PLAY)
    if ";" in chat:
        lct = spl[1].split(";", maxsplit=1)
        limit = int(lct[-1])
        spl = [None, lct[0]]

    if len(spl) == 2:
        try:
            playfrom = await Client.get_chat(chat_id=spl[1])
        except Exception as Ex:
            return await eor(message, str(Ex))
    else:
        return await eor(
            message, "Provide the Chat Username/Id from where to Play Songs..."
        )
    ALL = []
    M = await asst.send_message(
        LOG_CHANNEL, f"Started Chat Song Play at {PlayAT.title} [`{PlayAT.id}`]"
    )
    async for mi in Client.search_messages(playfrom.id, limit=limit, filter="audio"):
        ALL.append(mi)
    TTl = len(ALL)
    Sleep = False
    for i in range(TTl):
        music = ALL[i]
        durat = music.audio.duration
        sleepy = durat + 20
        dl = await music.download()
        TS = dt.now().strftime("%H:%M:%S")
        song = f"VCSONG_{PlayAT.id}_{TS}.raw"
        await bash(
            f'ffmpeg -i "{dl}" -f s16le -ac 1 -acodec pcm_s16le -ar 48000 {song} -y'
        )
        os.remove(dl)
        if PlayAT.id in CallsClient.active_calls.keys():
            add_to_queue(
                PlayAT.id, song, music.audio.title, message.from_user.mention, sleepy
            )
        else:
            try:
                CallsClient.join_group_call(PlayAT.id, song)
                mn = await message.reply_text(
                    f"✤ **Playing** : {music.audio.title}\n✤ **Song No** : {i+1}/{TTl}\n✤ **Duration :** {time_formatter(durat*1000)}\n**✤ At** : `{PlayAT.title}`",
                    quote=False,
                )
                Durat = durat
                Song = song

                Sleep = True
            except Exception as er:
                await mn.edit(str(er))
                continue
    if Sleep:
        await asyncio.sleep(Durat)
        os.remove(Song)
        await mn.delete()
    await M.delete()


@Client.on_message(filters.me & filters.command("playfrom") & ~filters.edited)
async def pleya(_, message):
    await PlayFrom(_, message)
